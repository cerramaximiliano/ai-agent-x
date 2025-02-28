---
title: ai-agent-x
app_file: dashboard.py
sdk: gradio
sdk_version: 5.19.0
---
# AI Agent X - Bot de Criptomonedas para X (Twitter)

Bot automatizado que monitorea conversaciones sobre criptomonedas en X (Twitter), genera respuestas relevantes utilizando OpenAI, y opcionalmente puede responder automáticamente a tweets.

## Características

- 🔍 **Monitoreo inteligente** de tweets relacionados con criptomonedas
- 🧠 **Generación de respuestas contextuales** con OpenAI GPT-4
- 📊 **Análisis de relevancia y sentimiento** para identificar tweets importantes
- 🔄 **Manejo avanzado de rate limits** de la API de X (Twitter)
- 📝 **Registro completo de actividad** y estadísticas
- 🔒 **Almacenamiento persistente** de tweets procesados y respuestas
- 🌐 **Dashboard web** para monitoreo en tiempo real
- 🛑 **Espera inteligente** cuando se alcanzan límites de API

## Estructura del Proyecto

```plaintext
crypto-bot-x/
├── config/
│   ├── init.py
│   └── settings.py          # Configuración y variables de entorno
├── services/
│   ├── init.py
│   ├── twitter_service.py   # Interacción con la API de X (Twitter)
│   ├── openai_service.py    # Interacción con la API de OpenAI
│   └── sentiment_service.py # Análisis de sentimiento con Hugging Face
├── utils/
│   └── database.py          # Gestión de tweets procesados
├── scripts/
│   ├── view_tweets.py       # Script para visualizar tweets procesados
│   ├── fix_stats.py         # Herramienta para corregir estadísticas
│   └── update_stats.py      # Actualizador de estadísticas
├── data/
│   └── processed_tweets.json # Base de datos local (se crea automáticamente)
├── .env                     # Variables de entorno (crear a partir de .env.example)
├── .env.example             # Plantilla para variables de entorno
├── .gitignore               # Archivos ignorados por git
├── main.py                  # Punto de entrada principal
├── dashboard.py             # Dashboard de monitoreo
├── requirements.txt         # Dependencias del proyecto
└── README.md                # Documentación (este archivo)
```

## Instalación y Configuración

### 1. Requisitos Previos
Asegúrate de tener instalado Python 3.8 o superior. Si no lo tienes, puedes instalarlo en sistemas basados en Debian/Ubuntu con:

```bash
sudo apt update && sudo apt install python3 python3-venv python3-pip
```

### 2. Clonar el Repositorio

```bash
git clone https://github.com/tu-usuario/crypto-bot-x.git
cd crypto-bot-x
```

### 3. Crear un Entorno Virtual

```bash
python3 -m venv venv
```

### 4. Activar el Entorno Virtual

```bash
source venv/bin/activate  # En Linux/macOS
```
En Windows, usa:
```powershell
venv\Scripts\activate
```

### 5. Instalar las Dependencias

```bash
pip install -r requirements.txt
```

### 6. Configurar Variables de Entorno

```bash
cp .env.example .env
```
Edita el archivo `.env` con tus claves de API:

- Obtén tus credenciales de X (Twitter) en el [Portal para Desarrolladores de X](https://developer.twitter.com/)
- Obtén tu clave de API de OpenAI en [OpenAI Platform](https://platform.openai.com/)
- Opcionalmente, añade tu clave de API de Hugging Face para el análisis de sentimiento

### 7. Crear Directorios Necesarios

```bash
mkdir -p data scripts
```

## Uso del Bot

### Iniciar el Bot
Para ejecutar el bot en modo de simulación (genera respuestas pero no las publica):

```bash
python main.py
```

### Modo de Respuesta Real
Para habilitar la publicación de respuestas reales, modifica el código en `main.py`:

```python
# Cambiar:
twitter_service = TwitterService(openai_service, db)
# Por:
twitter_service = TwitterService(openai_service, db, respond=True)
```

### Utilizar el Dashboard
Para monitorear la actividad del bot en tiempo real:

```bash
python dashboard.py
```
Accede al dashboard desde tu navegador en:

```
http://localhost:7860
```

## Funcionalidades Avanzadas

### Análisis de Sentimiento
El bot analiza el sentimiento de cada tweet para adaptar sus respuestas según el tono emocional del mensaje. Esto permite:

- 📉 Respuestas más empáticas a tweets negativos
- 📈 Tono entusiasta para tweets positivos
- 🧐 Respuestas neutras e informativas para contenido objetivo

### Manejo de Rate Limits
El sistema implementa un manejo sofisticado de límites de tasa de la API de Twitter:

- ⏳ Detección automática de límites de tasa
- 🕒 Espera inteligente del tiempo exacto indicado por la API
- 🔄 Reintentos con backoff exponencial
- 📑 Registro detallado de cada evento de rate limit

### Personalización
Puedes personalizar varios aspectos del bot:

- **Frecuencia de ejecución**: Modifica `schedule.every(15).minutes.do(...)` en `main.py`
- **Consulta de búsqueda**: Modifica `query` en `twitter_service.py`
- **Umbral de relevancia**: Ajusta el valor en `_process_single_tweet`
- **Modelo de OpenAI**: Cambia el modelo en `OpenAIService.__init__`

## Logs y Monitoreo
El bot genera logs detallados que se guardan en el archivo `crypto_bot.log`. Incluyen:

- 📌 Información de inicio y configuración
- 📊 Tweets encontrados y procesados
- 📍 Análisis de sentimiento de cada tweet
- ✍️ Respuestas generadas
- ⚠️ Errores y advertencias
- ⏳ Eventos de rate limit con tiempo de espera

## Mantenimiento

### Actualizar Dependencias

```bash
pip install --upgrade -r requirements.txt
```

### Corregir Estadísticas

```bash
python scripts/fix_stats.py
```

### Limpiar la Base de Datos

```bash
rm data/processed_tweets.json
```

## Resolución de Problemas

### Rate Limits de X (Twitter)
Si encuentras errores de rate limit frecuentemente:

- ⏳ Aumenta el tiempo entre ejecuciones en `main.py`
- 📉 Reduce el número de tweets procesados por ciclo
- 📊 Verifica el estado de los rate limits en el dashboard

### El Bot No Responde a Tweets
Verifica:

- 🔄 Que `respond=True` esté activado si deseas respuestas reales
- 🔍 Que la consulta de búsqueda esté encontrando tweets relevantes
- 📏 Que los tweets superen el umbral de relevancia (`0.7` por defecto)
- 🔑 Que las credenciales de API estén configuradas correctamente

## Contribuir
Las contribuciones son bienvenidas. Por favor, abre un issue para discutir cambios importantes antes de enviar un pull request.

## Nota Legal
Este bot debe utilizarse de acuerdo con los términos de servicio de X (Twitter) y OpenAI. El uso excesivo o inapropiado puede resultar en limitaciones o suspensión de tus cuentas.