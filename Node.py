from Message import Message
from Donnees import Donnees

from collections import deque
from typing import Optional

class Node:
    def __init__(self, env, dht, node_id, is_connected=False, is_origin=False):
        self.env = env
        self.dht = dht
        self.node_id = node_id
        self.left = self
        self.right = self
        self.inbox = deque()
        self.data = []
        self.is_connected = is_connected
        self.is_origin = is_origin
        self.env.process(self.handle_messages())

    def join(self, noeud_origine):
        """Un nouveau nœud rejoint l'anneau en trouvant sa position via un nœud existant."""
        print(f"[{self.env.now}] Nœud {self.node_id} veut s'insérer")
        self.env.process(self._process_join(noeud_origine))

    def _process_join(self, noeud_origine):
        """Processus pour rejoindre l'anneau sans bloquer."""
        current = noeud_origine
        while not self.is_connected:
            print(f"[{self.env.now}] Nœud {self.node_id} veut envoyer un message à {current.node_id} pour s'insérer dans la dht")
            self.send_message(current, "", join_info=True)

            while len(self.inbox) == 0:
                yield self.env.timeout(0.1)

            msg = self.inbox.popleft()
            voisins = msg.content
            tmp_left, current, tmp_right = voisins

            if tmp_left == tmp_right == current:
                self.left = tmp_left
                self.right = tmp_left
                self.is_connected = True
            else:
                if self.node_id > tmp_right.node_id and tmp_right.node_id > current.node_id:
                    current = tmp_right
                elif self.node_id < tmp_left.node_id and tmp_left.node_id < current.node_id:
                    current = tmp_left
                else:
                    if current.node_id > self.node_id:
                        self.left = tmp_left
                        self.right = current
                    else:
                        self.left = current
                        self.right = tmp_right
                    self.is_connected = True

        print(f"[{self.env.now}] Nœud {self.node_id} envoie un message à ses voisins pour maj")
        self.send_message(self.left, "", voisin="gauche_joining")
        self.send_message(self.right, "", voisin="droite_joining")
        print(f"[{self.env.now}] Nœud {self.node_id} inséré entre {self.left.node_id} et {self.right.node_id}")

        self.dht.add_node_dht(self)
        self.right.check_donnees()
        self.left.check_donnees()

    def leave(self):
        """Le nœud quitte l'anneau en informant ses voisins."""
        self.send_message(self.left, "", voisin="gauche_leaving")
        self.send_message(self.right, "", voisin="droite_leaving")

        self.is_connected = False
        if self.is_origin:
            self.dht.setNoeudOrigine(self.right)
            self.right.is_origin = True

        self.dht.remove_node_dht(self)
        print(f"[{self.env.now}] Node {self.node_id} est parti.")
        for element in self.data:
            element.owner=self.right
        self.right.check_donnees()
        self.left.check_donnees()

    def send_message(self, receiver: Optional['Node'], content, final_destinataire: Optional['Node'] = None, join_info=False, voisin=None):
        """Envoie un message à un nœud via le mécanisme de routage."""
        if receiver is None:
            receiver = self.right if final_destinataire.node_id > self.node_id else self.left

        msg = Message(self, receiver, content, final_destinataire, join_info, voisin)
        receiver.inbox.append(msg)

    def stocker_donnees(self, tmp_data: Donnees):
        #verifie que la donnée est pas deja stocker 
        if tmp_data not in self.data:
            self.data.append(tmp_data)#ajoute la donnée

            if tmp_data.owner is None:
                #on regarde si il ya deja un owner sinon on devient le owner et on replique sur nos voisins
                tmp_data.setOwner(self)
                self.send_message(receiver=None, final_destinataire=self.right, content=tmp_data)
                self.send_message(receiver=None, final_destinataire=self.left, content=tmp_data)
            print(f"[{self.env.now}] Nœud {self.node_id} a stocké la donnée {tmp_data.id}")

    def check_donnees(self):
        for elements in self.data:
            #verifie que la data est a nous ou a un voisin proche sinon on la vire
            if elements.owner in (self.right, self.left) or elements.owner is self:
                self.data.append(elements)
        
        for elements in self.data:
            #renvoi la donnée aux voisins pour qu'il vérifie si ils l'ont
            if elements.owner is self:
                self.send_message(receiver=None, final_destinataire=self.right, content=elements)
                self.send_message(receiver=None, final_destinataire=self.left, content=elements)

    def handle_messages(self):
        """Gère les messages entrants et les transmet si nécessaire."""
        while True:
            yield self.env.timeout(1)
            while self.is_connected:
                yield self.env.timeout(2)
                while self.inbox:
                    msg = self.inbox.popleft()

                    if msg.join_info:
                        print(f"[{self.env.now}] Nœud {self.node_id} envoie un message à {msg.sender.node_id} pour lui donner ses voisins")
                        self.send_message(msg.sender, [self.left, self, self.right], None)

                    elif msg.voisin is not None:
                        self._update_neighbors(msg)

                    if isinstance(msg.content, Donnees) and msg.final_destinataire is None:
                        #insertion d'une donnée dans la dht
                        self._route_data_message(msg)

                    if msg.final_destinataire is not None:
                        #vérification de la replication des données
                        self._handle_final_destination_message(msg)

    def _update_neighbors(self, msg):
        #mets a jour les voisins du noeud
        if msg.voisin == "gauche_joining":
            self.right = msg.sender
        elif msg.voisin == "droite_joining":
            self.left = msg.sender
        elif msg.voisin == "gauche_leaving":
            self.right = msg.sender.right
        elif msg.voisin == "droite_leaving":
            self.left = msg.sender.left

    def _route_data_message(self, msg):
        #stocke la donnée si elle est sur la bon noeud sinon la route
        if msg.content.id >= self.right.node_id and self.node_id < self.right.node_id:
            self.right.inbox.append(msg)
        elif msg.content.id <= self.left.node_id and self.node_id > self.left.node_id:
            self.left.inbox.append(msg)
        else:
            self.stocker_donnees(msg.content)

    def _handle_final_destination_message(self, msg):
        #regarde si le message est pour nous et le traite 

        if isinstance(msg.content, Donnees):
            #stocke la donnée si le message en contient une
            self.stocker_donnees(msg.content)
        else:
            if self.node_id == msg.final_destinataire.node_id:
                #traitement d'un message textuel
                print(f"[{self.env.now}] Nœud {self.node_id} traite le message de {msg.sender.node_id}: {msg.content}")
            else:
                #on est pas le bon noeud alors on transfère
                self._forward_message(msg)

    def _forward_message(self, msg):
        #trasnfere les messages entre les noeuds
        if msg.final_destinataire.node_id == self.right.node_id:
            print(f"[{self.env.now}] Nœud {self.node_id} transmet le message à {self.right.node_id}")
            self.right.inbox.append(msg)
        elif msg.final_destinataire.node_id == self.left.node_id:
            print(f"[{self.env.now}] Nœud {self.node_id} transmet le message à {self.left.node_id}")
            self.left.inbox.append(msg)
        elif self.node_id < msg.final_destinataire.node_id:
            print(f"[{self.env.now}] Nœud {self.node_id} transmet le message à {self.right.node_id}")
            self.right.inbox.append(msg)
        else:
            print(f"[{self.env.now}] Nœud {self.node_id} transmet le message à {self.left.node_id}")
            self.left.inbox.append(msg)
