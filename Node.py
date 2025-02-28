from Message import Message

class Node:
    def __init__(self, env, dht, node_id):
        self.env = env
        self.dht = dht
        self.node_id = node_id
        self.left = self  # Voisin gauche (par défaut, lui-même)
        self.right = self  # Voisin droit (par défaut, lui-même)
        self.inbox = []  # File des messages reçus
        self.env.process(self.handle_messages())

    def join(self):
        """Un nouveau nœud rejoint l'anneau en contactant un nœud existant."""
        self.dht.add_node(self)

    def leave(self):
        """Le nœud quitte l'anneau en informant ses voisins."""
        self.dht.remove_node(self)

    def send_message(self, target_id, content):
        """Envoie un message à un nœud via le mécanisme de routage."""
        msg = Message(self.node_id, target_id, content)
        self.inbox.append(msg)  # Met le message dans la boîte de réception
        print(f"[{self.env.now}] Nœud {self.node_id} veut envoyer un message à {target_id}")

    def handle_messages(self):
        """Gère les messages entrants et les transmet si nécessaire."""
        while True:
            yield self.env.timeout(2)  # Attente d'un délai avant de traiter le message
            while self.inbox:
                msg = self.inbox.pop(0)  # Récupère le premier message
                if self.node_id == msg.receiver:
                    # Si c'est le bon destinataire, on traite le message
                    print(f"[{self.env.now}] Nœud {self.node_id} traite le message de {msg.sender}: {msg.content}")
                else:
                    # Si ce n'est pas le bon destinataire, on transmet au voisin suivant
                    # On regarde nos voisins dans le cas où notre destinataire se trouve de l'autre coté du cercle
                    # Cela permet d'eviter de faire tout le tour de la DHT
                    if msg.receiver == self.right.node_id :
                        print(f"[{self.env.now}] Nœud {self.node_id} transmet le message à {self.right.node_id}")
                        self.right.inbox.append(msg)
                    elif msg.receiver == self.left.node_id :
                        print(f"[{self.env.now}] Nœud {self.node_id} transmet le message à {self.left.node_id}")
                        self.left.inbox.append(msg)

                    elif self.node_id < msg.receiver:
                        print(f"[{self.env.now}] Nœud {self.node_id} transmet le message à {self.right.node_id}")
                        self.right.inbox.append(msg)  # Transmet le message au voisin suivant
                    else: 
                        print(f"[{self.env.now}] Nœud {self.node_id} transmet le message à {self.left.node_id}")
                        self.left.inbox.append(msg)  # Transmet le message au voisin suivant
    