# --- Configuration de la connexion PostgreSQL ---
# Il est préférable d'utiliser des variables d'environnement pour la sécurité,
# mais pour cet exemple, nous allons les définir directement.

DB_CONFIG = {
    "dbname": "BD_TG",  # À modifier avec le nom de votre base
    "user": "postgres",            # Votre utilisateur PostgreSQL
    "password": "p@ssw0rd232430@l!",    # Votre mot de passe
    "host": "localhost",
    "port": "5432"   
}

# --- Constantes des champs de données (CECI ÉTAIT MANQUANT) ---
# NODE_REQUIRED_FIELDS et EDGE_REQUIRED_FIELDS ont été déplacés dans les modèles (models/graph_models.py)