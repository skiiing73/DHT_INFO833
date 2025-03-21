class DHT:
    def __init__(self, env):
        self.env = env
        self.nodes = []
        self.noeud_origine=None

    def setNoeudOrigine(self,noeud):
        self.noeud_origine=noeud

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
            nodes_state.append(
    f"[Nœud {current.node_id}] Données : {', '.join(str(d.id) for d in current.data) if hasattr(current, 'data') and current.data else 'Aucune'}"
)

            current = current.right
            if current == first:
                break

        # Affichage circulaire des nœuds
        for i in range(len(nodes_state)):
            print(nodes_state[i], end="  <->  ")
           
            print()
        
        print("----------------------------------------------------\n")