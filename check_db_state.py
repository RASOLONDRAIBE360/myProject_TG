import psycopg2
import json
from backend.dbaccess.config import DB_CONFIG

def check_state():
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        
        data = {"nodes": [], "edges": []}
        
        cur.execute("SELECT id_noeud FROM noeuds ORDER BY id_noeud")
        data["nodes"] = [r[0] for r in cur.fetchall()]
        
        cur.execute("SELECT u, v, poids, contrainte FROM aretes ORDER BY u, v")
        data["edges"] = [{"u": r[0], "v": r[1], "poids": r[2], "contrainte": r[3]} for r in cur.fetchall()]
        
        print(json.dumps(data, indent=2))
        
        cur.close()
        conn.close()
    except Exception as e:
        print(json.dumps({"error": str(e)}))

if __name__ == "__main__":
    check_state()
