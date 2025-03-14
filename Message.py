class Message:
    def __init__(self, sender, receiver, content, join_info=False,voisin=None):
        self.sender = sender
        self.receiver = receiver
        self.content = content
        self.join_info = join_info
        self.voisin = voisin
