# Fichier : models/graph_models.py

from dataclasses import dataclass
from typing import List

# --- Modèle de Données : Noeud ---

@dataclass
class Noeud:
    """
    Représente un point de collecte (Sommet) du graphe.
    """
    id_noeud: str         # Identifiant du nœud (clé primaire)
    x: float        # Coordonnée X
    y: float        # Coordonnée Y
    capacite: float # Capacité de collecte associée au point
    
# Champ statique pour la validation des requêtes API (Utilisé par le Contrôleur)
Noeud.REQUIRED_FIELDS = ['id_noeud', 'x', 'y', 'capacite']

# --- Modèle de Données : Arete ---

@dataclass
class Arete:
    """
    Représente une route (Arête) du graphe.
    """
    u: str        # ID du nœud source
    v: str        # ID du nœud destination
    poids: float  # Poids (distance ou temps) de l'arête
    contrainte: float = 0.0 # Contrainte (pénalité) ajoutée à l'arête

# Champ statique pour la validation des requêtes API (Utilisé par le Contrôleur)
Arete.REQUIRED_FIELDS = ['u', 'v', 'poids']