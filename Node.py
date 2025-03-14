from Message import Message


class Node:
    def __init__(self, env, dht, node_id, is_connected=False):
        self.env = env
        self.dht = dht
        self.node_id = node_id
        self.left = self  # Voisin gauche (par défaut, lui-même)
        self.right = self  # Voisin droit (par défaut, lui-même)
        self.inbox = []  # File des messages reçus
        self.is_connected = is_connected
        self.env.process(self.handle_messages())



    def join(self, noeud_origine):
        """Un nouveau nœud rejoint l'anneau en trouvant sa position via un nœud existant."""
        print(f"[{self.env.now}] Nœud {self.node_id} veut s'insérer")
        self.env.process(self._process_join(noeud_origine))  # Lance le processus dans SimPy

    def _process_join(self, noeud_origine):
        """Processus SimPy pour rejoindre l'anneau sans bloquer."""
        current = noeud_origine
        while not self.is_connected:
            print(f"[{self.env.now}] Nœud {self.node_id} veut envoyer un message à {current.node_id}")
            self.send_message(current, "", join_info=True)
            

            while len(self.inbox) == 0:
                yield self.env.timeout(0.1)  # Pause dans la simulation

            msg = self.inbox.pop(0)
            voisins = msg.content
            left, current, right = voisins

            if left == right == current:  # Cas d'un seul nœud
                self.left = left
                self.right = right
                print("voisins de ",self.node_id,": sont",self.left.node_id," et ",self.right.node_id)

                self.is_connected = True

            elif left==right :#cas pour le deuxieme noeud
                if current.node_id > self.node_id :
                    self.left = left 
                    self.right = current
                else :
                    self.left = current 
                    self.right = right
                print("voisins de ",self.node_id,": sont",self.left.node_id," et ",self.right.node_id)
                self.is_connected = True

            else:
                if self.node_id > right.node_id:
                    current = right
                if self.node_id < left.node_id:
                    current = left
                else:
                    if current.node_id > self.node_id :
                        self.left = left 
                        self.right = current
                    else :
                        self.left = current 
                        self.right = right
                    print("voisins de ",self.node_id,": sont",self.left.node_id," et ",self.right.node_id)

                    self.is_connected = True

        print(f"[{self.env.now}] Nœud {self.node_id} ennvoie un message a ses voisins pour maj")
        self.send_message(left, "", voisin="gauche")
        self.send_message(right, "", voisin="droite")
        print(f"[{self.env.now}] Nœud {self.node_id} inséré entre {self.left.node_id} et {self.right.node_id}")

        self.dht.add_node_dht(self)  # Ajout dans la DHT


    def leave(self):
        """Le nœud quitte l'anneau en informant ses voisins."""
        # Ajout dans la DHT pour la visualisation
        self.left.right = self.right
        self.right.left = self.left
        self.is_connected = False
        self.dht.remove_node_dht(self)
        print(f"[{self.env.now}] Node {self.node_id} est parti.")

    def send_message(self, receiver, content, join_info = False, voisin= None):
        """Envoie un message à un nœud via le mécanisme de routage."""
        msg = Message(self, receiver, content, join_info, voisin)
        receiver.inbox.append(msg)  # Met le message dans la boîte de réception
        

    def handle_messages(self):
        """Gère les messages entrants et les transmet si nécessaire."""
        while True :
            yield self.env.timeout(0.1)
            while self.is_connected:
                yield self.env.timeout(2)  # Attente d'un délai avant de traiter le message
                while self.inbox:
                    msg = self.inbox.pop(0)  # Récupère le premier message
                    # Message pour l'arrivé de nouveau noeud
                    if msg.join_info:
                        print(f"[{self.env.now}] Nœud {self.node_id} veut envoyer un message à {msg.sender.node_id} pour lui donner ses voisins")
                        self.send_message(msg.sender,[self.left,self,self.right])
                        
                    
                    # Message pour la maj des voisins lors de l'insertion
                    elif msg.voisin is not None:
                        print("maj")
                        if msg.voisin == "gauche":
                            self.left = msg.sender
                        else:
                            self.right = msg.sender
                        
                    
                    elif self.node_id == msg.receiver:
                        # Si c'est le bon destinataire, on traite le message
                        print(f"[{self.env.now}] Nœud {self.node_id} traite le message de {msg.sender}: {msg.content}")
                    else:
                        # Si ce n'est pas le bon destinataire, on transmet au voisin suivant
                        # On regarde nos voisins dans le cas où notre destinataire se trouve de l'autre coté du cercle
                        # Cela permet d'eviter de faire tout le tour de la DHT
                        if msg.receiver.node_id == self.right.node_id :
                            print(f"[{self.env.now}] Nœud {self.node_id} transmet le message à {self.right.node_id}")
                            self.right.inbox.append(msg)
                        elif msg.receiver.node_id == self.left.node_id :
                            print(f"[{self.env.now}] Nœud {self.node_id} transmet le message à {self.left.node_id}")
                            self.left.inbox.append(msg)

                        elif self.node_id < msg.receiver.node_id:
                            print(f"[{self.env.now}] Nœud {self.node_id} transmet le message à {self.right.node_id}")
                            self.right.inbox.append(msg)  # Transmet le message au voisin suivant
                        else: 
                            print(f"[{self.env.now}] Nœud {self.node_id} transmet le message à {self.left.node_id}")
                            self.left.inbox.append(msg)  # Transmet le message au voisin suivant

        