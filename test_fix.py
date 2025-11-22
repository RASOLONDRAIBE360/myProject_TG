from backend.services.db_service import db_update_edge_constraint, get_db_connection
import sys

def test_update():
    print("Testing update for C -> D...")
    try:
        # Check what is in the DB first
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT u, v FROM aretes WHERE (u='C' AND v='D') OR (u='D' AND v='C')")
        rows = cur.fetchall()
        print(f"Existing edges matching C-D: {rows}")
        conn.close()

        # Try update
        db_update_edge_constraint('C', 'D', 5.0)
        print("✅ Update C->D success!")
    except Exception as e:
        print(f"❌ Update C->D failed: {e}")

    print("\nTesting update for A -> C...")
    try:
        # Check what is in the DB first
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT u, v FROM aretes WHERE (u='A' AND v='C') OR (u='C' AND v='A')")
        rows = cur.fetchall()
        print(f"Existing edges matching A-C: {rows}")
        conn.close()

        db_update_edge_constraint('A', 'C', 5.0)
        print("✅ Update A->C success!")
    except Exception as e:
        print(f"❌ Update A->C failed: {e}")

if __name__ == "__main__":
    test_update()
