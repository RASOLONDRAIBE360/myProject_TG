# Fichier : controllers/graph_controller.py

from flask import Blueprint, request, jsonify
from backend.models.graph_models import Noeud, Arete
from backend.services.graph_service import (
    load_graph_into_networkx,
    service_add_node,
    service_add_edge,
    service_delete_node,
    service_clear_graph
)
from backend.services.db_service import get_db_connection
import dataclasses

graph_bp = Blueprint('graph_api', __name__, url_prefix='/graph')

@graph_bp.route('', methods=['GET'])
def get_graph():
    """ GET /graph : Renvoie le graphe complet (nœuds et arêtes). """
    G = load_graph_into_networkx()

    if G is None:
        return jsonify({"error": "Erreur lors du chargement des données du graphe."}), 500

    # Reconstruction des objets à partir du graphe NetworkX pour la sérialisation
    nodes_data = []
    for n, attr in G.nodes(data=True):
        node_obj = Noeud(id_noeud=n, x=attr['x'], y=attr['y'], capacite=attr['capacite'])
        nodes_data.append(dataclasses.asdict(node_obj))

    edges_data = []
    for u, v, attr in G.edges(data=True):
        edge_obj = Arete(u=u, v=v, poids=attr['poids'])
        edges_data.append(dataclasses.asdict(edge_obj))

    response = {
        "nodes": nodes_data,
        "edges": edges_data
    }
    return jsonify(response), 200

@graph_bp.route('/node', methods=['POST'])
def add_node():
    """ POST /graph/node : Ajouter un nœud {id_noeud, x, y, capacite}. """
    try:
        data = request.get_json()
    except:
        return jsonify({"error": "Requête invalide ou Content-Type non JSON (415)."}), 415

    if not all(field in data for field in Noeud.REQUIRED_FIELDS):
        return jsonify({"error": f"Champs manquants. Doit inclure {Noeud.REQUIRED_FIELDS}."}), 400

    try:
        service_add_node(data)
        return jsonify({"message": f"Nœud '{data['id_noeud']}' ajouté."}), 201

    except ValueError as e:
        if "UniqueViolation" in str(e):
             return jsonify({"error": f"Le nœud '{data.get('id_noeud')}' existe déjà."}), 409
        if "Sommet(s) inexistant(s)" in str(e):
             return jsonify({"error": str(e)}), 404
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": f"Erreur interne: {str(e)}"}), 500

@graph_bp.route('/edge', methods=['POST'])
def add_edge():
    """ POST /graph/edge : Ajouter une arête {u, v, poids}. """
    try:
        data = request.get_json()
    except:
        return jsonify({"error": "Requête invalide ou Content-Type non JSON (415)."}), 415

    if not all(field in data for field in Arete.REQUIRED_FIELDS):
        return jsonify({"error": f"Champs manquants. Doit inclure {Arete.REQUIRED_FIELDS}."}), 400

    try:
        service_add_edge(data['u'], data['v'], data['poids'])
        return jsonify({"message": f"Arête {data['u']}-{data['v']} ajoutée."}), 201

    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"error": f"Erreur interne: {str(e)}"}), 500

@graph_bp.route('/edge', methods=['PUT'])
def update_edge():
    """ PUT /graph/edge : Modifier le poids d'une arête {u, v, poids}. """
    try:
        data = request.get_json()
    except:
        return jsonify({"error": "Requête invalide ou Content-Type non JSON (415)."}), 415

    if not all(field in data for field in ['u', 'v', 'poids']):
        return jsonify({"error": "Champs manquants. Doit inclure u, v, poids."}), 400

    try:
        # Update edge weight in database
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Update the edge (bidirectional, so update both directions if they exist)
        cursor.execute("""
            UPDATE aretes 
            SET poids = %s 
            WHERE (u = %s AND v = %s) OR (u = %s AND v = %s)
        """, (data['poids'], data['u'], data['v'], data['v'], data['u']))
        
        if cursor.rowcount == 0:
            cursor.close()
            conn.close()
            return jsonify({"error": f"Arête entre '{data['u']}' et '{data['v']}' introuvable."}), 404
        
        conn.commit()
        cursor.close()
        conn.close()
        
        # Force reload of NetworkX graph
        load_graph_into_networkx(force_reload=True)
        
        return jsonify({"message": f"Poids de l'arête {data['u']}-{data['v']} mis à jour à {data['poids']}."}), 200

    except Exception as e:
        return jsonify({"error": f"Erreur interne: {str(e)}"}), 500

@graph_bp.route('/node/<id_noeud>', methods=['DELETE'])
def delete_node(id_noeud):
    """ DELETE /graph/node/<id> : Supprimer un nœud intelligemment. """
    try:
        service_delete_node(id_noeud)
        return jsonify({"message": f"Nœud '{id_noeud}' supprimé et voisins reconnectés."}), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"error": f"Erreur interne: {str(e)}"}), 500

@graph_bp.route('/reset', methods=['DELETE'])
def reset_graph():
    """ DELETE /graph/reset : Vider le graphe. """
    try:
        service_clear_graph()
        return jsonify({"message": "Graphe réinitialisé avec succès."}), 200
    except Exception as e:
        return jsonify({"error": f"Erreur interne: {str(e)}"}), 500