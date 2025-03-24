import matplotlib.pyplot as plt
import numpy as np

class DHT:
    def __init__(self, env):
        self.env = env
        self.nodes = []
        self.noeud_origine = None
        self.data = []

    def setNoeudOrigine(self, noeud):
        self.noeud_origine = noeud

    def getNoeudOrigine(self):
        return self.noeud_origine

    def add_node_dht(self, new_node):
        """Ajoute un nœud à l'anneau."""
        self.nodes.append(new_node)
        self.nodes.sort(key=lambda n: n.node_id)  # Trie les nœuds par ID

    def remove_node_dht(self, node):
        """Supprime un nœud de l'anneau et met à jour les voisins."""
        self.nodes.remove(node)
        
    def print_etat_dht(self):
        """Affiche l'état de la DHT sous forme circulaire avec matplotlib."""
        if not self.nodes:
            print("Aucun nœud dans la DHT.")
            return
        
        # Récupérer les données des nœuds
        nodes_state = []
        first = self.nodes[0]
        current = first
        
        while True:
            nodes_state.append(
                f"[Nœud {current.node_id}] Données : {', '.join(str(d.id) for d in current.data) if hasattr(current, 'data') and current.data else 'Aucune'}"
            )
            current = current.right
            if current == first:
                break

        # Matplotlib - Création d'un cercle pour afficher les nœuds
        fig, ax = plt.subplots()
        ax.set_aspect('equal')
        ax.axis('off')  # Désactiver les axes
        
        # Nombre de nœuds
        num_nodes = len(self.nodes)
        
        # Calculer les positions des nœuds sur un cercle
        angles = np.linspace(0, 2 * np.pi, num_nodes, endpoint=False)
        positions = [(np.cos(angle), np.sin(angle)) for angle in angles]
        
        # Affichage des nœuds et de leurs données
        for i, (node, (x, y)) in enumerate(zip(self.nodes, positions)):
            # Placer le nœud
            ax.plot(x, y, 'bo', markersize=10)
            ax.text(x * 1.1, y * 1.1, nodes_state[i], ha='center', va='center', fontsize=8)
        
        # Relier les nœuds entre eux avec des lignes
        for i in range(num_nodes):
            next_node = (i + 1) % num_nodes  # Pour relier le dernier nœud au premier
            x1, y1 = positions[i]
            x2, y2 = positions[next_node]
            ax.plot([x1, x2], [y1, y2], 'k-', lw=1)  # Tracer une ligne noire

        plt.show()
