class DHT:
    def __init__(self, env):
        self.env = env
        self.nodes = []

    def add_node(self, new_node):
        """Ajoute un nœud à l'anneau."""
        self.nodes.append(new_node)
        self.nodes.sort(key=lambda n: n.node_id)  # Trie les nœuds par ID
        
        # Trouver les nouveaux voisins
        idx = self.nodes.index(new_node)
        if idx > 0:
            new_node.left = self.nodes[idx - 1]  
        else :
            new_node.left=self.nodes[-1]
        if idx < len(self.nodes) - 1:
            new_node.right = self.nodes[idx + 1]  
        else :
            new_node.right=self.nodes[0]
        
        # Mise à jour des voisins
        new_node.left.right = new_node
        new_node.right.left = new_node
        print(f"[{self.env.now}] Node {new_node.node_id} a rejoint. Ses voisins sont: {new_node.left.node_id}, {new_node.right.node_id}")

    def remove_node(self, node):
        """Supprime un nœud de l'anneau et met à jour les voisins."""
        if node in self.nodes:
            node.left.right = node.right
            node.right.left = node.left
            self.nodes.remove(node)
            print(f"[{self.env.now}] Node {node.node_id} est parti.")
        
    def print_etat_dht(self):
        """Affiche l'état de la DHT sous forme circulaire."""
        if not self.nodes:
            print("Aucun nœud dans la DHT.")
            return
        
        print("\nÉtat actuel de la DHT :")
        print("----------------------------------------------------")
        
        nodes_state = []
        first = self.nodes[0]
        current = first
        
        while True:
            nodes_state.append(f"[Nœud {current.node_id}] Données : {current.data if hasattr(current, 'data') else 'Aucune'}")
            current = current.right
            if current == first:
                break

        # Affichage circulaire des nœuds
        for i in range(len(nodes_state)):
            print(nodes_state[i], end="  <->  ")
           
            print()
        
        print("----------------------------------------------------\n")