# Fichier : controllers/dijkstra_controller.py

from flask import Blueprint, request, jsonify
import networkx as nx
from backend.services.dijkstra_service import calculate_dijkstra
from backend.services.coloring import run_coloring_algorithm

# Le préfixe /algo est défini ici [cite: 17]
dijkstra_bp = Blueprint('algo_api', __name__, url_prefix='/algo')

@dijkstra_bp.route('/dijkstra', methods=['GET'])
def run_dijkstra():
    """ GET /algo/dijkstra?src=A&dst=Z : Calcule le plus court chemin[cite: 17]. """
    id_src = request.args.get('src')
    id_dst = request.args.get('dst')

    if not id_src or not id_dst:
        return jsonify({"error": "Les paramètres 'src' et 'dst' sont requis."}), 400

    try:
        # Appel au Service
        path, distance = calculate_dijkstra(id_src, id_dst)
        
        response = {
            "path": path,
            "distance": distance,
            "message": f"Chemin trouvé de {id_src} à {id_dst}"
        }
        return jsonify(response), 200

    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except nx.NetworkXNoPath:
        return jsonify({"error": f"Aucun chemin n'existe entre {id_src} et {id_dst}."}), 404
    except Exception as e:
        return jsonify({"error": f"Erreur lors de l'exécution: {str(e)}"}), 500

@dijkstra_bp.route('/coloring', methods=['GET'])
def run_coloring():
    """ GET /algo/coloring : Exécute l'algorithme de coloriage[cite: 18]. """
    try:
        # Appel au Service
        coloring_result = run_coloring_algorithm()
        
        # Le résultat doit être converti en une liste de paires (node, color) pour JSON
        coloring_list = [{"node": node, "color": color} for node, color in coloring_result.items()]
        
        response = {
            "colors_used": len(set(coloring_result.values())),
            "assignments": coloring_list,
            "message": "Assignation couleurs/équipes effectuée."
        }
        return jsonify(response), 200
    
    except Exception as e:
        return jsonify({"error": f"Erreur lors de l'exécution du coloriage: {str(e)}"}), 500