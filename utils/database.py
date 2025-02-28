import os
import json
import logging
from datetime import datetime

logger = logging.getLogger("crypto_bot.database")

class Database:
    """
    Clase para gestionar el almacenamiento de tweets procesados.
    Ahora también almacena datos de sentimiento y rate limits.
    """
    
    def __init__(self, db_file="data/processed_tweets.json"):
        """
        Inicializa la base de datos local.
        
        Args:
            db_file: Ruta al archivo JSON que almacenará los tweets procesados
        """
        self.db_file = db_file
        self._ensure_data_dir()
        self._init_db()
    
    def _ensure_data_dir(self):
        """Asegura que existe el directorio de datos"""
        os.makedirs(os.path.dirname(self.db_file), exist_ok=True)
    
    def _init_db(self):
        """Inicializa la base de datos si no existe"""
        if not os.path.exists(self.db_file):
            with open(self.db_file, 'w') as f:
                json.dump({
                    "processed_tweets": {},
                    "stats": {
                        "total_processed": 0,
                        "total_responded": 0
                    },
                    "rate_limits": {
                        "last_encounter": None,
                        "wait_seconds": 0,
                        "history": []
                    }
                }, f)
            logger.info(f"✅ Base de datos inicializada en {self.db_file}")
    
    def _load_db(self):
        """Carga los datos de la base de datos"""
        try:
            with open(self.db_file, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            logger.error(f"❌ Error al leer la base de datos. Creando nueva.")
            return {
                "processed_tweets": {}, 
                "stats": {
                    "total_processed": 0, 
                    "total_responded": 0
                },
                "rate_limits": {
                    "last_encounter": None,
                    "wait_seconds": 0,
                    "history": []
                }
            }
    
    def _save_db(self, data):
        """Guarda los datos en la base de datos"""
        with open(self.db_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def is_tweet_processed(self, tweet_id):
        """
        Verifica si un tweet ya ha sido procesado.
        
        Args:
            tweet_id: ID del tweet a verificar
            
        Returns:
            bool: True si ya fue procesado, False en caso contrario
        """
        db = self._load_db()
        return str(tweet_id) in db["processed_tweets"]
    
    def mark_tweet_processed(self, tweet_id, responded=False, tweet_text=None, response_text=None, author_username=None, sentiment_data=None):
        """
        Marca un tweet como procesado y almacena su contenido y respuesta.
        
        Args:
            tweet_id: ID del tweet procesado
            responded: Si se respondió o no al tweet
            tweet_text: El texto original del tweet
            response_text: La respuesta generada para el tweet
            author_username: Nombre de usuario del autor del tweet
            sentiment_data: Datos de análisis de sentimiento (opcional)
        """
        db = self._load_db()
        
        # Comprobar si el tweet ya fue procesado
        tweet_already_processed = str(tweet_id) in db["processed_tweets"]
        
        # Registrar el tweet con su contenido y respuesta
        db["processed_tweets"][str(tweet_id)] = {
            "processed_at": datetime.now().isoformat(),
            "responded": responded,
            "author_username": author_username,
            "tweet_text": tweet_text,
            "response_text": response_text
        }
        
        # Agregar datos de sentimiento si están disponibles
        if sentiment_data:
            db["processed_tweets"][str(tweet_id)]["sentiment"] = sentiment_data
        
        # Actualizar estadísticas sólo si es un tweet nuevo
        if not tweet_already_processed:
            db["stats"]["total_processed"] += 1
        
        # Si tiene una respuesta generada, contar como respondido para estadísticas
        if response_text:
            # Comprobar si ya tenía una respuesta generada
            old_response = False
            if tweet_already_processed:
                old_response = db["processed_tweets"][str(tweet_id)].get("response_text") is not None
            
            # Solo incrementar el contador si es nuevo o no tenía respuesta antes
            if not tweet_already_processed or not old_response:
                db["stats"]["total_responded"] += 1
        
        self._save_db(db)
        logger.info(f"✅ Tweet {tweet_id} de @{author_username} guardado en la base de datos")
    
    def record_rate_limit(self, wait_seconds, endpoint=None):
        """
        Registra información sobre un rate limit encontrado.
        
        Args:
            wait_seconds: Tiempo de espera en segundos
            endpoint: Endpoint de la API que generó el rate limit (opcional)
        """
        db = self._load_db()
        
        # Asegurarse de que la sección de rate_limits existe
        if "rate_limits" not in db:
            db["rate_limits"] = {
                "last_encounter": None,
                "wait_seconds": 0,
                "history": []
            }
        
        # Actualizar información del último rate limit
        current_time = datetime.now().isoformat()
        db["rate_limits"]["last_encounter"] = current_time
        db["rate_limits"]["wait_seconds"] = wait_seconds
        
        # Agregar a historial (limitado a los últimos 10 eventos)
        db["rate_limits"]["history"].append({
            "timestamp": current_time,
            "wait_seconds": wait_seconds,
            "endpoint": endpoint
        })
        
        # Mantener historial limitado a 10 eventos
        if len(db["rate_limits"]["history"]) > 10:
            db["rate_limits"]["history"] = db["rate_limits"]["history"][-10:]
        
        self._save_db(db)
        logger.info(f"📊 Rate limit registrado: {wait_seconds} segundos")
    
    def get_rate_limit_info(self):
        """
        Obtiene información sobre los rate limits.
        
        Returns:
            dict: Información de rate limits
        """
        db = self._load_db()
        return db.get("rate_limits", {
            "last_encounter": None,
            "wait_seconds": 0,
            "history": []
        })
    
    def get_tweet_details(self, tweet_id):
        """
        Obtiene los detalles de un tweet procesado.
        
        Args:
            tweet_id: ID del tweet
            
        Returns:
            dict: Detalles del tweet o None si no existe
        """
        db = self._load_db()
        tweet_id_str = str(tweet_id)
        
        if tweet_id_str in db["processed_tweets"]:
            return db["processed_tweets"][tweet_id_str]
        return None
        
    def get_stats(self):
        """
        Obtiene estadísticas de tweets procesados.
        
        Returns:
            dict: Estadísticas actuales
        """
        db = self._load_db()
        return db.get("stats", {"total_processed": 0, "total_responded": 0})
        
    def get_last_processed_tweets(self, limit=10):
        """
        Obtiene los últimos tweets procesados.
        
        Args:
            limit: Número máximo de tweets a retornar
            
        Returns:
            list: Lista de los últimos tweets procesados con sus detalles
        """
        db = self._load_db()
        tweets = db.get("processed_tweets", {})
        
        # Convertir a lista y agregar ID como propiedad
        tweet_list = [
            {"id": tweet_id, **details} 
            for tweet_id, details in tweets.items()
        ]
        
        # Ordenar por fecha de procesamiento (descendente)
        tweet_list.sort(key=lambda x: x.get("processed_at", ""), reverse=True)
        
        # Retornar solo los más recientes según el límite
        return tweet_list[:limit]