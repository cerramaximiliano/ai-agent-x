#!/usr/bin/env python
"""
Script para actualizar las estadísticas para reflejar respuestas generadas
"""

import json
import os

# Ruta al archivo de base de datos
db_file = "data/processed_tweets.json"

def update_stats():
    print(f"Actualizando estadísticas en {db_file}...")
    
    # Cargar el archivo JSON
    if not os.path.exists(db_file):
        print(f"Error: El archivo {db_file} no existe.")
        return
    
    try:
        with open(db_file, 'r') as f:
            db = json.load(f)
    except Exception as e:
        print(f"Error al leer el archivo: {e}")
        return
    
    # Obtener todos los tweets
    processed_tweets = db.get("processed_tweets", {})
    if not processed_tweets:
        print("No hay tweets procesados en la base de datos.")
        return
    
    # Contar tweets con respuestas generadas
    tweets_with_response = [
        tweet_id for tweet_id, tweet_data in processed_tweets.items() 
        if tweet_data.get("response_text") is not None
    ]
    
    # Actualizar estadísticas
    if "stats" not in db:
        db["stats"] = {}
    
    old_responded = db["stats"].get("total_responded", 0)
    db["stats"]["total_processed"] = len(processed_tweets)
    db["stats"]["total_responded"] = len(tweets_with_response)
    
    print(f"Estadísticas actualizadas:")
    print(f"  - Total tweets procesados: {len(processed_tweets)}")
    print(f"  - Total tweets con respuestas: {len(tweets_with_response)} (antes: {old_responded})")
    
    # Guardar archivo actualizado
    try:
        with open(db_file, 'w') as f:
            json.dump(db, f, indent=2)
        print("\n✅ Estadísticas actualizadas correctamente.")
    except Exception as e:
        print(f"\nError al guardar el archivo: {e}")

if __name__ == "__main__":
    update_stats()