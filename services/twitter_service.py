import tweepy
import time
import logging
import random
from config.settings import (
    X_API_BEARER,
    X_API_KEY,
    X_API_KEY_SECRET,
    X_API_KEY_CONSUMER,
    X_API_KEY_SECRET_CONSUMER
)

logger = logging.getLogger("crypto_bot.twitter")

class TwitterService:
    def __init__(self, openai_service, db, max_results=10, respond=False):
        """
        Inicializa el servicio de Twitter.
        
        Args:
            openai_service: Servicio para generar respuestas con OpenAI
            db: Servicio de base de datos
            max_results: Número máximo de tweets a procesar por consulta (mínimo 10 requerido por la API)
            respond: Si es True, responderá a los tweets. Si es False, solo simulará
        """
        self.openai_service = openai_service
        self.db = db
        self.max_results = max_results  # Mínimo 10 requerido por la API
        self.respond = respond
        
        # Cliente solo para lectura (búsqueda)
        self.read_client = tweepy.Client(
            bearer_token=X_API_BEARER,
            wait_on_rate_limit=False  # Cambiado a False para manejar manualmente
        )
        
        # Cliente para lectura y escritura (responder)
        if self.respond:
            self.write_client = tweepy.Client(
                consumer_key=X_API_KEY_CONSUMER,
                consumer_secret=X_API_KEY_SECRET_CONSUMER,
                access_token=X_API_KEY,
                access_token_secret=X_API_KEY_SECRET,
                wait_on_rate_limit=False  # Cambiado a False para manejar manualmente
            )
    
    def process_tweets(self):
        """Busca tweets recientes y genera/envía respuestas"""
        try:
            logger.info("🔍 Buscando tweets recientes sobre criptomonedas...")
            
            # Usamos una consulta más restrictiva para reducir el volumen
            query = "crypto -is:retweet lang:en"
            
            try:
                tweets = self.read_client.search_recent_tweets(
                    query=query, 
                    max_results=10,  # Twitter requiere mínimo 10
                    tweet_fields=["author_id", "created_at"]  # Menos campos
                )
            except tweepy.errors.TooManyRequests:
                logger.warning("⚠️ Rate limit alcanzado durante la búsqueda. Intentando usar datos de demostración.")
                # En lugar de fallar, usamos algunos datos de demostración
                tweets = self._generate_demo_tweets()
            except Exception as e:
                logger.error(f"❌ Error al buscar tweets: {e}")
                return
            
            if not tweets or not tweets.data:
                logger.info("⚠️ No se encontraron tweets recientes.")
                return
                
            logger.info(f"✅ Encontrados {len(tweets.data)} tweets para procesar.")
            
            # Procesar solo una muestra de los tweets (máximo 5)
            # para evitar rate limits pero cumpliendo con los requisitos de la API
            sample_size = min(5, len(tweets.data))
            sample_tweets = random.sample(list(tweets.data), sample_size)
            
            logger.info(f"🔄 Procesando muestra de {sample_size} tweets para evitar rate limits")
            
            # Procesar cada tweet con pausa para evitar rate limits
            for i, tweet in enumerate(sample_tweets):
                logger.info(f"Procesando tweet {i+1}/{sample_size}")
                
                # Añadir retrasos aleatorios entre procesos
                time.sleep(random.uniform(2, 5))
                
                # Intentar procesar el tweet con manejo de rate limits
                try:
                    self._process_single_tweet(tweet)
                except tweepy.errors.TooManyRequests:
                    # Si hay un rate limit, guardamos el tweet sin información de usuario
                    logger.warning(f"⚠️ Rate limit alcanzado al procesar el tweet {tweet.id}. Guardando con información mínima.")
                    self._process_minimal_tweet(tweet)
                except Exception as e:
                    logger.error(f"❌ Error al procesar tweet {tweet.id}: {e}")
                    continue
                
            logger.info("✅ Procesamiento de tweets completado.")
                
        except Exception as e:
            logger.error(f"❌ Error al procesar tweets: {e}")
    
    def _generate_demo_tweets(self):
        """Genera datos de demostración cuando hay rate limits"""
        # Crear un objeto similar al que devuelve Tweepy pero con datos ficticios
        class DemoTweet:
            def __init__(self, id, text, author_id):
                self.id = id
                self.text = text
                self.author_id = author_id
        
        class DemoResponse:
            def __init__(self):
                self.data = [
                    DemoTweet(1, "Bitcoin looking strong today! #crypto", "user1"),
                    DemoTweet(2, "What's your favorite altcoin? #crypto", "user2"),
                    DemoTweet(3, "DeFi projects are the future of finance. #crypto", "user3")
                ]
        
        logger.info("🔄 Usando datos de demostración debido a rate limits.")
        return DemoResponse()
    
    def _process_minimal_tweet(self, tweet):
        """Procesa un tweet con información mínima cuando hay rate limits"""
        try:
            # Verificar si ya procesamos este tweet
            if self.db.is_tweet_processed(tweet.id):
                return
                
            username = "desconocido_ratelimit"
            
            # Generar respuesta con OpenAI (esto no afecta los rate limits de Twitter)
            response = self.openai_service.generate_response(tweet.text)
            
            logger.info(f"📝 Respuesta generada para tweet {tweet.id}: {response}")
            
            # Guardar sin responder
            self.db.mark_tweet_processed(
                tweet_id=tweet.id, 
                responded=False,
                tweet_text=tweet.text,
                response_text=response,
                author_username=username
            )
                
        except Exception as e:
            logger.error(f"❌ Error al procesar tweet mínimo {tweet.id}: {e}")
    
    def _process_single_tweet(self, tweet):
        """Procesa un tweet individual"""
        try:
            # Verificar si ya procesamos este tweet
            if self.db.is_tweet_processed(tweet.id):
                logger.debug(f"⏭️ Tweet {tweet.id} ya procesado anteriormente.")
                return
            
            # Intentar obtener información del usuario
            try:
                user = self.read_client.get_user(id=tweet.author_id, user_fields=["username"])
                username = user.data.username
            except:
                # Si falla, usamos un valor genérico
                username = f"usuario_{tweet.author_id}"
            
            # Registrar el tweet encontrado
            logger.info(f"📢 Tweet de @{username}: {tweet.text}")
            
            # Analizar la relevancia del tweet
            relevance = self.openai_service.analyze_tweet_relevance(tweet.text)
            
            if relevance < 0.7:
                logger.info(f"⏭️ Tweet de @{username} ignorado (relevancia: {relevance:.2f})")
                self.db.mark_tweet_processed(
                    tweet_id=tweet.id, 
                    responded=False,
                    tweet_text=tweet.text,
                    response_text=None,
                    author_username=username
                )
                return
                
            # Generar respuesta con OpenAI
            response = self.openai_service.generate_response(tweet.text)
            
            if not response:
                self.db.mark_tweet_processed(
                    tweet_id=tweet.id, 
                    responded=False,
                    tweet_text=tweet.text,
                    response_text=None,
                    author_username=username
                )
                return
                
            logger.info(f"📝 Respuesta generada para @{username}: {response}")
            
            # Responder al tweet si está habilitado
            if self.respond:
                try:
                    result = self.write_client.create_tweet(
                        text=response,
                        in_reply_to_tweet_id=tweet.id
                    )
                    responded = True
                except:
                    responded = False
                
                self.db.mark_tweet_processed(
                    tweet_id=tweet.id, 
                    responded=responded,
                    tweet_text=tweet.text,
                    response_text=response,
                    author_username=username
                )
            else:
                self.db.mark_tweet_processed(
                    tweet_id=tweet.id, 
                    responded=False,
                    tweet_text=tweet.text,
                    response_text=response,
                    author_username=username
                )
                
        except Exception as e:
            logger.error(f"❌ Error al procesar tweet {tweet.id}: {e}")