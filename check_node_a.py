import psycopg2
from backend.dbaccess.config import DB_CONFIG

def check_a():
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        
        print("Checking for Node A...")
        cur.execute("SELECT * FROM noeuds WHERE id_noeud = 'A'")
        print(f"Node A: {cur.fetchone()}")
        
        print("Checking for edges connected to A...")
        cur.execute("SELECT * FROM aretes WHERE u = 'A' OR v = 'A'")
        print(f"Edges: {cur.fetchall()}")
        
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_a()
