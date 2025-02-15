import tweepy
import time
from config.settings import X_API_BEARER
from services.openai_service import generate_response

# Cliente de la API de X
client = tweepy.Client(bearer_token=X_API_BEARER, wait_on_rate_limit=True)

# Función para buscar tweets recientes sobre "crypto" y generar respuestas sin publicarlas
def search_and_test_responses():
    try:
        query = "crypto -is:retweet"
        tweets = client.search_recent_tweets(query=query, max_results=10, tweet_fields=["author_id"])

        if tweets.data:
            for tweet in tweets.data:
                # Obtener información del usuario que publicó el tweet
                user = client.get_user(id=tweet.author_id, user_fields=["username"])

                print(f"📢 Nuevo tweet detectado de @{user.data.username}: {tweet.text}")

                # Generar respuesta con OpenAI
                response = generate_response(tweet.text)
                
                if response:
                    print(f"📝 Respuesta generada: {response}\n")
                else:
                    print("❌ No se generó una respuesta válida.\n")

        else:
            print("⚠️ No se encontraron tweets recientes.")

    except tweepy.errors.TooManyRequests:
        print("⚠️ Rate limit alcanzado. Esperando 15 minutos antes de reintentar...")
        time.sleep(15 * 60)
    except Exception as e:
        print(f"❌ Error inesperado: {e}")

# Ejecutar la búsqueda cada 2 minutos para testear respuestas sin publicarlas
while True:
    search_and_test_responses()
    time.sleep(120)  # Espera 2 minutos entre cada búsqueda
