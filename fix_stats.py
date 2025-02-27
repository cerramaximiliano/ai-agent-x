import json
import os

# Ruta al archivo de base de datos
db_file = "data/processed_tweets.json"

def fix_stats():
    print(f"Corrigiendo estadísticas en {db_file}...")
    
    # Cargar el archivo JSON
    if not os.path.exists(db_file):
        print(f"Error: El archivo {db_file} no existe.")
        return
    
    try:
        with open(db_file, 'r') as f:
            db = json.load(f)
    except json.JSONDecodeError:
        print(f"Error: El archivo {db_file} no contiene JSON válido.")
        return
    except Exception as e:
        print(f"Error al leer el archivo: {e}")
        return
    
    # Contar tweets procesados y respondidos
    processed_tweets = db.get("processed_tweets", {})
    total_processed = len(processed_tweets)
    total_responded = sum(1 for t in processed_tweets.values() if t.get("responded", False))
    
    # Imprimir estadísticas actuales vs. calculadas
    current_stats = db.get("stats", {})
    print(f"Estadísticas actuales:")
    print(f"  - Total procesados: {current_stats.get('total_processed', 0)}")
    print(f"  - Total respondidos: {current_stats.get('total_responded', 0)}")
    
    print(f"\nEstadísticas calculadas:")
    print(f"  - Total procesados: {total_processed}")
    print(f"  - Total respondidos: {total_responded}")
    
    # Actualizar estadísticas
    if "stats" not in db:
        db["stats"] = {}
    
    db["stats"]["total_processed"] = total_processed
    db["stats"]["total_responded"] = total_responded
    
    # Guardar archivo actualizado
    try:
        with open(db_file, 'w') as f:
            json.dump(db, f, indent=2)
        print("\n✅ Estadísticas actualizadas correctamente.")
    except Exception as e:
        print(f"\nError al guardar el archivo: {e}")

if __name__ == "__main__":
    fix_stats()