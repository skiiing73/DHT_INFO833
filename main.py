import simpy
import random

class Node:
    def __init__(self, env, dht, node_id):
        self.env = env
        self.dht = dht
        self.node_id = node_id
        self.left = self  # Voisin gauche (par défaut, lui-même)
        self.right = self  # Voisin droit (par défaut, lui-même)
        self.process = env.process(self.run())

    def run(self):
        while True:
            yield self.env.timeout(random.uniform(5, 10))  # Simule une activité du nœud
            print(f"[{self.env.now}] Node {self.node_id} is active")

    def join(self, existing_node):
        """Un nouveau nœud rejoint l'anneau en contactant un nœud existant."""
        self.dht.add_node(self, existing_node)

    def leave(self):
        """Le nœud quitte l'anneau en informant ses voisins."""
        self.dht.remove_node(self)

class DHT:
    def __init__(self, env):
        self.env = env
        self.nodes = []

    def add_node(self, new_node, contact_node):
        """Ajoute un nœud à l'anneau."""
        self.nodes.append(new_node)
        self.nodes.sort(key=lambda n: n.node_id)  # Trie les nœuds par ID
        
        # Trouver les nouveaux voisins
        idx = self.nodes.index(new_node)
        if idx > 0:
            new_node.left = self.nodes[idx - 1]  
        else :
            self.nodes[-1]
        if idx < len(self.nodes) - 1:
            new_node.right = self.nodes[idx + 1]  
        else :
            self.nodes[0]
        
        # Mise à jour des voisins
        new_node.left.right = new_node
        new_node.right.left = new_node
        print(f"[{self.env.now}] Node {new_node.node_id} joined. Neighbors: {new_node.left.node_id}, {new_node.right.node_id}")

    def remove_node(self, node):
        """Supprime un nœud de l'anneau et met à jour les voisins."""
        if node in self.nodes:
            node.left.right = node.right
            node.right.left = node.left
            self.nodes.remove(node)
            print(f"[{self.env.now}] Node {node.node_id} left. New neighbors: {node.left.node_id}, {node.right.node_id}")

# Simulation
env = simpy.Environment()
dht = DHT(env)

# Création du premier nœud
first_node = Node(env, dht, random.randint(0, 100))
dht.nodes.append(first_node)
print(f"[{env.now}] First node {first_node.node_id} initialized")

# Ajouter des nœuds progressivement
def node_arrival(env, dht):
    while True:
        yield env.timeout(random.uniform(3, 7))  # Temps aléatoire avant un nouveau join
        new_node = Node(env, dht, random.randint(0, 100))
        new_node.join(random.choice(dht.nodes))

# Démarrer le processus d'arrivée de nœuds
env.process(node_arrival(env, dht))

# Lancer la simulation
env.run(until=50)
