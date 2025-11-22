# Fichier : app.py

from flask import Flask, send_from_directory
# Importe les Blueprints exposés par le backend/controllers/__init__.py
from backend.controllers import graph_bp, dijkstra_bp 

app = Flask(__name__, static_folder='frontend')

# Enregistre tous les contrôleurs
app.register_blueprint(graph_bp)       # Gère /graph/...
app.register_blueprint(dijkstra_bp)    # Gère /algo/...

@app.route('/')
def index():
    return send_from_directory('frontend', 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('frontend', path)

if __name__ == '__main__':
    # Lance le serveur en mode débogage
    app.run(debug=True)