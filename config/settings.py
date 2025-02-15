import os
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
load_dotenv()

# Configuración de la API de X (Twitter)
X_API_PROJECT_ID = os.getenv("X_API_PROJECT_ID")
X_API_KEY_CONSUMER = os.getenv("X_API_KEY_CONSUMER")
X_API_KEY_SECRET_CONSUMER = os.getenv("X_API_KEY_SECRET_CONSUMER")
X_API_BEARER = os.getenv("X_API_BEARER")
X_API_KEY = os.getenv("X_API_KEY")
X_API_KEY_SECRET = os.getenv("X_API_KEY_SECRET")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Verificar que todas las credenciales sean correctas
if not all([X_API_PROJECT_ID, X_API_KEY_CONSUMER, X_API_KEY_SECRET_CONSUMER, X_API_BEARER, X_API_KEY, X_API_KEY_SECRET, OPENAI_API_KEY]):
    raise ValueError("❌ ERROR: Faltan credenciales en el archivo .env")