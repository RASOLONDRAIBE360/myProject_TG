import psycopg2
from backend.dbaccess.config import DB_CONFIG

def inspect_edges():
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        
        print("--- NOEUDS ---")
        cur.execute("SELECT id_noeud FROM noeuds")
        nodes = cur.fetchall()
        for n in nodes:
            print(f"'{n[0]}'")

        print("\n--- ARETES ---")
        cur.execute("SELECT u, v, poids, contrainte FROM aretes")
        rows = cur.fetchall()
        
        if not rows:
            print("Aucune arête trouvée.")
        else:
            for row in rows:
                print(f"Edge: '{row[0]}' -> '{row[1]}' | Poids: {row[2]} | Contrainte: {row[3]}")
                
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Erreur: {e}")

if __name__ == "__main__":
    inspect_edges()
