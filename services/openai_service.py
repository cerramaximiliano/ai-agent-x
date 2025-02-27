import openai
import logging
import time
from config.settings import OPENAI_API_KEY

logger = logging.getLogger("crypto_bot.openai")

class OpenAIService:
    def __init__(self, model="gpt-4", max_retries=3):
        """
        Inicializa el servicio de OpenAI.
        
        Args:
            model: Modelo de OpenAI a utilizar
            max_retries: Número máximo de reintentos en caso de error
        """
        # Configuración para versión 0.28.x
        openai.api_key = OPENAI_API_KEY
        self.model = model
        self.max_retries = max_retries
    
    def generate_response(self, tweet_text):
        """
        Genera una respuesta basada en el texto del tweet usando OpenAI.
        
        Args:
            tweet_text: Texto del tweet al que se responderá
            
        Returns:
            str: Respuesta generada o None si hay error
        """
        system_prompt = """
        Eres un bot de X especializado en criptomonedas. Responde de manera informativa,
        amigable y concisa. Tu objetivo es proporcionar valor y ayudar a las personas
        interesadas en criptomonedas. Limita tus respuestas a 280 caracteres.
        Nunca menciones que eres una IA o un bot.
        """
        
        for attempt in range(self.max_retries):
            try:
                # API para versión 0.28.x
                response = openai.ChatCompletion.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": f"Responde a este tweet: {tweet_text}"}
                    ],
                    max_tokens=120,  # Limitado para mantener respuestas cortas
                    temperature=0.7   # Balance entre creatividad y coherencia
                )
                
                # Estructura de respuesta para 0.28.x
                reply = response['choices'][0]['message']['content'].strip()
                
                # Asegurar que la respuesta no excede el límite de caracteres
                if len(reply) > 280:
                    reply = reply[:277] + "..."
                    
                return reply
                
            except openai.error.RateLimitError as e:
                wait_time = 2 ** attempt  # Backoff exponencial
                logger.warning(f"⚠️ OpenAI temporalmente no disponible. Reintentando en {wait_time}s: {e}")
                time.sleep(wait_time)
                
            except Exception as e:
                logger.error(f"❌ Error al generar respuesta con OpenAI: {e}")
                break
                
        return None
    
    def analyze_tweet_relevance(self, tweet_text):
        """
        Analiza la relevancia de un tweet para determinar si merece respuesta.
        
        Args:
            tweet_text: Texto del tweet a analizar
            
        Returns:
            float: Puntuación de relevancia entre 0.0 y 1.0
        """
        system_prompt = """
        Evalúa la relevancia de un tweet sobre criptomonedas. Asigna una puntuación
        entre 0.0 y 1.0 donde:
        - 0.0: Completamente irrelevante o spam
        - 0.5: Moderadamente relevante
        - 1.0: Altamente relevante, pregunta directa o discusión interesante
        Responde solamente con el número.
        """
        
        try:
            # API para versión 0.28.x
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": tweet_text}
                ],
                max_tokens=10,
                temperature=0.1  # Baja temperatura para respuestas consistentes
            )
            
            # Extraer el valor numérico
            relevance_text = response['choices'][0]['message']['content'].strip()
            try:
                relevance = float(relevance_text)
                # Asegurar que está en el rango correcto
                relevance = max(0.0, min(1.0, relevance))
                return relevance
            except ValueError:
                logger.warning(f"⚠️ No se pudo convertir la relevancia a número: {relevance_text}")
                return 0.5  # Valor por defecto
                
        except Exception as e:
            logger.error(f"❌ Error al analizar relevancia: {e}")
            return 0.5  # Valor por defecto en caso de error