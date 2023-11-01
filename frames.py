from config import config
import json
import os
import spacy
from ftfy import fix_text
import re 
from collections import Counter
import statistics
from award_categories_important_words import import_awards_from_answers, is_award_in_tweet, define_important_words

spacy_model = spacy.load("en_core_web_sm")  

def is_actor(name, year):
    query = {"$or": [
                                { "deathYear": "\\N" },
                                { "deathYear": { "$gte": str(int(year) - 1) } }
                            ],
                            "primaryName": name,
                            
                        }
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



def get_people(examples,year): 
    names = []
    all_data = ' '.join(examples)
    output = spacy_model(all_data)
    for entity in output.ents:
        if entity.label_ == "PERSON":
            split = entity.text.split()
            while(len(split) > 2):
                names.append(split[0] + " " + split[1])
                split = split[2:]
            names.append(" ".join(split))
                
    
    counter = Counter(names)
    top = counter.most_common(50)
    two_name = [s for s in top if len(s[0].split()) ==2 and is_actor(s[0],year)] #Checks for first names that match a first/last name pair. Hopefully no duplicates!
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

def get_hosts(year):
    
    data = load_json()
    text = [d['text'] for d in data]
    host_words = [h for h in text if re.search("host(?:s|ing|ed)?",h, re.IGNORECASE)]
    
    return [p[0] for p in get_people(host_words, year)[:config.num_hosts]]

def get_presenter(year): 
    answers_path = config.answers
    data = load_json()
    data = [d['text'] for d in data]
    f = open(answers_path)
    answers = json.load(f)
    hosts = answers["hosts"]
    # presenter_pattern = re.compile('present|\sgave|\sgiving|\sgive|\sannounc|\sread|\sintroduc', re.IGNORECASE)
    presenter_pattern = re.compile('present|\sannounc|\sintroduc', re.IGNORECASE)
    info = []
    presenters_answer = {}
    for award in answers['award_data']:
        info.append(([answers['award_data'][award]['winner']] + \
                     answers['award_data'][award]["nominees"], award))
        presenters_answer[award] = answers['award_data'][award]['presenters'] # we use that just so that we could print it out and compare it manually with what our code returns
    
    got_presenters = {}
    for people, award in info:
        filter_text = '|\s'.join(people + hosts)
        filter = f'{filter_text}'
        filter = re.compile(filter, re.IGNORECASE)
        imp_words = define_important_words(award)
        people_words = ['actor', 'actress', 'director']
        
        isPersonAward = any([w in award.lower() for w in people_words])
        # if not isPersonAward: continue
        r_data = [t for t in data if re.search(presenter_pattern, t) and 
                  (re.search(people[0].split(' ')[0].lower(), ' '+t.lower()) or # the pattern won't be able to detect if a word is in the beginning of the string cause it has no preceeding space
                   re.search(people[0].split(' ')[-1].lower(), ' '+t.lower()) or 
                   is_award_in_tweet(t, imp_words, isPersonAward))]
        people = get_people(r_data, year)
        # print(r_data)
        # print(people)
        people = [p for p in people if not filter.search(' '+p[0])]
        print('-' * 20)
        print(presenters_answer[award])
        got_presenters[award] = [p[0] for p in people[:5]]
        print(f'Award: {award}, {isPersonAward}, potential hosts: {[p for p in people[:5]]}')
    return got_presenters

if __name__ == "__main__":
    print(get_presenter("2013"))
    