# AI Agent X - Bot de Criptomonedas para X (Twitter)

Bot automatizado que monitorea conversaciones sobre criptomonedas en X (Twitter), genera respuestas relevantes utilizando OpenAI, y puede responder automáticamente a tweets.

## Características

- 🔍 Monitoreo de tweets relacionados con criptomonedas
- 🧠 Generación de respuestas con OpenAI GPT-4
- 📊 Sistema de análisis de relevancia para filtrar tweets
- 🔄 Procesamiento periódico de tweets nuevos
- 📝 Registro completo de actividad y estadísticas
- 🔒 Evita responder a tweets ya procesados
- 🧪 Modo de simulación y modo de respuesta real

## Estructura del Proyecto

```
crypto-bot-x/
├── config/
│   ├── __init__.py
│   └── settings.py          # Configuración y variables de entorno
├── services/
│   ├── __init__.py
│   ├── twitter_service.py   # Interacción con la API de X (Twitter)
│   └── openai_service.py    # Interacción con la API de OpenAI
├── utils/
│   └── database.py          # Gestión de tweets procesados
├── data/
│   └── processed_tweets.json # Base de datos local (se crea automáticamente)
├── .env                     # Variables de entorno (crear a partir de .env.example)
├── .env.example             # Plantilla para variables de entorno
├── .gitignore               # Archivos ignorados por git
├── main.py                  # Punto de entrada principal
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
Para evitar conflictos con paquetes del sistema, se recomienda el uso de un entorno virtual:

```bash
python3 -m venv venv
```

### 4. Activar el Entorno Virtual
Una vez creado, activa el entorno virtual con:

```bash
source venv/bin/activate  # En Linux/macOS
```

Si estás en Windows, usa:

```powershell
venv\Scripts\activate
```

Al activar el entorno virtual, tu terminal debería mostrar un prefijo `(venv)`, indicando que estás dentro del entorno virtual.

### 5. Instalar las Dependencias
Con el entorno virtual activado, instala los paquetes necesarios:

```bash
pip install -r requirements.txt
```

### 6. Configurar Variables de Entorno
Copia el archivo `.env.example` a `.env` y configura tus credenciales:

```bash
cp .env.example .env
```

Edita el archivo `.env` con tus claves de API:
- Obtén tus credenciales de X (Twitter) en el [Portal para Desarrolladores de X](https://developer.twitter.com/)
- Obtén tu clave de API de OpenAI en [OpenAI Platform](https://platform.openai.com/account/api-keys)

### 7. Crear Directorios Necesarios
```bash
mkdir -p data
```

## Uso del Bot

### Modo de Simulación (por defecto)
Para ejecutar el bot en modo de simulación (genera respuestas pero no las publica):

```bash
python main.py
```

### Modo de Respuesta Real
Para habilitar la publicación de respuestas reales, debes modificar el código en `main.py`:

```python
# Cambiar:
twitter_service = TwitterService(openai_service, db)
# Por:
twitter_service = TwitterService(openai_service, db, respond=True)
```

### Personalización del Bot

Puedes personalizar varios aspectos del bot:

- **Frecuencia de ejecución**: Modifica el valor en la línea `schedule.every(15).minutes.do(...)` en `main.py`
- **Consulta de búsqueda**: Modifica el valor de `query` en el método `process_tweets` de `twitter_service.py`
- **Umbral de relevancia**: Modifica el valor de comparación con `relevance` en `_process_single_tweet`
- **Modelo de OpenAI**: Cambia el modelo predeterminado en `OpenAIService.__init__`

## Logs y Monitoreo

El bot genera logs detallados que se guardan en el archivo `crypto_bot.log` y también se muestran en la consola. Los logs incluyen:

- Información de inicio y configuración
- Tweets encontrados y procesados
- Respuestas generadas
- Errores y advertencias

## Mantenimiento

### Actualizar Dependencias
Para actualizar a las últimas versiones de las dependencias:

```bash
pip install --upgrade -r requirements.txt
```

### Guardar Nuevas Dependencias
Si agregas nuevas librerías al proyecto:

```bash
pip freeze > requirements.txt
```

### Limpiar la Base de Datos
Para resetear el historial de tweets procesados:

```bash
rm data/processed_tweets.json
```

## Resolución de Problemas

### Rate Limits de X (Twitter)
Si encuentras errores de rate limit frecuentemente, puedes aumentar el tiempo entre ejecuciones en `main.py`.

### Errores de OpenAI
El bot incluye reintentos automáticos con backoff exponencial para problemas temporales con OpenAI.

### El Bot No Responde a Tweets
Verifica:
1. Que el modo `respond=True` esté activado si deseas respuestas reales
2. Que la consulta de búsqueda esté encontrando tweets relevantes
3. Que los tweets estén superando el umbral de relevancia (0.7 por defecto)
4. Que las credenciales de API estén configuradas correctamente

## Contribuir

Las contribuciones son bienvenidas. Por favor, abre un issue para discutir cambios importantes antes de enviar un pull request.

## Nota Legal

Este bot debe utilizarse de acuerdo con los términos de servicio de X (Twitter) y OpenAI. El uso excesivo o inapropiado puede resultar en limitaciones o suspensión de tus cuentas.