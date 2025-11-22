// --- CONFIGURATION ---
const API_BASE_URL = 'http://127.0.0.1:5000';
const SVG_NS = "http://www.w3.org/2000/svg";
const svg = document.getElementById('wastegraph-svg');

// Variables globales
let currentGraphData = { nodes: [], edges: [] };
let currentMode = 'none';
let edgeStartNode = null;

// --- FONCTION TOAST NOTIFICATION ---

function showToast(message, type = 'error') {
    const existingToast = document.querySelector('.toast');
    if (existingToast) {
        existingToast.remove();
    }

    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.textContent = message;

    document.body.appendChild(toast);

    setTimeout(() => {
        toast.remove();
    }, 30000);
}

// --- 1. GESTION DES MODES ---

function setMode(mode) {
    currentMode = mode;
    edgeStartNode = null;

    const statusEl = document.getElementById('mode-status');
    const addBtn = document.getElementById('mode-add-btn');
    const renameBtn = document.getElementById('mode-rename-btn');
    const addEdgeBtn = document.getElementById('mode-add-edge-btn');
    const deleteBtn = document.getElementById('mode-delete-btn');
    const deleteEdgeBtn = document.getElementById('mode-delete-edge-btn');
    const constraintBtn = document.getElementById('mode-constraint-btn');
    const noneBtn = document.getElementById('mode-none-btn');

    const buttons = [addBtn, renameBtn, addEdgeBtn, deleteBtn, deleteEdgeBtn, constraintBtn, noneBtn];

    buttons.forEach(btn => {
        if (btn) {
            btn.style.opacity = '0.6';
            btn.style.transform = 'scale(1)';
        }
    });

    document.querySelectorAll('.graph-node').forEach(node => {
        node.style.stroke = '';
        node.style.strokeWidth = '';
    });

    if (mode === 'add') {
        statusEl.textContent = 'Mode actuel: ➕ Ajouter Nœud (Cliquez sur le graphe)';
        statusEl.style.color = '#4caf50';
        addBtn.style.opacity = '1';
        addBtn.style.transform = 'scale(1.05)';
        svg.style.cursor = 'crosshair';
    } else if (mode === 'rename') {
        statusEl.textContent = 'Mode actuel: ✏️ Renommer Nœud (Cliquez sur un nœud)';
        statusEl.style.color = '#ff9800';
        renameBtn.style.opacity = '1';
        renameBtn.style.transform = 'scale(1.05)';
        svg.style.cursor = 'pointer';
    } else if (mode === 'addEdge') {
        statusEl.textContent = 'Mode actuel: 🔗 Ajouter Arête (Cliquez sur 2 nœuds)';
        statusEl.style.color = '#2196F3';
        addEdgeBtn.style.opacity = '1';
        addEdgeBtn.style.transform = 'scale(1.05)';
        svg.style.cursor = 'pointer';
    } else if (mode === 'delete') {
        statusEl.textContent = 'Mode actuel: ❌ Supprimer Nœud (Cliquez sur un nœud)';
        statusEl.style.color = '#d32f2f';
        deleteBtn.style.opacity = '1';
        deleteBtn.style.transform = 'scale(1.05)';
        svg.style.cursor = 'pointer';
    } else if (mode === 'deleteEdge') {
        statusEl.textContent = 'Mode actuel: ❌ Supprimer Arête (Cliquez sur une arête)';
        statusEl.style.color = '#d32f2f';
        deleteEdgeBtn.style.opacity = '1';
        deleteEdgeBtn.style.transform = 'scale(1.05)';
        svg.style.cursor = 'pointer';
    } else if (mode === 'addConstraint') {
        statusEl.textContent = 'Mode actuel: ⚠️ Ajouter Contrainte (Cliquez sur une arête)';
        statusEl.style.color = '#ff5722';
        constraintBtn.style.opacity = '1';
        constraintBtn.style.transform = 'scale(1.05)';
        svg.style.cursor = 'pointer';
    } else {
        statusEl.textContent = 'Mode actuel: 🚫 Aucun';
        statusEl.style.color = '#666';
        noneBtn.style.opacity = '1';
        noneBtn.style.transform = 'scale(1.05)';
        svg.style.cursor = 'default';

        document.querySelectorAll('.graph-edge').forEach(line => {
            line.classList.remove('highlighted-path');
        });

        document.querySelectorAll('.graph-node').forEach(node => {
            node.setAttribute('class', 'graph-node');
        });

        displayResults({ message: "Tous les filtres et effets visuels ont été réinitialisés." });
    }
}

// --- 2. FONCTIONS UTILITAIRES DE RENDU (SVG) ---

function clearSVG() {
    svg.innerHTML = '';
}

function drawGraph(graphData) {
    clearSVG();

    graphData.edges.forEach(edge => {
        const nodeU = graphData.nodes.find(n => n.id_noeud === edge.u);
        const nodeV = graphData.nodes.find(n => n.id_noeud === edge.v);

        if (nodeU && nodeV) {
            const line = document.createElementNS(SVG_NS, 'line');
            line.setAttribute('x1', nodeU.x);
            line.setAttribute('y1', nodeU.y);
            line.setAttribute('x2', nodeV.x);
            line.setAttribute('y2', nodeV.y);
            line.setAttribute('data-u', edge.u);
            line.setAttribute('data-v', edge.v);
            line.setAttribute('class', 'graph-edge');
            line.setAttribute('stroke', '#999');
            line.setAttribute('stroke-width', '2');
            line.style.cursor = 'pointer';

            line.addEventListener('click', (e) => {
                e.stopPropagation();
                const weight = edge.poids !== undefined ? edge.poids : edge.weight;
                const contrainte = edge.contrainte !== undefined ? edge.contrainte : 0;
                handleEdgeClick(edge.u, edge.v, weight, contrainte);
            });

            svg.appendChild(line);

            const text = document.createElementNS(SVG_NS, 'text');
            const midX = (nodeU.x + nodeV.x) / 2;
            const midY = (nodeU.y + nodeV.y) / 2;
            text.setAttribute('x', midX);
            text.setAttribute('y', midY - 5);
            text.setAttribute('text-anchor', 'middle');

            const weight = edge.poids !== undefined ? edge.poids : edge.weight;
            const contrainte = edge.contrainte !== undefined ? edge.contrainte : 0;

            if (contrainte > 0) {
                const tspanWeight = document.createElementNS(SVG_NS, 'tspan');
                tspanWeight.textContent = weight.toFixed(1);

                const tspanConstraint = document.createElementNS(SVG_NS, 'tspan');
                tspanConstraint.textContent = ` (+${contrainte.toFixed(1)})`;
                tspanConstraint.setAttribute('class', 'constraint-label');
                tspanConstraint.setAttribute('fill', '#d32f2f');
                tspanConstraint.setAttribute('font-weight', 'bold');

                text.appendChild(tspanWeight);
                text.appendChild(tspanConstraint);
            } else {
                text.textContent = weight.toFixed(1);
            }

            text.setAttribute('class', 'edge-label');
            text.style.cursor = 'pointer';

            text.addEventListener('click', (e) => {
                e.stopPropagation();
                handleEdgeClick(edge.u, edge.v, weight, contrainte);
            });

            svg.appendChild(text);
        }
    });

    graphData.nodes.forEach(node => {
        const circle = document.createElementNS(SVG_NS, 'circle');
        circle.setAttribute('cx', node.x);
        circle.setAttribute('cy', node.y);
        circle.setAttribute('r', 15);
        circle.setAttribute('id', `node-${node.id_noeud}`);
        circle.setAttribute('class', 'graph-node');
        circle.setAttribute('data-node-id', node.id_noeud);

        circle.addEventListener('click', (e) => handleNodeClick(e, node.id_noeud));

        svg.appendChild(circle);

        const text = document.createElementNS(SVG_NS, 'text');
        text.setAttribute('x', node.x);
        text.setAttribute('y', node.y + 3);
        text.textContent = node.id_noeud;
        text.setAttribute('text-anchor', 'middle');
        text.setAttribute('class', 'node-label');
        text.style.pointerEvents = 'none';
        svg.appendChild(text);
    });
}

function fillSelectors(nodes) {
    const selects = ['source-select', 'dest-select'];

    selects.forEach(id => {
        const el = document.getElementById(id);
        if (el) {
            el.innerHTML = '';
            nodes.forEach(node => {
                const option = document.createElement('option');
                option.value = node.id_noeud;
                option.textContent = node.id_noeud;
                el.appendChild(option);
            });
        }
    });
}

function displayResults(data) {
    const output = document.getElementById('results-output');
    output.innerHTML = '';

    if (data.error) {
        output.innerHTML = `<p style="color: red;">❌ ERREUR : ${data.error}</p>`;
        return;
    }

    if (data.path) {
        output.innerHTML = `
            <h3>Résultat Dijkstra</h3>
            <p><strong>Chemin:</strong> ${data.path.join(' → ')}</p>
            <p><strong>Distance Totale:</strong> ${data.distance.toFixed(2)} km/min</p>
        `;
    } else if (data.assignments) {
        let coloringOutput = '<h3>Résultat Coloriage</h3>';
        coloringOutput += '<ul>';
        data.assignments.forEach(assignment => {
            coloringOutput += `<li>Nœud ${assignment.node}: Couleur ${assignment.color}</li>`;
        });
        coloringOutput += '</ul>';
        output.innerHTML = coloringOutput;
    } else if (data.new_edges || data.deleted_node) {
        let deleteOutput = `<h3>✅ ${data.message}</h3>`;

        if (data.incident_weights && data.incident_weights.length > 0) {
            const weightsStr = data.incident_weights.map(w => w.toFixed(1)).join(' + ');
            deleteOutput += `<p style="font-weight: bold; color: #333; background: #e8f5e9; padding: 8px; border-radius: 4px;">
                Total des distances connectées : ${weightsStr} = ${data.total_incident_weight.toFixed(1)}
             </p>`;
        }

        if (data.new_edges && data.new_edges.length > 0) {
            deleteOutput += '<h4>Nouvelles arêtes créées (reconnexion) :</h4><ul>';
            data.new_edges.forEach(edge => {
                deleteOutput += `<li><strong>${edge.u} ↔ ${edge.v}</strong> : Distance = <span style="color: #2196F3; font-weight: bold;">${edge.poids.toFixed(1)}</span></li>`;
            });
            deleteOutput += '</ul>';
        } else if (data.new_edges) {
            deleteOutput += '<p>Aucune nouvelle arête créée (le nœud n\'avait pas assez de voisins).</p>';
        }

        output.innerHTML = deleteOutput;
    } else if (data.message) {
        output.innerHTML = `<p>✅ ${data.message}</p>`;
    }
}

// --- 3. GESTION DES CLICS ---

function handleSVGClick(event) {
    if (currentMode !== 'add') return;

    const rect = svg.getBoundingClientRect();
    const x = event.clientX - rect.left;
    const y = event.clientY - rect.top;

    const nodeId = prompt('Entrez l\'ID du nœud (ex: A, B, C):');
    if (!nodeId) return;

    const capacite = prompt('Entrez la capacité du nœud:', '10');
    if (!capacite) return;

    addNodeAtPosition(nodeId, x, y, parseFloat(capacite));
}

function handleEdgeClick(u, v, currentWeight, currentConstraint = 0) {
    if (currentMode === 'deleteEdge') {
        if (confirm(`Voulez-vous vraiment supprimer l'arête "${u}" ↔ "${v}" ?\n\nDistance actuelle: ${currentWeight.toFixed(1)}`)) {
            deleteEdgeById(u, v);
        }
    } else if (currentMode === 'addConstraint') {
        const newConstraint = prompt(`Ajouter une contrainte (pénalité) sur l'arête "${u}" ↔ "${v}".\n\nContrainte actuelle: ${currentConstraint.toFixed(1)}\nNouvelle contrainte (0 pour supprimer):`, currentConstraint.toFixed(1));

        if (newConstraint !== null && !isNaN(parseFloat(newConstraint))) {
            addConstraintToEdge(u, v, parseFloat(newConstraint));
        }
    } else {
        const newWeight = prompt(`Modifier le poids de l'arête "${u}" ↔ "${v}".\n\nPoids actuel: ${currentWeight.toFixed(1)}\nNouveau poids:`, currentWeight.toFixed(1));

        if (newWeight && !isNaN(parseFloat(newWeight))) {
            updateEdgeWeight(u, v, parseFloat(newWeight));
        }
    }
}

function handleNodeClick(event, nodeId) {
    event.stopPropagation();

    if (currentMode === 'delete') {
        if (confirm(`Voulez-vous vraiment supprimer le nœud "${nodeId}" ?\n\nSes voisins seront reconnectés intelligemment.`)) {
            deleteNodeById(nodeId);
        }
    } else if (currentMode === 'rename') {
        const newId = prompt(`Renommer le nœud "${nodeId}".\n\nNouveau nom:`, nodeId);
        if (newId && newId !== nodeId) {
            renameNode(nodeId, newId);
        }
    } else if (currentMode === 'addEdge') {
        if (!edgeStartNode) {
            edgeStartNode = nodeId;
            const nodeEl = document.getElementById(`node-${nodeId}`);
            nodeEl.style.stroke = '#2196F3';
            nodeEl.style.strokeWidth = '3';

            const statusEl = document.getElementById('mode-status');
            statusEl.textContent = `Mode actuel: 🔗 Nœud "${nodeId}" sélectionné - Cliquez sur le 2ème nœud`;
        } else {
            if (edgeStartNode === nodeId) {
                displayResults({ error: "Impossible de créer une arête vers le même nœud !" });
                return;
            }

            const weight = prompt(`Créer une arête de "${edgeStartNode}" vers "${nodeId}".\n\nEntrez la distance (ex: 5.0):`, '5.0');
            if (weight) {
                addEdgeBetweenNodes(edgeStartNode, nodeId, parseFloat(weight));
            }

            edgeStartNode = null;
            setMode('addEdge');
        }
    }
}

// --- 4. FONCTIONS LOGIQUES ---

function highlightPath(path) {
    document.querySelectorAll('.graph-edge').forEach(line => {
        line.classList.remove('highlighted-path');
    });

    if (!path || path.length < 2) return;

    for (let i = 0; i < path.length - 1; i++) {
        const u = path[i];
        const v = path[i + 1];
        const line = document.querySelector(`[data-u="${u}"][data-v="${v}"], [data-u="${v}"][data-v="${u}"]`);
        if (line) line.classList.add('highlighted-path');
    }
}

function applyColoring(assignments) {
    document.querySelectorAll('.graph-node').forEach(node => {
        node.setAttribute('class', 'graph-node');
    });

    assignments.forEach(assignment => {
        const nodeElement = document.getElementById(`node-${assignment.node}`);
        if (nodeElement) {
            const colorIndex = assignment.color % 6;
            nodeElement.classList.add(`color-${colorIndex}`);
        }
    });
}

// --- 5. APPELS API ---

async function fetchGraph(silent = false) {
    if (!silent) displayResults({ message: "Chargement..." });
    try {
        const response = await fetch(`${API_BASE_URL}/graph`);
        const data = await response.json();
        if (response.ok) {
            currentGraphData = data;
            drawGraph(data);
            fillSelectors(data.nodes);
            if (!silent) displayResults({ message: "Graphe synchronisé." });
        } else {
            displayResults({ error: data.error });
        }
    } catch (e) {
        displayResults({ error: "Erreur connexion backend." });
    }
}

async function runDijkstra() {
    const src = document.getElementById('source-select').value;
    const dst = document.getElementById('dest-select').value;

    if (!src || !dst) {
        displayResults({ error: "Veuillez sélectionner source et destination." });
        return;
    }

    try {
        const response = await fetch(`${API_BASE_URL}/algo/dijkstra?src=${src}&dst=${dst}`);
        const data = await response.json();
        displayResults(data);
        if (response.ok) highlightPath(data.path);
    } catch (e) {
        displayResults({ error: "Erreur lors du calcul." });
    }
}

async function runColoring() {
    try {
        const response = await fetch(`${API_BASE_URL}/algo/coloring`);
        const data = await response.json();
        displayResults(data);
        if (response.ok) applyColoring(data.assignments);
    } catch (e) {
        displayResults({ error: "Erreur lors du coloriage." });
    }
}

async function addNodeAtPosition(id, x, y, capacite) {
    try {
        const response = await fetch(`${API_BASE_URL}/graph/node`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ id_noeud: id, x: x, y: y, capacite: capacite })
        });
        const data = await response.json();

        if (response.ok) {
            displayResults({ message: data.message });
            fetchGraph();
            setMode('none');
        } else {
            if (response.status === 409) {
                showToast(`Le nœud "${id}" existe déjà !`, 'error');
            } else {
                displayResults({ error: data.error });
            }
        }
    } catch (e) {
        displayResults({ error: "Erreur lors de l'ajout du nœud." });
    }
}

async function addEdgeBetweenNodes(u, v, weight) {
    try {
        const response = await fetch(`${API_BASE_URL}/graph/edge`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ u: u, v: v, poids: weight })
        });
        const data = await response.json();
        displayResults(response.ok ? { message: data.message } : { error: data.error });
        if (response.ok) {
            fetchGraph();
            setMode('none');
        }
    } catch (e) {
        displayResults({ error: "Erreur lors de l'ajout de l'arête." });
    }
}

async function updateEdgeWeight(u, v, newWeight) {
    try {
        const response = await fetch(`${API_BASE_URL}/graph/edge`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ u: u, v: v, poids: newWeight })
        });
        const data = await response.json();
        displayResults(response.ok ? { message: data.message } : { error: data.error });
        if (response.ok) {
            fetchGraph();
        }
    } catch (e) {
        displayResults({ error: "Erreur lors de la modification du poids." });
    }
}

async function deleteEdgeById(u, v) {
    try {
        const response = await fetch(`${API_BASE_URL}/graph/edge`, {
            method: 'DELETE',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ u: u, v: v })
        });
        const data = await response.json();
        displayResults(response.ok ? { message: data.message } : { error: data.error });
        if (response.ok) {
            fetchGraph();
            setMode('none');
        }
    } catch (e) {
        displayResults({ error: "Erreur lors de la suppression de l'arête." });
    }
}

async function addConstraintToEdge(u, v, constraint) {
    try {
        const response = await fetch(`${API_BASE_URL}/graph/edge/constraint`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ u: u, v: v, contrainte: constraint })
        });
        const data = await response.json();
        displayResults(response.ok ? { message: data.message } : { error: data.error });
        if (response.ok) {
            fetchGraph();
            setMode('none');
        }
    } catch (e) {
        displayResults({ error: "Erreur lors de l'ajout de la contrainte." });
    }
}

async function deleteNodeById(id) {
    try {
        const response = await fetch(`${API_BASE_URL}/graph/node/${id}`, {
            method: 'DELETE'
        });
        const data = await response.json();

        if (response.ok) {
            await fetchGraph(true);
            setMode('none');
            displayResults(data);
        } else {
            displayResults(data);
        }
    } catch (e) {
        displayResults({ error: "Erreur lors de la suppression." });
    }
}

async function renameNode(oldId, newId) {
    try {
        const response = await fetch(`${API_BASE_URL}/graph/node/${oldId}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ new_id: newId })
        });
        const data = await response.json();

        if (response.ok) {
            displayResults({ message: data.message });
            fetchGraph();
            setMode('none');
        } else {
            if (response.status === 409) {
                showToast(`Le nœud "${newId}" existe déjà !`, 'error');
            } else {
                displayResults({ error: data.error });
            }
        }
    } catch (e) {
        displayResults({ error: "Erreur lors du renommage du nœud." });
    }
}

async function resetConstraints() {
    if (!confirm("Voulez-vous vraiment supprimer TOUTES les contraintes (pénalités) ?")) return;

    try {
        const response = await fetch(`${API_BASE_URL}/graph/constraints`, {
            method: 'DELETE'
        });
        const data = await response.json();
        displayResults(response.ok ? { message: data.message } : { error: data.error });
        if (response.ok) fetchGraph();
    } catch (e) {
        displayResults({ error: "Erreur lors de la suppression des contraintes." });
    }
}

async function resetGraph() {
    if (!confirm("ATTENTION : Cela va effacer TOUT le graphe. Voulez-vous continuer ?")) return;

    try {
        const response = await fetch(`${API_BASE_URL}/graph/reset`, {
            method: 'DELETE'
        });
        const data = await response.json();
        displayResults(response.ok ? { message: data.message } : { error: data.error });
        if (response.ok) fetchGraph();
    } catch (e) {
        displayResults({ error: "Erreur lors de la réinitialisation." });
    }
}

// --- 6. INITIALISATION ---

window.onload = () => {
    fetchGraph();

    document.getElementById('dijkstra-btn').addEventListener('click', runDijkstra);
    document.getElementById('coloring-btn').addEventListener('click', runColoring);
    svg.addEventListener('click', handleSVGClick);

    setMode('none');
};