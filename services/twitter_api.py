import tweepy
import time
import logging
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
            max_results: Número máximo de tweets a procesar por consulta
            respond: Si es True, responderá a los tweets. Si es False, solo simulará
        """
        self.openai_service = openai_service
        self.db = db
        self.max_results = max_results
        self.respond = respond
        
        # Cliente solo para lectura (búsqueda)
        self.read_client = tweepy.Client(
            bearer_token=X_API_BEARER,
            wait_on_rate_limit=True
        )
        
        # Cliente para lectura y escritura (responder)
        if self.respond:
            self.write_client = tweepy.Client(
                consumer_key=X_API_KEY_CONSUMER,
                consumer_secret=X_API_KEY_SECRET_CONSUMER,
                access_token=X_API_KEY,
                access_token_secret=X_API_KEY_SECRET,
                wait_on_rate_limit=True
            )
    
    def process_tweets(self):
        """Busca tweets recientes y genera/envía respuestas"""
        try:
            logger.info("🔍 Buscando tweets recientes sobre criptomonedas...")
            query = "crypto -is:retweet lang:es OR lang:en"
            tweets = self.read_client.search_recent_tweets(
                query=query, 
                max_results=self.max_results, 
                tweet_fields=["author_id", "created_at", "public_metrics"]
            )
            
            if not tweets.data:
                logger.info("⚠️ No se encontraron tweets recientes.")
                return
                
            logger.info(f"✅ Encontrados {len(tweets.data)} tweets para procesar.")
            
            for tweet in tweets.data:
                self._process_single_tweet(tweet)
                
            logger.info("✅ Procesamiento de tweets completado.")
                
        except tweepy.errors.TooManyRequests:
            logger.warning("⚠️ Rate limit alcanzado. Esperando antes de reintentar...")
            time.sleep(15 * 60)  # 15 minutos
        except Exception as e:
            logger.error(f"❌ Error al procesar tweets: {e}")
    
    def _process_single_tweet(self, tweet):
        """Procesa un tweet individual"""
        try:
            # Verificar si ya procesamos este tweet
            if self.db.is_tweet_processed(tweet.id):
                logger.debug(f"⏭️ Tweet {tweet.id} ya procesado anteriormente.")
                return
                
            # Obtener información del usuario
            user = self.read_client.get_user(id=tweet.author_id, user_fields=["username"])
            username = user.data.username
            
            # Registrar el tweet encontrado
            logger.info(f"📢 Tweet de @{username}: {tweet.text}")
            
            # Analizar la relevancia del tweet para determinar si merece respuesta
            relevance = self.openai_service.analyze_tweet_relevance(tweet.text)
            
            if relevance < 0.7:  # Umbral de relevancia
                logger.info(f"⏭️ Tweet de @{username} ignorado (relevancia: {relevance:.2f})")
                self.db.mark_tweet_processed(tweet.id, responded=False)
                return
                
            # Generar respuesta con OpenAI
            response = self.openai_service.generate_response(tweet.text)
            
            if not response:
                logger.warning(f"⚠️ No se pudo generar respuesta para tweet de @{username}")
                self.db.mark_tweet_processed(tweet.id, responded=False)
                return
                
            logger.info(f"📝 Respuesta generada para @{username}: {response}")
            
            # Responder al tweet si está habilitado
            if self.respond:
                self._reply_to_tweet(tweet.id, response)
                self.db.mark_tweet_processed(tweet.id, responded=True)
            else:
                logger.info("ℹ️ Modo simulación: no se envió respuesta real")
                self.db.mark_tweet_processed(tweet.id, responded=False)
                
        except Exception as e:
            logger.error(f"❌ Error al procesar tweet {tweet.id}: {e}")
    
    def _reply_to_tweet(self, tweet_id, response_text):
        """Responde a un tweet específico"""
        try:
            result = self.write_client.create_tweet(
                text=response_text,
                in_reply_to_tweet_id=tweet_id
            )
            logger.info(f"✅ Respuesta enviada correctamente. ID: {result.data['id']}")
            return True
        except Exception as e:
            logger.error(f"❌ Error al responder al tweet {tweet_id}: {e}")
            return False