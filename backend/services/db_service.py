# Fichier : services/db_service_access.py

import psycopg2
from psycopg2.extras import DictCursor
from backend.dbaccess.config import DB_CONFIG
from backend.models.graph_models import Noeud, Arete

# --- Connexion de base ---
def get_db_connection():
    """ Établit et retourne une connexion à la base de données. """
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except Exception as e:
        print(f"Erreur de connexion à la base de données: {e}")
        return None

# --- Fonctions DAL (Data Access Layer) ---

def db_load_graph_data():
    """ Charge tous les nœuds et arêtes. """
    conn = get_db_connection()
    if conn is None: return None
        
    try:
        cur = conn.cursor(cursor_factory=DictCursor)
        
        cur.execute("SELECT id_noeud, x, y, capacite FROM noeuds;")
        # Instanciation des objets Noeud
        nodes = [Noeud(id_noeud=row['id_noeud'], x=row['x'], y=row['y'], capacite=row['capacite']) for row in cur.fetchall()]
        
        # Chargement des arêtes avec la contrainte (si la colonne existe, sinon 0)
        cur.execute("SELECT * FROM aretes;")
        rows = cur.fetchall()
        edges = []
        for row in rows:
            contrainte = row['contrainte'] if 'contrainte' in row else 0.0
            edges.append(Arete(u=row['u'], v=row['v'], poids=row['poids'], contrainte=contrainte))
        
        cur.close()
        return {"nodes": nodes, "edges": edges}
    
    except Exception as e:
        print(f"Erreur SQL lors du chargement des données: {e}")
        return None
        
    finally:
        if conn: conn.close()

def db_insert_node(id_noeud, x, y, capacite):
    """ Insère un nœud. Lève une exception si l'ID existe déjà. """
    conn = get_db_connection()
    if conn is None: raise Exception("Connexion BD échouée.")

    try:
        cur = conn.cursor()
        query = "INSERT INTO noeuds (id_noeud, x, y, capacite) VALUES (%s, %s, %s, %s);"
        cur.execute(query, (id_noeud, x, y, capacite))
        conn.commit()
        cur.close()
    except psycopg2.errors.UniqueViolation as e:
        if conn: conn.rollback()
        raise ValueError("UniqueViolation") from e
    finally:
        if conn: conn.close()

def db_insert_edge(u, v, poids):
    """ Insère une arête (u, v). """
    conn = get_db_connection()
    if conn is None: raise Exception("Connexion BD échouée.")

    try:
        cur = conn.cursor()
        
        # 1. Vérification de l'existence des sommets
        cur.execute("SELECT id_noeud FROM noeuds WHERE id_noeud IN (%s, %s);", (u, v))
        if cur.rowcount != 2:
             raise ValueError("Sommet(s) inexistant(s).")

        # 2. Insertion de l'arête (A->B). L'unicité doit être gérée au niveau de la BD (contrainte)
        query = "INSERT INTO aretes (u, v, poids, contrainte) VALUES (%s, %s, %s, 0);"
        cur.execute(query, (u, v, poids))
        conn.commit()
        cur.close()

    except psycopg2.errors.UniqueViolation as e:
        if conn: conn.rollback()
        raise ValueError("Arête (ou son inverse) existe déjà.") from e
    
    finally:
        if conn: conn.close()

def db_delete_node(id_noeud):
    """ Supprime un nœud et ses arêtes incidentes. """
    conn = get_db_connection()
    if conn is None: raise Exception("Connexion BD échouée.")

    try:
        cur = conn.cursor()
        cur.execute("DELETE FROM aretes WHERE u = %s OR v = %s;", (id_noeud, id_noeud))
        cur.execute("DELETE FROM noeuds WHERE id_noeud = %s;", (id_noeud,))
        conn.commit()
        cur.close()
    except Exception as e:
        if conn: conn.rollback()
        raise e
    finally:
        if conn: conn.close()

def db_clear_graph():
    """ Supprime TOUTES les données du graphe (TRUNCATE). """
    conn = get_db_connection()
    if conn is None: raise Exception("Connexion BD échouée.")

    try:
        cur = conn.cursor()
        cur.execute("TRUNCATE TABLE noeuds, aretes CASCADE;")
        conn.commit()
        cur.close()
    except Exception as e:
        if conn: conn.rollback()
        raise e
    finally:
        if conn: conn.close()

def db_update_edge_constraint(u, v, contrainte):
    """ Met à jour la contrainte d'une arête (bidirectionnel). """
    conn = get_db_connection()
    if conn is None: raise Exception("Connexion BD échouée.")

    try:
        cur = conn.cursor()
        
        # Vérifier si l'arête existe dans le sens u->v
        cur.execute("SELECT 1 FROM aretes WHERE u=%s AND v=%s", (u, v))
        if cur.fetchone():
            cur.execute("UPDATE aretes SET contrainte = %s WHERE u = %s AND v = %s", (contrainte, u, v))
        else:
            # Vérifier dans l'autre sens v->u
            cur.execute("SELECT 1 FROM aretes WHERE u=%s AND v=%s", (v, u))
            if cur.fetchone():
                cur.execute("UPDATE aretes SET contrainte = %s WHERE u = %s AND v = %s", (contrainte, v, u))
            else:
                raise ValueError(f"Arête {u}<->{v} introuvable.")

        conn.commit()
        cur.close()
    except Exception as e:
        if conn: conn.rollback()
        raise e
    finally:
        if conn: conn.close()

def db_remove_all_constraints():
    """ Réinitialise toutes les contraintes à 0. """
    conn = get_db_connection()
    if conn is None: raise Exception("Connexion BD échouée.")

    try:
        cur = conn.cursor()
        cur.execute("UPDATE aretes SET contrainte = 0;")
        conn.commit()
        cur.close()
    except Exception as e:
        if conn: conn.rollback()
        raise e
    finally:
        if conn: conn.close()

def db_migrate_add_constraint_column():
    """ Migration : Ajoute la colonne contrainte à la table aretes si elle n'existe pas. """
    conn = get_db_connection()
    if conn is None: raise Exception("Connexion BD échouée.")

    try:
        cur = conn.cursor()
        cur.execute("""
            ALTER TABLE aretes 
            ADD COLUMN IF NOT EXISTS contrainte REAL DEFAULT 0;
        """)
        conn.commit()
        cur.close()
        print("✅ Migration réussie : colonne 'contrainte' ajoutée")
    except Exception as e:
        if conn: conn.rollback()
        print(f"❌ Erreur migration : {e}")
        raise e
    finally:
        if conn: conn.close()