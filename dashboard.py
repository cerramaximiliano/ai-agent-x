import os
import sys
import time
import threading
import gradio as gr
from datetime import datetime

# Agregar el directorio raíz del proyecto al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.database import Database

class TwitterDashboard:
    def __init__(self, refresh_interval=10, db_file="data/processed_tweets.json"):
        """
        Inicializa el dashboard de Twitter con Gradio.
        
        Args:
            refresh_interval: Intervalo de actualización en segundos
            db_file: Ruta al archivo de la base de datos
        """
        self.refresh_interval = refresh_interval
        self.db = Database(db_file=db_file)
        self.last_update = None
        self.theme = gr.themes.Soft(
            primary_hue="blue",
            secondary_hue="indigo",
        )
    
    def format_date(self, iso_date):
        """Formatea una fecha ISO a un formato más legible"""
        try:
            dt = datetime.fromisoformat(iso_date)
            return dt.strftime("%d/%m/%Y %H:%M:%S")
        except:
            return iso_date
    
    def get_stats(self):
        """Obtiene estadísticas formateadas"""
        stats = self.db.get_stats()
        processed = stats.get('total_processed', 0)
        responded = stats.get('total_responded', 0)
        
        # Calcular porcentaje de respuesta
        response_rate = (responded / processed * 100) if processed > 0 else 0
        
        stats_text = f"""
## Estadísticas del Bot

- **Total de tweets procesados:** {processed}
- **Total de tweets respondidos:** {responded}
- **Tasa de respuesta:** {response_rate:.1f}%
- **Última actualización:** {datetime.now().strftime("%d/%m/%Y %H:%M:%S")}
        """
        return stats_text
    
    def get_tweets(self):
        """Obtiene los tweets más recientes"""
        tweets = self.db.get_last_processed_tweets(limit=10)
        self.last_update = datetime.now()
        
        if not tweets:
            return "No hay tweets procesados todavía."
        
        # Formatear los tweets para mostrar en markdown
        tweets_text = "## Tweets procesados recientemente\n\n"
        
        for i, tweet in enumerate(tweets, 1):
            # Verificar si el tweet tiene respuesta
            has_response = tweet.get('response_text') is not None
            
            # Badge de estado
            status_badge = "🟢 Respondido" if tweet.get('responded', False) else "🔵 Procesado"
            if not has_response:
                status_badge = "⚪ Ignorado"
            
            # Formatear el texto del tweet
            tweets_text += f"""
### Tweet #{i} {status_badge}

**De:** @{tweet.get('author', 'desconocido')}  
**Fecha:** {self.format_date(tweet.get('processed_at', ''))}  
**ID:** {tweet.get('id', 'N/A')}

**Tweet original:**
```
{tweet.get('tweet_text', 'No disponible')}
```
"""
            
            # Agregar la respuesta si existe
            if has_response:
                tweets_text += f"""
**Respuesta generada:**
```
{tweet.get('response_text', '')}
```
"""
            
            tweets_text += "---\n"
            
        return tweets_text
    
    def refresh_data(self):
        """Actualiza los datos del dashboard"""
        stats = self.get_stats()
        tweets = self.get_tweets()
        return stats, tweets
    
    def auto_refresh(self, state):
        """Función para actualización automática"""
        while state:
            time.sleep(self.refresh_interval)
            if not state:
                break
            # Trigger manual refresh in background
            try:
                stats = self.get_stats()
                tweets = self.get_tweets()
                # Enviar actualización a la interfaz
                # Nota: Esta es una aproximación ya que Gradio no permite
                # actualizar directamente desde este hilo
                pass
            except Exception as e:
                print(f"Error en actualización automática: {e}")
    
    def launch_dashboard(self):
        """Inicia el dashboard de Gradio"""
        with gr.Blocks(title="Crypto Bot Dashboard", theme=self.theme) as dashboard:
            with gr.Row():
                with gr.Column(scale=2):
                    title = gr.Markdown("# 🤖 Dashboard de Crypto Bot para X")
                with gr.Column(scale=1):
                    auto_refresh_toggle = gr.Checkbox(label="Actualización automática", value=True)
                    refresh_button = gr.Button("🔄 Actualizar")
            
            with gr.Row():
                with gr.Column(scale=1):
                    stats_md = gr.Markdown(self.get_stats())
                    auto_refresh_info = gr.Markdown(f"_Actualizando cada {self.refresh_interval} segundos_")
                with gr.Column(scale=2):
                    tweets_md = gr.Markdown(self.get_tweets())
            
            # Manejar el refresco manual
            refresh_button.click(
                fn=self.refresh_data,
                inputs=[],
                outputs=[stats_md, tweets_md]
            )
            
            # Manejar el toggle de auto-refresh
            auto_refresh_state = [True]
            
            def toggle_auto_refresh(value):
                auto_refresh_state[0] = value
                return f"_{'Actualizando' if value else 'Actualización automática desactivada'}_"
            
            auto_refresh_toggle.change(
                fn=toggle_auto_refresh,
                inputs=[auto_refresh_toggle],
                outputs=[auto_refresh_info]
            )
            
            # Iniciar hilo de actualización automática
            refresh_thread = threading.Thread(
                target=self.auto_refresh,
                args=(auto_refresh_state,),
                daemon=True
            )
            refresh_thread.start()
        
        # Lanzar el dashboard
        dashboard.launch(
            share=True,
            server_name="0.0.0.0",
            server_port=7860,
            inbrowser=True
        )

if __name__ == "__main__":
    dashboard = TwitterDashboard(refresh_interval=10)
    dashboard.launch_dashboard()