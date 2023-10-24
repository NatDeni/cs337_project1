from config import config
import json
import os
import spacy
from ftfy import fix_text
import re 
from collections import Counter
import statistics


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
    top = counter.most_common(50)
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
    
    return [p[0] for p in get_people(host_words)[:config.num_hosts]]

def get_presenter():
    answers_path = os.path.join(os.curdir, "data/gg2013answers.json")
    data = load_json()
    data = [(d['text'], int(str(d['timestamp_ms'])[:-5])) for d in data]
    f = open(answers_path)
    answers = json.load(f)
    info = []
    for award in answers['award_data']:
        info.append((answers['award_data'][award]['winner'], award))
    for winner, award in info:
        pattern = re.compile(re.escape(winner), re.IGNORECASE)
        time_data = [t[1] for t in data if re.search(pattern, t[0])]
        winner_mode = statistics.mode(time_data)
        pattern = re.compile('joke', re.IGNORECASE)
        r_data = [t[0] for t in data if winner_mode - t[1] <5 and winner_mode - t[1] > 0 and re.search(pattern, t[0])]
        people = get_people(r_data)
        print(people)
        people = [p for p in people if not re.search(pattern,p[0])]
        print(f'Winner: {winner}, Award: {award}, potential hosts: {[p[0] for p in people[:5]]}')


if __name__ == "__main__":
    print(get_presenter())
    