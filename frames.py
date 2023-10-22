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

def get_people(examples):
    spacy_model = spacy.load("en_core_web_sm")   
    names = []
    for t in examples:
        output = spacy_model(t)
        
        for entity in output.ents:
            
            if entity.label_ == "PERSON":
                split = entity.text.split()
                while(len(split) > 2):
                    names.append(split[0] + " " + split[1])
                    split = split[2:]
                names.append(" ".join(split))
                
    
    counter = Counter(names)
    top = counter.most_common(20)
    print(top)
    two_name = [s for s in top if len(s[0].split()) ==2 and is_actor(s[0])] #Checks for first names that match a first/last name pair. Hopefully no duplicates!
    one_name = [s for s in top if len(s[0].split()) ==1]
    final_list = []
    for name2, count in two_name:
        for name1, count1 in one_name:
            if name1 in name2:
                count+=count1
        final_list.append((name2,count))
    
    final_list = sorted(final_list, key = lambda x: -x[1])
    return final_list

def load_json(): #Need to make more efficient, don't need to open every time
    tweet_json_path = config.preproc_datapath

    f = open(tweet_json_path)
    return json.load(f)

def get_hosts():
    
    data = load_json()
    text = [d['text'] for d in data]
    host_words = [h for h in text if re.search("host(?:s|ing|ed)?",h, re.IGNORECASE)]
    
    return get_people(host_words)[:config.num_hosts]

def get_winners(awards_list): #takes in list of awards, could change later
    winners_dict = {}
    data = load_json()
    for award in awards_list:
        matches = [re.search(f'(.+?)wins.*?{re.escape(award)}', match, re.IGNORECASE).group(1) for match in data if re.search(f'(.+?)wins.*?{re.escape(award)}', match, re.IGNORECASE)]
        winners = get_people(matches)
        i=0
        while(not could_win(winners[0])):
            i+=1
        winners_dict.append(award, winners[i])
        
if __name__ == "__main__":
    print(get_hosts())
    