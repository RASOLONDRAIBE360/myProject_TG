✨ Fonctionnalités

Visualisation Interactive : Affichage du graphe (Nœuds/Arêtes) en temps réel via SVG.

Gestion du Graphe (CRUD) :

  - Ajout et suppression de Points de Collecte (Nœuds).
  - Création de Routes (Arêtes) avec pondération (distance/temps).
  - Intégrité référentielle : La suppression d'un point entraîne la suppression automatique des routes connectées.
  - Algorithme de Dijkstra : Calcul et visualisation du chemin le plus court entre un point de départ (Dépôt) et une destination.
  - Algorithme de Coloriage (Graph Coloring) : Assignation automatique des jours de passage ou des équipes pour éviter les conflits entre zones adjacentes.

🏗 Architecture Technique

Le projet suit une architecture modulaire MVS (Model-View-Service) pour assurer une séparation claire des responsabilités :

  - Backend : Python 3 avec Flask.
  - Logique Graphe : Bibliothèque NetworkX.
  - Base de Données : PostgreSQL avec le pilote psycopg2.
  - Frontend : HTML5, CSS3, JavaScript (Vanilla) pour le rendu graphique.

🛠 Pré-requis

Avant de commencer, assurez-vous d'avoir installé :

  - Python 3.8+
  - PostgreSQL (avec pgAdmin 4 recommandé)
  - Git

⚙️ Installation et Configuration

1. Cloner le projet
  Bash

    git clone https://github.com/RASOLONDRAIBE360/myProject_TG.git
   
    cd myProject_TG

3. Configurer l'environnement virtuel
  Bash
    # Création
    python -m venv venv_temp
    
    # Activation (Windows)
    .\venv_temp\Scripts\activate
    
    # Activation (Mac/Linux)
    source venv_temp/bin/activate

4. Installer les dépendances
  Bash
    pip install -r requirements.txt
    (Le fichier requirements.txt doit contenir : Flask, psycopg2-binary, networkx)

🗄 Base de Données

Créez une base de données PostgreSQL nommée wastegraph_db.

Exécutez le script SQL suivant pour créer les tables avec les contraintes de cascade :
  SQL
    CREATE TABLE IF NOT EXISTS noeuds (
        id_noeud VARCHAR(50) PRIMARY KEY, 
        x REAL NOT NULL,
        y REAL NOT NULL,
        capacite INTEGER NOT NULL 
    );
    
    CREATE TABLE IF NOT EXISTS aretes (
        u VARCHAR(50) REFERENCES noeuds(id_noeud),
        v VARCHAR(50) REFERENCES noeuds(id_noeud),
        
        -- Contrainte sur le Nœud Source
        CONSTRAINT fk_u
            FOREIGN KEY (u) 
            REFERENCES noeuds(id_noeud) 
            ON DELETE CASCADE, 
        
        -- Contrainte sur le Nœud Destination
        CONSTRAINT fk_v
            FOREIGN KEY (v) 
            REFERENCES noeuds(id_noeud) 
            ON DELETE CASCADE,
        -- Poids de l'arête (distance ou temps, référence à POST /graph/edge {weight}) [cite: 5, 16]
        poids REAL NOT NULL
    );
    
Configurez vos identifiants dans le fichier dbaccess/config.py :

  Python
    DB_CONFIG = {
        "dbname": "wastegraph_db",
        "user": "postgres",        # Votre utilisateur
        "password": "votre_mot_de_passe",
        "host": "localhost"
        "port": "5432" #A adapter en fonction du port utilisé sur votre machine
    }

🚀 Démarrage

Une fois la configuration terminée, lancez le serveur :
  Bash
    python app.py
Ouvrez votre navigateur et accédez à : http://127.0.0.1:5000

👥 Auteurs

Projet réalisé dans le cadre du cours de Théorie des Graphes (UDM).
  RASOLONDRAIBE STEVY BRYAN PHILIPPE
