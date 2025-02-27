import os
import json
import logging
from datetime import datetime

logger = logging.getLogger("crypto_bot.database")

class Database:
    """
    Clase simple para gestionar el almacenamiento de tweets procesados.
    En una implementación más robusta, esto podría usar MongoDB u otra BD.
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
            return {"processed_tweets": {}, "stats": {"total_processed": 0, "total_responded": 0}}
    
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
    
    def mark_tweet_processed(self, tweet_id, responded=False):
        """
        Marca un tweet como procesado.
        
        Args:
            tweet_id: ID del tweet procesado
            responded: Si se respondió o no al tweet
        """
        db = self._load_db()
        
        # Registrar el tweet
        db["processed_tweets"][str(tweet_id)] = {
            "processed_at": datetime.now().isoformat(),
            "responded": responded
        }
        
        # Actualizar estadísticas
        db["stats"]["total_processed"] += 1
        if responded:
            db["stats"]["total_responded"] += 1
        
        self._save_db(db)
        
    def get_stats(self):
        """
        Obtiene estadísticas de tweets procesados.
        
        Returns:
            dict: Estadísticas actuales
        """
        db = self._load_db()
        return db["stats"]