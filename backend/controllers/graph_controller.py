# Fichier : controllers/graph_controller.py

from flask import Blueprint, request, jsonify
from backend.models.graph_models import Noeud, Arete
from backend.services.graph_service import (
    load_graph_into_networkx,
    service_add_node,
    service_add_edge,
    service_delete_node,
    service_clear_graph,
    service_update_constraint,
    service_remove_all_constraints
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
        contrainte = attr.get('contrainte', 0.0)
        edge_obj = Arete(u=u, v=v, poids=attr['poids'], contrainte=contrainte)
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
        conn = get_db_connection()
        cursor = conn.cursor()
        
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
        
        load_graph_into_networkx(force_reload=True)
        
        return jsonify({"message": f"Poids de l'arête {data['u']}-{data['v']} mis à jour à {data['poids']}."}), 200

    except Exception as e:
        return jsonify({"error": f"Erreur interne: {str(e)}"}), 500

@graph_bp.route('/edge', methods=['DELETE'])
def delete_edge():
    """ DELETE /graph/edge : Supprimer une arête {u, v}. """
    try:
        data = request.get_json()
    except:
        return jsonify({"error": "Requête invalide ou Content-Type non JSON (415)."}), 415

    if not all(field in data for field in ['u', 'v']):
        return jsonify({"error": "Champs manquants. Doit inclure u, v."}), 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            DELETE FROM aretes 
            WHERE (u = %s AND v = %s) OR (u = %s AND v = %s)
        """, (data['u'], data['v'], data['v'], data['u']))
        
        if cursor.rowcount == 0:
            cursor.close()
            conn.close()
            return jsonify({"error": f"Arête entre '{data['u']}' et '{data['v']}' introuvable."}), 404
        
        conn.commit()
        cursor.close()
        conn.close()
        
        load_graph_into_networkx(force_reload=True)
        
        return jsonify({"message": f"Arête {data['u']}-{data['v']} supprimée."}), 200

    except Exception as e:
        return jsonify({"error": f"Erreur interne: {str(e)}"}), 500

@graph_bp.route('/node/<id_noeud>', methods=['PUT'])
def update_node(id_noeud):
    """ PUT /graph/node/<id> : Renommer un nœud. """
    try:
        data = request.get_json()
    except:
        return jsonify({"error": "Requête invalide."}), 415

    if 'new_id' not in data:
        return jsonify({"error": "Champ 'new_id' manquant."}), 400

    new_id = data['new_id']
    
    if not new_id or not isinstance(new_id, str):
        return jsonify({"error": "Le nouveau nom doit être une chaîne non vide."}), 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT x, y, capacite FROM noeuds WHERE id_noeud = %s", (id_noeud,))
        node_data = cursor.fetchone()
        if not node_data:
            cursor.close()
            conn.close()
            return jsonify({"error": f"Nœud '{id_noeud}' introuvable."}), 404
        
        x, y, capacite = node_data
        
        cursor.execute("SELECT id_noeud FROM noeuds WHERE id_noeud = %s", (new_id,))
        if cursor.fetchone():
            cursor.close()
            conn.close()
            return jsonify({"error": f"Le nœud '{new_id}' existe déjà."}), 409
        
        cursor.execute("""
            INSERT INTO noeuds (id_noeud, x, y, capacite) 
            VALUES (%s, %s, %s, %s)
        """, (new_id, x, y, capacite))
        
        cursor.execute("UPDATE aretes SET u = %s WHERE u = %s", (new_id, id_noeud))
        cursor.execute("UPDATE aretes SET v = %s WHERE v = %s", (new_id, id_noeud))
        cursor.execute("DELETE FROM noeuds WHERE id_noeud = %s", (id_noeud,))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        load_graph_into_networkx(force_reload=True)
        
        return jsonify({"message": f"Nœud '{id_noeud}' renommé en '{new_id}'."}), 200

    except Exception as e:
        return jsonify({"error": f"Erreur interne: {str(e)}"}), 500

@graph_bp.route('/node/<id_noeud>', methods=['DELETE'])
def delete_node(id_noeud):
    """ DELETE /graph/node/<id> : Supprimer un nœud intelligemment. """
    try:
        result = service_delete_node(id_noeud)
        
        message = f"Nœud '{id_noeud}' supprimé."
        if result['new_edges']:
            message += f"\n{len(result['new_edges'])} nouvelle(s) arête(s) créée(s) :"
        
        if result.get('incident_weights'):
            weights_str = " + ".join([f"{w:.1f}" for w in result['incident_weights']])
            message += f"\n\nTotal des distances connectées : {weights_str} = {result['total_incident_weight']:.1f}"
        
        return jsonify({
            "message": message,
            "deleted_node": result['deleted_node'],
            "neighbors": result['neighbors'],
            "new_edges": result['new_edges'],
            "incident_weights": result.get('incident_weights', []),
            "total_incident_weight": result.get('total_incident_weight', 0)
        }), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"error": f"Erreur interne: {str(e)}"}), 500

@graph_bp.route('/edge/constraint', methods=['PUT'])
def update_edge_constraint():
    """ PUT /graph/edge/constraint : Ajouter/Modifier une contrainte. """
    try:
        data = request.get_json()
    except:
        return jsonify({"error": "Requête invalide."}), 415
        
    if not all(k in data for k in ['u', 'v', 'contrainte']):
        return jsonify({"error": "Champs manquants (u, v, contrainte)."}), 400
        
    try:
        service_update_constraint(data['u'], data['v'], float(data['contrainte']))
        return jsonify({"message": "Contrainte mise à jour."}), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@graph_bp.route('/constraints', methods=['DELETE'])
def remove_all_constraints():
    """ DELETE /graph/constraints : Supprimer toutes les contraintes. """
    try:
        service_remove_all_constraints()
        return jsonify({"message": "Toutes les contraintes ont été supprimées."}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@graph_bp.route('/reset', methods=['DELETE'])
def reset_graph():
    """ DELETE /graph/reset : Vider le graphe. """
    try:
        service_clear_graph()
        return jsonify({"message": "Graphe réinitialisé avec succès."}), 200
    except Exception as e:
        return jsonify({"error": f"Erreur interne: {str(e)}"}), 500