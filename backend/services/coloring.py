import networkx as nx
from backend.services.graph_service import load_graph_into_networkx

def run_coloring_algorithm():
    """ Exécute l'algorithme de coloriage[cite: 8]. """
    G = load_graph_into_networkx()
    if G is None:
        raise Exception("Graphe non disponible.")

    # Le coloriage est souvent une approximation dans NetworkX
    # Note: L'algorithme de coloration est un exemple de logique métier
    coloring = nx.coloring.greedy_color(G, strategy="largest_first")
    
    # Le résultat est un dictionnaire {node: color_index} [cite: 18]
    return coloring