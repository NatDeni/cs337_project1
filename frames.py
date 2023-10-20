from config import config
import json
import os
import spacy
from ftfy import fix_text
import re 
from collections import Counter


def is_actor(name):
    query = {"primaryName": name}
    if config.actors.find_one(query) is not None:
        return True
    else:
        return False

def is_movie(name):
    query = {"primaryTitle": name}
    query2 = {"originalTitle": name}
    if config.actors.find_one(query) is not None or config.actors.find_one(query2) is not None:
        return True
    else:
        return False

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
           
def get_hosts():
    spacy_model = spacy.load("en_core_web_sm")   
    tweet_json_path = config.datapath

    f = open(tweet_json_path)
    data = json.load(f)
    text = [d['text'] for d in data]
    host_words = [h for h in text if re.search("host(?:s|ing|ed)?",h, re.IGNORECASE)]
    names = []
    for t in host_words:
        output = spacy_model(t)
        
        for entity in output.ents:
            
            if entity.label_ == "PERSON":
                
                names.append(entity.text)
    counter = Counter(names)
    top = counter.most_common(20)
    
    two_name = [s for s in top if len(s[0].split()) ==2 and is_actor(s[0])] # add actor check
    one_name = [s for s in top if len(s[0].split()) ==1]
    
    for name2, count in two_name:
        for name1, count1 in one_name:
            if name1 in name2:
                count+=count1
        final_list.append((name2,count))
    
    final_list = sorted(final_list, key = lambda x: -x[1])
    return final_list

    