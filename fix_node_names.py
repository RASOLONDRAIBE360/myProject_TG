import psycopg2
from backend.dbaccess.config import DB_CONFIG

def fix_names():
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        
        # Check if DEPOT exists
        cur.execute("SELECT 1 FROM noeuds WHERE id_noeud = 'DEPOT'")
        if cur.fetchone():
            print("Found DEPOT. Renaming to A...")
            
            # Check if A exists
            cur.execute("SELECT 1 FROM noeuds WHERE id_noeud = 'A'")
            if cur.fetchone():
                print("Node A already exists! Cannot rename DEPOT to A directly.")
            else:
                # Insert A
                cur.execute("INSERT INTO noeuds (id_noeud, x, y, capacite) SELECT 'A', x, y, capacite FROM noeuds WHERE id_noeud = 'DEPOT'")
                # Update edges
                cur.execute("UPDATE aretes SET u = 'A' WHERE u = 'DEPOT'")
                cur.execute("UPDATE aretes SET v = 'A' WHERE v = 'DEPOT'")
                # Delete DEPOT
                cur.execute("DELETE FROM noeuds WHERE id_noeud = 'DEPOT'")
                conn.commit()
                print("✅ Renamed DEPOT to A successfully.")
        else:
            print("DEPOT not found. Checking for A...")
            cur.execute("SELECT 1 FROM noeuds WHERE id_noeud = 'A'")
            if cur.fetchone():
                print("Node A already exists. No action needed.")
            else:
                print("Neither DEPOT nor A found. Weird.")
                
        cur.close()
        conn.close()
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    fix_names()
