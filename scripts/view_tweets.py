#!/usr/bin/env python
"""
Script para visualizar los tweets procesados y almacenados en la base de datos.
Ejecutar desde la raíz del proyecto: python scripts/view_tweets.py
"""

import os
import sys
import json
from datetime import datetime

# Agregar el directorio raíz del proyecto al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.database import Database

def format_date(iso_date):
    """Formatea una fecha ISO a un formato más legible"""
    try:
        dt = datetime.fromisoformat(iso_date)
        return dt.strftime("%d/%m/%Y %H:%M:%S")
    except:
        return iso_date

def main():
    """Función principal"""
    db = Database()
    tweets = db.get_last_processed_tweets(limit=20)  # Obtener los últimos 20 tweets
    stats = db.get_stats()
    
    # Mostrar estadísticas
    print("\n===== ESTADÍSTICAS =====")
    print(f"Total de tweets procesados: {stats['total_processed']}")
    print(f"Total de tweets respondidos: {stats['total_responded']}")
    print(f"Tasa de respuesta: {(stats['total_responded']/stats['total_processed']*100) if stats['total_processed'] > 0 else 0:.1f}%")
    
    # Mostrar tweets
    print("\n===== ÚLTIMOS TWEETS PROCESADOS =====")
    
    if not tweets:
        print("No hay tweets procesados todavía.")
        return
        
    for i, tweet in enumerate(tweets, 1):
        print(f"\n----- Tweet #{i} -----")
        print(f"ID: {tweet['id']}")
        print(f"Autor: @{tweet['author']}")
        print(f"Procesado: {format_date(tweet['processed_at'])}")
        print(f"Respondido: {'✅ Sí' if tweet['responded'] else '❌ No'}")
        
        print("\nTWEET ORIGINAL:")
        print(f"{tweet['tweet_text']}")
        
        if tweet['response_text']:
            print("\nRESPUESTA GENERADA:")
            print(f"{tweet['response_text']}")
        else:
            print("\nRESPUESTA: No se generó respuesta")
        
        print("-" * 50)

if __name__ == "__main__":
    main()