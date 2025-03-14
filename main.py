import simpy 
import random
from Node import Node
from DHT import DHT

# Ajouter des nœuds progressivement
def node_arrival(env, dht, noeud_origine):
    while True:
        yield env.timeout(random.uniform(10, 15))  # Temps aléatoire avant un nouveau join
        
        # Générer un identifiant unique pour le nœud
        new_node_id = random.randint(0, 100)
        while any(node.node_id == new_node_id for node in dht.nodes):  # Vérifie si l'ID existe déjà
            new_node_id = random.randint(0, 100)  # Génère un autre ID si l'ID existe déjà
        new_node = Node(env, dht, new_node_id)
        new_node.join(noeud_origine)


def node_exit(env, dht,first_node):
    while True:
        yield env.timeout(random.uniform(30,40))
        node_leaving=random.choice(dht.nodes)
        if node_leaving != first_node:
            node_leaving.leave()

# Tester l'envoi de messages
def send_test_messages(env, dht):
    while True:
        yield env.timeout(28)
        if len(dht.nodes) > 3:
            sender = random.choice(dht.nodes)
            final_destinataire = random.choice(dht.nodes)
            if sender != final_destinataire:
                sender.send_message(None,"Hello DHT!",final_destinataire=final_destinataire)
                print(f"[{env.now}] Nœud {sender.node_id} veut envoyer un message à {final_destinataire.node_id} avec le contenu suivant Hello DHT!")

#Afficher l'etat de la DHT
def afficher_DHT(env,dht):
    while True:
        yield env.timeout(50)
        dht.print_etat_dht()

env = simpy.Environment()
dht = DHT(env)

# Création du premier nœud
first_node = Node(env, dht, random.randint(0, 100),is_connected = True)
dht.nodes.append(first_node)
print(f"[{env.now}] premier node {first_node.node_id} inséré")

env.process(node_arrival(env, dht, first_node))
env.process(send_test_messages(env, dht))
env.process(node_exit(env, dht,first_node))
env.process(afficher_DHT(env,dht))
env.run(until=200)