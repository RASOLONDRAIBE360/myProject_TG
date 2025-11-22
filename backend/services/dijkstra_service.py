import networkx as nx
from backend.services.graph_service import load_graph_into_networkx

def calculate_dijkstra(id_src, id_dst):
    """ Exécute l'algorithme de Dijkstra[cite: 6]. """
    G = load_graph_into_networkx()
    if G is None:
        raise Exception("Graphe non disponible.")

    if id_src not in G or id_dst not in G:
        raise ValueError("Nœud source ou destination inexistant.")

    # Utilisation des mots-clés NetworkX: 'target' et 'weight'
    # On utilise 'weight' qui contient (poids + contrainte) calculé dans graph_service
    path = nx.shortest_path(G, source=id_src, target=id_dst, weight='weight')
    distance = nx.shortest_path_length(G, source=id_src, target=id_dst, weight='weight')
    
    return path, distance
