import openai
from config.settings import OPENAI_API_KEY

# Configurar la API Key de OpenAI
client = openai.OpenAI(api_key=OPENAI_API_KEY)

def generate_response(tweet_text):
    """
    Genera una respuesta basada en el texto del tweet usando OpenAI GPT-4.
    """
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Eres un bot de X especializado en criptomonedas. Responde de manera informativa y amigable."},
                {"role": "user", "content": f"Responde a este tweet de manera breve y concisa: {tweet_text}"}
            ]
        )
        return response.choices[0].message.content

    except Exception as e:
        print(f"❌ Error al generar respuesta con OpenAI: {e}")
        return None
