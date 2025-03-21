class Donnees:
    
    def __init__(self,id,data,owner=None):
        self.id=id
        self.data=data #tableau des données 
        self.owner=owner

    def setOwner(self,node):
        self.owner=node