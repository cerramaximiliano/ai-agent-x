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
    def __init__(self, openai_service, db, sentiment_service=None, max_results=10, respond=False):
        """
        Inicializa el servicio de Twitter.
        
        Args:
            openai_service: Servicio para generar respuestas con OpenAI
            db: Servicio de base de datos
            sentiment_service: Servicio opcional para análisis de sentimiento
            max_results: Número máximo de tweets a procesar por consulta
            respond: Si es True, responderá a los tweets. Si es False, solo simulará
        """
        self.openai_service = openai_service
        self.db = db
        self.sentiment_service = sentiment_service
        self.max_results = max_results
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
            query = "crypto -is:retweet lang:en OR lang:es"
            
            # Intentar obtener tweets con manejo de rate limits
            tweets = self._safe_api_call(
                lambda: self.read_client.search_recent_tweets(
                    query=query, 
                    max_results=10,
                    tweet_fields=["author_id", "created_at"]
                ),
                endpoint="search_recent_tweets"
            )
            
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
                
                # Procesar tweet con manejo de errores
                try:
                    self._process_single_tweet(tweet)
                except Exception as e:
                    logger.error(f"❌ Error al procesar tweet {tweet.id}: {e}")
                    continue
                
            logger.info("✅ Procesamiento de tweets completado.")
                
        except Exception as e:
            logger.error(f"❌ Error al procesar tweets: {e}")
    
    def _safe_api_call(self, api_function, endpoint=None, max_retries=3):
        """
        Ejecuta una función de API de manera segura, manejando rate limits.
        
        Args:
            api_function: Función lambda que contiene la llamada a la API
            endpoint: Nombre del endpoint para registro (opcional)
            max_retries: Número máximo de reintentos
            
        Returns:
            El resultado de la función o None si hay un error persistente
        """
        retries = 0
        
        while retries < max_retries:
            try:
                return api_function()
            except tweepy.errors.TooManyRequests as e:
                # Extraer el tiempo de espera de la respuesta
                wait_seconds = self._extract_rate_limit_wait_time(e)
                
                # Registrar el rate limit en la base de datos
                self.db.record_rate_limit(wait_seconds, endpoint)
                
                retries += 1
                if retries >= max_retries:
                    logger.error(f"❌ Alcanzado número máximo de reintentos ({max_retries}). Abortando operación.")
                    raise e
                
                logger.warning(f"⚠️ Rate limit alcanzado ({wait_seconds} segundos). Esperando antes de reintentar... ({retries}/{max_retries})")
                
                # Esperar el tiempo indicado antes de reintentar
                time.sleep(wait_seconds)
            except Exception as e:
                logger.error(f"❌ Error en llamada a API: {e}")
                raise e
    
    def _extract_rate_limit_wait_time(self, error):
        """
        Extrae el tiempo de espera del error de rate limit de Twitter.
        
        Args:
            error: Objeto de excepción de TooManyRequests
            
        Returns:
            int: Tiempo de espera en segundos o valor por defecto
        """
        try:
            # Intentar extraer el tiempo de espera del mensaje de error
            error_message = str(error)
            if "Retry-After" in error_message:
                import re
                wait_time_match = re.search(r'Retry-After: (\d+)', error_message)
                if wait_time_match:
                    return int(wait_time_match.group(1))
            
            # Intentar extraer el tiempo de reset de los headers de respuesta
            if hasattr(error, 'response') and hasattr(error.response, 'headers'):
                headers = error.response.headers
                if 'x-rate-limit-reset' in headers:
                    reset_time = int(headers['x-rate-limit-reset'])
                    current_time = int(time.time())
                    return max(reset_time - current_time, 1)
                if 'retry-after' in headers:
                    return int(headers['retry-after'])
            
            # Si no podemos extraer el tiempo, verificar el mensaje
            if "Try again in" in error_message:
                import re
                wait_time_match = re.search(r'Try again in (\d+)', error_message)
                if wait_time_match:
                    return int(wait_time_match.group(1))
            
            # Si llegamos aquí, no pudimos extraer el tiempo de espera
            return 60  # Valor por defecto de 1 minuto (60 segundos)
        except Exception as e:
            logger.error(f"Error al extraer tiempo de rate limit: {e}")
            return 60  # Valor por defecto de 1 minuto (60 segundos)
    
    def _process_single_tweet(self, tweet):
        """Procesa un tweet individual"""
        try:
            # Verificar si ya procesamos este tweet
            if self.db.is_tweet_processed(tweet.id):
                logger.debug(f"⏭️ Tweet {tweet.id} ya procesado anteriormente.")
                return
            
            # Obtener información del usuario con manejo seguro de rate limits
            username = None
            try:
                user_result = self._safe_api_call(
                    lambda: self.read_client.get_user(id=tweet.author_id, user_fields=["username"]),
                    endpoint="get_user"
                )
                
                if user_result and user_result.data:
                    username = user_result.data.username
                else:
                    username = f"usuario_{tweet.author_id}"
            except Exception as e:
                logger.warning(f"⚠️ No se pudo obtener información del usuario: {e}")
                username = f"usuario_{tweet.author_id}"
            
            # Registrar el tweet encontrado
            logger.info(f"📢 Tweet de @{username}: {tweet.text}")
            
            # Analizar sentimiento si está disponible
            sentiment = None
            if self.sentiment_service:
                sentiment = self.sentiment_service.analyze_sentiment(tweet.text)
                sentiment_label = sentiment.get("label", "unknown")
                sentiment_score = sentiment.get("sentiment_score", 0)
                logger.info(f"📊 Sentimiento detectado: {sentiment_label} ({sentiment_score:.2f})")
            
            # Analizar la relevancia del tweet
            relevance = self.openai_service.analyze_tweet_relevance(tweet.text)
            
            if relevance < 0.7:
                logger.info(f"⏭️ Tweet de @{username} ignorado (relevancia: {relevance:.2f})")
                self.db.mark_tweet_processed(
                    tweet_id=tweet.id, 
                    responded=False,
                    tweet_text=tweet.text,
                    response_text=None,
                    author_username=username,
                    sentiment_data=sentiment
                )
                return
                
            # Generar respuesta con OpenAI, pasando el sentimiento
            response = self.openai_service.generate_response(tweet.text, sentiment)
            
            if not response:
                self.db.mark_tweet_processed(
                    tweet_id=tweet.id, 
                    responded=False,
                    tweet_text=tweet.text,
                    response_text=None,
                    author_username=username,
                    sentiment_data=sentiment
                )
                return
                
            logger.info(f"📝 Respuesta generada para @{username}: {response}")
            
            # Responder al tweet si está habilitado
            if self.respond:
                try:
                    # Usar _safe_api_call para manejar rate limits al responder
                    result = self._safe_api_call(
                        lambda: self.write_client.create_tweet(
                            text=response,
                            in_reply_to_tweet_id=tweet.id
                        ),
                        endpoint="create_tweet"
                    )
                    responded = True
                    logger.info(f"✅ Respuesta enviada correctamente a @{username}")
                except Exception as e:
                    logger.error(f"❌ Error al responder al tweet: {e}")
                    responded = False
                
                self.db.mark_tweet_processed(
                    tweet_id=tweet.id, 
                    responded=responded,
                    tweet_text=tweet.text,
                    response_text=response,
                    author_username=username,
                    sentiment_data=sentiment
                )
            else:
                self.db.mark_tweet_processed(
                    tweet_id=tweet.id, 
                    responded=False,
                    tweet_text=tweet.text,
                    response_text=response,
                    author_username=username,
                    sentiment_data=sentiment
                )
                
        except Exception as e:
            logger.error(f"❌ Error al procesar tweet {tweet.id}: {e}")