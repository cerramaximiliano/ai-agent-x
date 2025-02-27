import os
import sys
import time
import json
import gradio as gr
from datetime import datetime

# Agregar el directorio raíz del proyecto al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Definición manual de la clase Database para evitar dependencias
class SimpleDatabase:
    def __init__(self, db_file="data/processed_tweets.json"):
        self.db_file = db_file
    
    def _load_db(self):
        try:
            if os.path.exists(self.db_file):
                with open(self.db_file, 'r') as f:
                    return json.load(f)
            else:
                return {"processed_tweets": {}, "stats": {"total_processed": 0, "total_responded": 0}}
        except Exception as e:
            print(f"Error al leer la base de datos: {e}")
            return {"processed_tweets": {}, "stats": {"total_processed": 0, "total_responded": 0}}
    
    def get_stats(self):
        db = self._load_db()
        return db.get("stats", {"total_processed": 0, "total_responded": 0})
    
    def get_last_processed_tweets(self, limit=10):
        db = self._load_db()
        tweets = db.get("processed_tweets", {})
        
        # Convertir a lista y agregar ID como propiedad
        tweet_list = [{"id": tweet_id, **details} for tweet_id, details in tweets.items()]
        
        # Ordenar por fecha de procesamiento (descendente)
        tweet_list.sort(
            key=lambda x: x.get("processed_at", ""),
            reverse=True
        )
        
        # Retornar solo los más recientes según el límite
        return tweet_list[:limit]

def format_date(iso_date):
    """Formatea una fecha ISO a un formato más legible"""
    try:
        dt = datetime.fromisoformat(iso_date)
        return dt.strftime("%d/%m/%Y %H:%M:%S")
    except:
        return iso_date

def get_stats_html():
    """Obtiene estadísticas formateadas en HTML"""
    db = SimpleDatabase()
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
            <li><b>Total de tweets respondidos:</b> {responded}</li>
            <li><b>Tasa de respuesta:</b> {response_rate:.1f}%</li>
            <li><b>Última actualización:</b> {datetime.now().strftime("%d/%m/%Y %H:%M:%S")}</li>
        </ul>
    </div>
    """
    return stats_html

def get_tweets_html():
    """Obtiene los tweets más recientes formateados en HTML"""
    db = SimpleDatabase()
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
        
        # Formatear tweet
        tweets_html += f"""
        <div style="border: 1px solid #ddd; border-radius: 8px; padding: 15px; margin-bottom: 15px;">
            <h3 style="margin-top: 0;">Tweet #{i} {status_badge}</h3>
            <p>
                <b>De:</b> @{tweet.get('author_username', 'desconocido')}<br>
                <b>Fecha:</b> {format_date(tweet.get('processed_at', ''))}<br>
                <b>ID:</b> {tweet.get('id', 'N/A')}
            </p>
            
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
    tweets_html = get_tweets_html()
    return stats_html, tweets_html

def create_dashboard():
    """Crea la interfaz del dashboard con Gradio"""
    with gr.Blocks(title="Crypto Bot Dashboard") as dashboard:
        with gr.Row():
            with gr.Column(scale=2):
                gr.HTML('<h1 style="color: #3b5998;">🤖 Dashboard de Crypto Bot para X</h1>')
            with gr.Column(scale=1):
                refresh_btn = gr.Button("🔄 Actualizar datos")
        
        with gr.Row():
            with gr.Column(scale=1):
                stats_display = gr.HTML(get_stats_html())
            with gr.Column(scale=2):
                tweets_display = gr.HTML(get_tweets_html())
        
        # Manejar el refresco manual
        refresh_btn.click(
            fn=refresh_data,
            inputs=[],
            outputs=[stats_display, tweets_display]
        )
        
        # Actualizar cada 15 segundos
        dashboard.load(
            fn=refresh_data,
            inputs=[],
            outputs=[stats_display, tweets_display],
            every=15
        )
    
    return dashboard

if __name__ == "__main__":
    dashboard = create_dashboard()
    dashboard.launch(server_name="0.0.0.0")