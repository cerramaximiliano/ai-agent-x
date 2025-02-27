import schedule
import time
import logging
from services.twitter_service import TwitterService
from services.openai_service import OpenAIService
from utils.database import Database

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("crypto_bot.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("crypto_bot")

def main():
    """Función principal del bot de X que maneja criptomonedas"""
    try:
        # Inicializar servicios
        db = Database()
        openai_service = OpenAIService()
        twitter_service = TwitterService(openai_service, db)
        
        # Ejecutar una vez al inicio
        twitter_service.process_tweets()
        
        # Programar ejecuciones periódicas
        schedule.every(15).minutes.do(twitter_service.process_tweets)
        
        # Bucle principal del programa
        logger.info("🚀 Bot iniciado correctamente. Ejecutándose cada 15 minutos.")
        while True:
            schedule.run_pending()
            time.sleep(1)
            
    except KeyboardInterrupt:
        logger.info("👋 Bot detenido manualmente.")
    except Exception as e:
        logger.error(f"❌ Error fatal: {e}")
        raise

if __name__ == "__main__":
    main()