from config import config

def is_actor(name):
    #Implement with MongoDB
    return True

def is_movie(name):
    #Implement with MongoDB
    return True

def could_win(winner,award):
    return winner in award.nominees 

class award():
    def __init__(self, award) -> None:
        self.award = award
        self.nominees = []
        self.winner = None
    def addNominee(self, name):
        if(len(self.nominees) > config.num_noms):
            return
        elif(not is_actor(name)):
            return
        else:
            self.nominees.append(name)
    def set_winner(self, winner):
        if could_win(winner):
            self.winner = winner
           

        


        
    