# Fichier : services/graph_service.py

import networkx as nx
from backend.services.db_service import (
    db_load_graph_data, 
    db_insert_node, 
    db_insert_edge,
    db_update_edge_constraint,
    db_remove_all_constraints
)

G = None # Variable globale pour le graphe NetworkX

def load_graph_into_networkx(force_reload=False):
    """ Charge le graphe à partir de la BD et le met en cache dans G. """
    global G
    if G is not None and not force_reload:
        return G

    data = db_load_graph_data()
    if not data:
        return None

    G = nx.Graph()
    
    for node in data['nodes']:
        G.add_node(node.id_noeud, x=node.x, y=node.y, capacite=node.capacite)

    for edge in data['edges']:
        # Calcul du poids effectif (poids + contrainte)
        poids_effectif = edge.poids + edge.contrainte
        G.add_edge(edge.u, edge.v, poids=edge.poids, contrainte=edge.contrainte, weight=poids_effectif) 
        
    return G

# --- Logique métier d'ajout de données ---

def service_add_node(data):
    """ Logique d'ajout de nœud. """
    db_insert_node(data['id_noeud'], data['x'], data['y'], data['capacite'])
    load_graph_into_networkx(force_reload=True)

def service_add_edge(u, v, poids):
    """ Logique d'ajout d'arête. """
    db_insert_edge(u, v, poids)
    load_graph_into_networkx(force_reload=True)

def service_update_constraint(u, v, contrainte):
    """ Met à jour la contrainte d'une arête. """
    db_update_edge_constraint(u, v, contrainte)
    load_graph_into_networkx(force_reload=True)

def service_remove_all_constraints():
    """ Supprime toutes les contraintes. """
    db_remove_all_constraints()
    load_graph_into_networkx(force_reload=True)

def service_delete_node(id_noeud):
    """ Supprime un nœud et reconnecte ses voisins (Intelligent Delete). 
    Retourne les informations sur les arêtes créées.
    """
    G = load_graph_into_networkx()
    if G is None or id_noeud not in G:
        raise ValueError("Nœud inexistant.")

    neighbors = list(G.neighbors(id_noeud))
    
    # Créer les nouvelles arêtes
    new_edges = []
    for i in range(len(neighbors)):
        for j in range(i + 1, len(neighbors)):
            u = neighbors[i]
            v = neighbors[j]
            
            # Calcul du poids : somme des poids
            w1 = G[u][id_noeud]['poids']
            w2 = G[id_noeud][v]['poids']
            new_weight = w1 + w2
            
            new_edges.append((u, v, new_weight))

    # Calculer les poids des arêtes incidentes pour le feedback
    incident_weights = []
    for neighbor in neighbors:
        # On récupère le poids effectif (weight) qui inclut la contrainte
        w = G[id_noeud][neighbor].get('weight', G[id_noeud][neighbor]['poids'])
        incident_weights.append(w)
    
    total_incident_weight = sum(incident_weights)

    # Supprimer le nœud en BD
    from backend.services.db_service import db_delete_node
    db_delete_node(id_noeud)

    # Ajouter les nouvelles arêtes en BD
    for u, v, w in new_edges:
        try:
            service_add_edge(u, v, w)
        except ValueError:
            pass

    load_graph_into_networkx(force_reload=True)
    
    # Retourner les informations sur les arêtes créées et supprimées
    return {
        "deleted_node": id_noeud,
        "neighbors": neighbors,
        "new_edges": [{"u": u, "v": v, "poids": w} for u, v, w in new_edges],
        "incident_weights": incident_weights,
        "total_incident_weight": total_incident_weight
    }

def service_clear_graph():
    """ Vide le graphe. """
    from backend.services.db_service import db_clear_graph
    db_clear_graph()
    load_graph_into_networkx(force_reload=True)