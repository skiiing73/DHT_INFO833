import simpy 
import random
from Node import Node
from DHT import DHT

# Ajouter des nœuds progressivement
def node_arrival(env, dht):
    while True:
        yield env.timeout(random.uniform(3, 7))  # Temps aléatoire avant un nouveau join
        
        # Générer un identifiant unique pour le nœud
        new_node_id = random.randint(0, 100)
        while any(node.node_id == new_node_id for node in dht.nodes):  # Vérifie si l'ID existe déjà
            new_node_id = random.randint(0, 100)  # Génère un autre ID si l'ID existe déjà
        new_node = Node(env, dht, new_node_id)
        new_node.join()


def node_exit(env, dht):
    while True:
        yield env.timeout(random.uniform(15,20))
        dht.remove_node(random.choice(dht.nodes))

# Tester l'envoi de messages
def send_test_messages(env, dht):
    while True:
        yield env.timeout(8)
        if len(dht.nodes) > 3:
            sender = random.choice(dht.nodes)
            receiver = random.choice(dht.nodes)
            if sender != receiver:
                sender.send_message(receiver.node_id, "Hello DHT!")

#Afficher l'etat de la DHT
def afficher_DHT(env,dht):
    while True:
        yield env.timeout(10)
        dht.print_etat_dht()

env = simpy.Environment()
dht = DHT(env)

# Création du premier nœud
first_node = Node(env, dht, random.randint(0, 100))
dht.nodes.append(first_node)
print(f"[{env.now}] premier node {first_node.node_id} inséré")

env.process(node_arrival(env, dht))
#env.process(send_test_messages(env, dht))
env.process(node_exit(env, dht))
env.process(afficher_DHT(env,dht))
env.run(until=100)