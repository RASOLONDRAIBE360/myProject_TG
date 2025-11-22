from flask import Flask, request, jsonify
import psycopg2
from psycopg2 import extras
import os

# --- Configuration de l'application Flask ---
app = Flask(__name__)

# --- Configuration de la connexion PostgreSQL ---
# Il est préférable d'utiliser des variables d'environnement pour la sécurité,
# mais pour cet exemple, nous allons les définir directement.
DB_NAME = os.environ.get("DB_NAME", "BD_TG")
DB_USER = os.environ.get("DB_USER", "postgres")
DB_PASSWORD = os.environ.get("DB_PASSWORD", "p@ssw0rd232430@l!")
DB_HOST = os.environ.get("DB_HOST", "localhost")
DB_PORT = os.environ.get("DB_PORT", "5432")

# Chaîne de connexion
CONN_STRING = f"dbname={DB_NAME} user={DB_USER} password={DB_PASSWORD} host={DB_HOST} port={DB_PORT}"

def get_db_connection():
    """
    Établit et retourne une nouvelle connexion à la base de données.
    """
    try:
        conn = psycopg2.connect(CONN_STRING)
        print("La connexion à la base de donnée a été établie avec succès.")
        return conn
    except Exception as e:
        print(f"Erreur de connexion à la base de données: {e}")
        raise


# --- Lancement du Serveur Flask ---
if __name__ == '__main__':
    print(f"Connexion DB: {DB_USER}@{DB_HOST}:{DB_PORT}/{DB_NAME}")
    get_db_connection()
    print("Démarrage du serveur Flask sur http://127.0.0.1:5000/")
    app.run(debug=True)

