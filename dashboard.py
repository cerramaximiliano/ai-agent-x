import os
import sys
import time
import gradio as gr
from datetime import datetime, timedelta

# Agregar el directorio raíz del proyecto al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Importar la clase Database
from utils.database import Database

def format_date(iso_date):
    """Formatea una fecha ISO a un formato más legible"""
    if not iso_date:
        return "Nunca"
    try:
        dt = datetime.fromisoformat(iso_date)
        return dt.strftime("%d/%m/%Y %H:%M:%S")
    except:
        return iso_date

def format_time_ago(iso_date):
    """Convierte una fecha ISO a 'hace X tiempo'"""
    if not iso_date:
        return "Nunca"
    try:
        dt = datetime.fromisoformat(iso_date)
        now = datetime.now()
        delta = now - dt
        
        if delta.days > 0:
            return f"hace {delta.days} día(s)"
        elif delta.seconds // 3600 > 0:
            return f"hace {delta.seconds // 3600} hora(s)"
        elif delta.seconds // 60 > 0:
            return f"hace {delta.seconds // 60} minuto(s)"
        else:
            return f"hace {delta.seconds} segundo(s)"
    except:
        return iso_date

def format_seconds(seconds):
    """Formatea segundos en un formato más legible"""
    if not seconds:
        return "0 segundos"
    
    minutes, sec = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    
    if hours > 0:
        return f"{int(hours)}h {int(minutes)}m {int(sec)}s"
    elif minutes > 0:
        return f"{int(minutes)}m {int(sec)}s"
    else:
        return f"{int(sec)}s"

def calculate_reset_time(iso_date, seconds):
    """Calcula cuando se reseteará el rate limit"""
    if not iso_date or not seconds:
        return "Desconocido"
    
    try:
        encounter_time = datetime.fromisoformat(iso_date)
        reset_time = encounter_time + timedelta(seconds=seconds)
        now = datetime.now()
        
        if reset_time < now:
            return "Ya disponible"
        
        delta = reset_time - now
        if delta.days > 0:
            return f"En {delta.days}d {(delta.seconds // 3600)}h {(delta.seconds % 3600) // 60}m"
        elif delta.seconds // 3600 > 0:
            return f"En {delta.seconds // 3600}h {(delta.seconds % 3600) // 60}m"
        else:
            return f"En {delta.seconds // 60}m {delta.seconds % 60}s"
    except:
        return "Desconocido"

def get_stats_html():
    """Obtiene estadísticas formateadas en HTML"""
    db = Database()
    stats = db.get_stats()
    processed = stats.get('total_processed', 0)
    responded = stats.get('total_responded', 0)
    
    # Calcular porcentaje de respuesta
    response_rate = (responded / processed * 100) if processed > 0 else 0
    
    stats_html = f"""
    <div style="background-color: #f5f7ff; padding: 15px; border-radius: 8px; margin-bottom: 20px;">
        <h2 style="margin-top: 0; color: #3b5998;">Estadísticas del Bot</h2>
        <ul style="list-style-type: none; padding-left: 0;">
            <li><b>Total de tweets procesados:</b> {processed}</li>
            <li><b>Total de tweets con respuestas:</b> {responded}</li>
            <li><b>Tasa de respuesta:</b> {response_rate:.1f}%</li>
            <li><b>Última actualización:</b> {datetime.now().strftime("%d/%m/%Y %H:%M:%S")}</li>
        </ul>
    </div>
    """
    return stats_html

def get_rate_limit_html():
    """Obtiene información de rate limits formateada en HTML"""
    db = Database()
    rate_limits = db.get_rate_limit_info()
    
    last_encounter = rate_limits.get('last_encounter')
    wait_seconds = rate_limits.get('wait_seconds', 0)
    history = rate_limits.get('history', [])
    
    # Si no hay información de rate limits
    if not last_encounter:
        return """
        <div style="background-color: #e8f5e9; padding: 15px; border-radius: 8px; margin-bottom: 20px;">
            <h2 style="margin-top: 0; color: #2e7d32;">Estado de Rate Limits</h2>
            <p>No se han detectado rate limits desde el inicio del bot.</p>
        </div>
        """
    
    # Calcular tiempo de reset
    reset_status = calculate_reset_time(last_encounter, wait_seconds)
    time_ago = format_time_ago(last_encounter)
    
    # Determinar color según el estado
    if reset_status == "Ya disponible":
        status_color = "#e8f5e9"  # Verde claro
        text_color = "#2e7d32"    # Verde oscuro
    else:
        status_color = "#fff3e0"  # Naranja claro
        text_color = "#e65100"    # Naranja oscuro
    
    # Tabla de historial
    history_rows = ""
    for entry in sorted(history, key=lambda x: x.get('timestamp', ''), reverse=True):
        timestamp = format_date(entry.get('timestamp'))
        wait_time = format_seconds(entry.get('wait_seconds', 0))
        endpoint = entry.get('endpoint', 'Desconocido')
        
        history_rows += f"""
        <tr>
            <td>{timestamp}</td>
            <td>{wait_time}</td>
            <td>{endpoint}</td>
        </tr>
        """
    
    rate_limit_html = f"""
    <div style="background-color: {status_color}; padding: 15px; border-radius: 8px; margin-bottom: 20px;">
        <h2 style="margin-top: 0; color: {text_color};">Estado de Rate Limits</h2>
        <ul style="list-style-type: none; padding-left: 0;">
            <li><b>Último rate limit:</b> {time_ago}</li>
            <li><b>Tiempo de espera:</b> {format_seconds(wait_seconds)}</li>
            <li><b>Estado actual:</b> {reset_status}</li>
        </ul>
        
        <h3 style="margin-top: 15px; color: {text_color};">Historial de Rate Limits</h3>
        <div style="max-height: 200px; overflow-y: auto;">
            <table style="width: 100%; border-collapse: collapse;">
                <thead>
                    <tr style="background-color: rgba(0,0,0,0.05);">
                        <th style="padding: 8px; text-align: left; border-bottom: 1px solid #ddd;">Fecha</th>
                        <th style="padding: 8px; text-align: left; border-bottom: 1px solid #ddd;">Espera</th>
                        <th style="padding: 8px; text-align: left; border-bottom: 1px solid #ddd;">Endpoint</th>
                    </tr>
                </thead>
                <tbody>
                    {history_rows}
                </tbody>
            </table>
        </div>
    </div>
    """
    return rate_limit_html

def get_tweets_html():
    """Obtiene los tweets más recientes formateados en HTML"""
    db = Database()
    tweets = db.get_last_processed_tweets(limit=10)
    
    if not tweets:
        return "<p>No hay tweets procesados todavía.</p>"
    
    # Formatear los tweets en HTML
    tweets_html = '<h2>Tweets procesados recientemente</h2>'
    
    for i, tweet in enumerate(tweets, 1):
        # Verificar si el tweet tiene respuesta
        has_response = tweet.get('response_text') is not None
        
        # Badge de estado
        if tweet.get('responded', False):
            status_badge = '<span style="background-color: #4CAF50; color: white; padding: 3px 8px; border-radius: 12px; font-size: 12px;">Respondido</span>'
        elif has_response:
            status_badge = '<span style="background-color: #2196F3; color: white; padding: 3px 8px; border-radius: 12px; font-size: 12px;">Procesado</span>'
        else:
            status_badge = '<span style="background-color: #9E9E9E; color: white; padding: 3px 8px; border-radius: 12px; font-size: 12px;">Ignorado</span>'
        
        # Formatear info de sentimiento
        sentiment_html = ""
        if "sentiment" in tweet and tweet["sentiment"]:
            sentiment = tweet["sentiment"]
            sentiment_label = sentiment.get("label", "desconocido")
            sentiment_score = sentiment.get("sentiment_score", 0)
            
            # Color según sentimiento
            if sentiment_label == "positive":
                sentiment_color = "#4CAF50"  # Verde
            elif sentiment_label == "negative":
                sentiment_color = "#F44336"  # Rojo
            else:
                sentiment_color = "#9E9E9E"  # Gris
                
            sentiment_html = f"""
            <div style="margin-top: 10px; font-size: 14px;">
                <span style="background-color: {sentiment_color}; color: white; padding: 2px 6px; border-radius: 10px; font-size: 11px;">
                    Sentimiento: {sentiment_label.capitalize()}
                </span>
                <span style="margin-left: 5px; color: #555;">
                    Score: {sentiment_score:.2f}
                </span>
            </div>
            """
        
        # Formatear tweet
        tweets_html += f"""
        <div style="border: 1px solid #ddd; border-radius: 8px; padding: 15px; margin-bottom: 15px;">
            <h3 style="margin-top: 0;">Tweet #{i} {status_badge}</h3>
            <p>
                <b>De:</b> @{tweet.get('author_username', 'desconocido')}<br>
                <b>Fecha:</b> {format_date(tweet.get('processed_at', ''))}<br>
                <b>ID:</b> {tweet.get('id', 'N/A')}
            </p>
            {sentiment_html}
            
            <div style="background-color: #f8f9fa; padding: 10px; border-radius: 5px; margin-top: 10px;">
                <b>Tweet original:</b><br>
                <pre style="white-space: pre-wrap; word-break: break-word;">{tweet.get('tweet_text', 'No disponible')}</pre>
            </div>
        """
        
        # Agregar la respuesta si existe
        if has_response:
            tweets_html += f"""
            <div style="background-color: #e8f5e9; padding: 10px; border-radius: 5px; margin-top: 10px;">
                <b>Respuesta generada:</b><br>
                <pre style="white-space: pre-wrap; word-break: break-word;">{tweet.get('response_text', '')}</pre>
            </div>
            """
        
        tweets_html += "</div>"
    
    return tweets_html

def refresh_data():
    """Actualiza los datos del dashboard"""
    stats_html = get_stats_html()
    rate_limit_html = get_rate_limit_html()
    tweets_html = get_tweets_html()
    return stats_html, rate_limit_html, tweets_html

def create_dashboard():
    """Crea la interfaz del dashboard con Gradio"""
    with gr.Blocks(title="Crypto Bot Dashboard") as dashboard:
        with gr.Row():
            with gr.Column(scale=2):
                gr.HTML('<h1 style="color: #3b5998;">🤖 Dashboard de Crypto Bot para X</h1>')
            with gr.Column(scale=1):
                refresh_btn = gr.Button("🔄 Actualizar datos")
                update_info = gr.HTML('<p style="color: #666; font-size: 12px;">Actualización automática: No disponible en esta versión de Gradio</p>')
        
        with gr.Row():
            with gr.Column(scale=1):
                stats_display = gr.HTML(get_stats_html())
                rate_limit_display = gr.HTML(get_rate_limit_html())
            with gr.Column(scale=2):
                tweets_display = gr.HTML(get_tweets_html())
        
        # Manejar el refresco manual
        refresh_btn.click(
            fn=refresh_data,
            inputs=[],
            outputs=[stats_display, rate_limit_display, tweets_display]
        )
        
        # Añadir un script para refresco automático
        gr.HTML("""
        <script>
            // Recargar la página cada 30 segundos para actualización automática
            setInterval(function() {
                location.reload();
            }, 30000);
        </script>
        """)
    
    return dashboard

if __name__ == "__main__":
    dashboard = create_dashboard()
    # Lanzar el servidor sin activar la cola (queue), que es lo que causa el error
    dashboard.launch(server_name="0.0.0.0", share=False)