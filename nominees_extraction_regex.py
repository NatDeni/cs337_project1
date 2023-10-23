import json
import spacy
import re
from config import config
from tqdm import tqdm
from collections import Counter
from frames import is_actor
from award_categories_important_words import define_important_words, is_award_in_tweet

nlp = spacy.load('en_core_web_sm')
name_pattern = r'[A-Za-z]{2,25} [A-Za-z]{2,25}'
movie_pattern = r'[[A-Z][A-z]{2,25}[ ]*]*'

person_award_words = ['actor', 'actress', 'director', 'supporting']

stop_words = ['golden', 'globe', 'globes',
              'best', 
              'actor', 'actress', 'director', 'supporting', 
              'score', 'song',
              'drama', 'comedy', 'musical', 'animated', 'screenplay',
              'series', 'picture', 'film', 'feature', 'movie', 'mini', 'miniseries',
              'television', 'tv', 'animated',
              'wins']


# def get_all_movies_from_db(year):
#     query = {"primaryName": name}
#     config.actors.find_one(query)

def is_good_match(match, shoud_be_person):
    if len(match) < 2: return False
    for sw in stop_words:
        if sw.lower() in match.lower().split():  return False   
    # for w in match.lower().split():
    #     if len(w) < 2 or len(w) > 25:  return False

    # if shouldn't but even 1 word is a person - False
    # if should and at least 1 word is a person - True
    doc = nlp(match)
    for tok in doc:
        if (tok.ent_type_ == 'PERSON') == shoud_be_person: return shoud_be_person
    # if shouldn't and no words is a person - True
    # if should and no word is a person - False
    return not shoud_be_person
 
def extract_person_ent(tweet):
    entities = []
    for match_name in re.findall(name_pattern, tweet):
        if not is_good_match(match_name, True): continue
        entities.append(match_name)
    return entities

def extract_non_person_ent(tweet):
    entities = []
    for match_movie in re.findall(movie_pattern, tweet):
        if not is_good_match(match_movie, False): continue
        entities.append(match_movie.strip())
    if len(entities) >= 1:
        return [' '.join(entities)]
    return entities

# def combine_counters(counter):

def get_nominees():
    f = open(config.preproc_datapath)
    data = json.load(f)
    f.close()

    f = open(config.award_datapath)
    awards_data = json.load(f)
    f.close()

    non_person = 0
    
    awards = []
    awards_words = []
    p_as = []
    for award in awards_data['top26']:
        person_award = False
        for word in person_award_words:
            if word in award.lower(): person_award = True
        awards.append(award)
        awards_words.append(define_important_words(award))
        p_as.append(person_award)
    # print('\n'.join([str(p_a)+'|'+str(award) + '  -  ' + str(awards_word) for award, awards_word, p_a in zip(awards, awards_words, p_as)]))
    # # print(awards_words)
    # print('----' * 4)

    tweets = [t['text'] for t in data]
    nominees = {award: [] for award in awards}

    has_p_award = False
    has_nonp_award = False

    for tweet in tqdm(tweets):
        # Check if award was mentioned, otherwise skip the tweet
        tweet_awards = []
        for award, award_words, p_a in zip(awards, awards_words, p_as):
            if is_award_in_tweet(tweet.lower(), award_words):
            # if award.lower() in tweet.lower():
                tweet_awards.append([award, award_words, p_a])
                has_p_award = (has_p_award or p_a)
                has_nonp_award = (has_nonp_award or (not p_a))
        if len(tweet_awards) < 1: continue
                
        # Check if important words mentioned in tweet, otherwise skip the tweet
        has_win_word = None
        words = ['win', 'won', 'goes to']
        words = ['']
        # words = ['present', 'presents', 'presenting', 'presented']
        for word in words:
            if word in tweet.lower():  
                has_win_word = True
                break
        if not has_win_word: continue 
        
        non_person += 1

        if has_p_award: person_entities_tweet = extract_person_ent(tweet)
        else: person_entities_tweet = []
        if has_nonp_award: nonperson_entities_tweet = extract_non_person_ent(tweet)
        else: nonperson_entities_tweet = []

        for [award, award_words, person_award] in tweet_awards:
            entities = []
            if person_award: entities.extend(person_entities_tweet)
            else: entities.extend(nonperson_entities_tweet)

            if len(entities) > 0: nominees[award].extend(entities)
    
    for t in nominees:
        counter = Counter(nominees[t])
        nominees[t] = counter
        print(t, nominees[t])
        print('-' * 20)
    print(non_person)


if __name__ == '__main__':
    get_nominees()