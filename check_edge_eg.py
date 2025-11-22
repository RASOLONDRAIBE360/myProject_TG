import psycopg2
import json
from backend.dbaccess.config import DB_CONFIG

def check_edge():
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        
        # Vérifier si E-G existe
        cur.execute("SELECT u, v, poids, contrainte FROM aretes WHERE (u='E' AND v='G') OR (u='G' AND v='E')")
        result = cur.fetchall()
        
        if result:
            print(f"✅ Arête E-G trouvée: {result}")
        else:
            print("❌ Arête E-G introuvable")
            
        # Afficher toutes les arêtes avec E
        print("\nToutes les arêtes connectées à E:")
        cur.execute("SELECT u, v, poids, contrainte FROM aretes WHERE u='E' OR v='E'")
        edges = cur.fetchall()
        for edge in edges:
            print(f"  {edge[0]} -> {edge[1]} | Poids: {edge[2]} | Contrainte: {edge[3]}")
        
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Erreur: {e}")

if __name__ == "__main__":
    check_edge()
