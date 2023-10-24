import json
import spacy
import re
from config import config
from tqdm import tqdm
from collections import Counter
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
from award_categories_important_words import define_important_words, is_award_in_tweet
from nltk.corpus import wordnet as wn
import nltk

nltk.download('wordnet')
nlp = spacy.load('en_core_web_sm')
nouns = {x.name().split('.', 1)[0] for x in wn.all_synsets('n')}

name_pattern = r'[A-Z][a-z]{1,25}(?:\s+[A-Z][a-z]{1,25})*'

# movie_pattern = r'[[A-Z][a-z]{1,25}[ ]*]*'
movie_pattern = r'[A-Z][a-z]{1,25}(?:[A-Z][a-z]{1,25})*'
hash_pattern = r'#\w+'

person_award_words = ['actor', 'actress', 'director', 'supporting']

stop_words = ['golden', 'globe', 'globes',
              'best', 
              'actor', 'actress', 'director', 'supporting', 
              'score', 'song',
              'drama', 'comedy', 'musical', 'animated', 'screenplay',
              'series', 'picture', 'film', 'feature', 'movie', 'mini', 'miniseries',
              'television', 'tv', 'animated',
              'wins', 'award']
stop_wrods_split = ['is', 'by', 'a', 'to', 'if', 'for', 'of', 'no', 'yes', 'the', 'wow', 'yay', 'are', 'you', 'yeah',
                    'on', 'as']
winner_verbs = ['win', 'won', 'goes to', 'received', 'receives', 'accepted', 'accepts', 'speech']
nominees_verbs = ['']
presenters_verbs = ['presented', 'gave', 'presents']


def get_all_movies_from_db(year):
    query = {
        "startYear": {"$gte": str(year - 4), "$lte": str(year)}
    }
    movies = config.movies.find(query)
    return movies

def closest_movie_match(movie_titles, possibly_title, threshold=80):
    best_match = process.extractOne(possibly_title, movie_titles, scorer=fuzz.partial_ratio)
    return best_match


def is_good_match(match, shoud_be_person):
    if len(match) < 2: return False
    for sw in stop_words:
        if sw.lower() in match.lower():  return False 
    # for w in match.lower().split():
    #     if w not in nouns: return False
    if shoud_be_person:  
        for sw in stop_wrods_split:
            if sw.lower() in match.lower().split():  return False

    # if shouldn't but even 1 word is a person - False
    # if should and at least 1 word is a person - True
    if shoud_be_person:
        doc = nlp(match)
        for tok in doc:
            if (tok.ent_type_ == 'PERSON') == shoud_be_person: return shoud_be_person
        return False
    # if shouldn't and no words is a person - True
    # if should and no word is a person - False
    return True
 
def extract_person_ent(tweet, nlp_check=False):
    entities = []
    for match_name in re.findall(name_pattern, tweet):
        # if not is_good_match(match_name, nlp_check): continue
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

def extract_hastags(tweet):
    if 'cong' in tweet.lower(): return []
    hashtags = re.findall(hash_pattern, tweet)
    hashtags = [h[1:] for h in hashtags]
    new_hashtags = []
    for h in hashtags:
        new_hashtags.extend(re.findall(movie_pattern, h))
    split_words = [' '.join(re.sub('([a-z0-9])([A-Z])', r'\1 \2', h).split()) for h in new_hashtags]
    split_words = [s for s in split_words if 'golden' not in s.lower()]
    # split_words = [s for s in split_words if is_good_match(s)]
    return split_words


def combine_counters(counter):
    new_counter = {}
    added_counters = []
    for i, first_count in enumerate(counter):
        split_first_words = first_count.lower().split()
        if first_count in added_counters: continue
        new_counter[first_count] = counter[first_count]
        for j, second_count in enumerate(counter):
            if j <= i: continue 
            if second_count in added_counters: continue
            split_second_words = second_count.lower().split()
            for w in split_first_words:
                if w in split_second_words:
                    added_counters.append(second_count)
                    new_counter[first_count] += counter[second_count]
                    break
    return new_counter


def get_entites(year, verbose=True, important_verbs=[''], category='NOMINEES'):
    movie_titles = get_all_movies_from_db(year)
    if verbose: print("Extracted movie titles")
    
    f = open(config.preproc_special_datapath)
    data = json.load(f)
    f.close()
    if verbose: print("Extracted processed twitter data")
    
    # f = open(config.preproc_special_datapath)
    # data_orig = json.load(f)
    # f.close()
    # if verbose: print("Extracted twitter data")

    # f = open(config.award_datapath)
    f = open('./tmp.json')
    awards_data = json.load(f)
    f.close()
    if verbose: print("Extracted awards data")

    non_person = 0
    
    awards = []
    awards_words = []
    person_award = {}
    for award in awards_data['top26']:
        p_a = False
        for word in person_award_words:
            if word in award.lower(): p_a = True
        awards.append(award)
        awards_words.append(define_important_words(award))
        person_award[award] = p_a
    if verbose: print("Collected important words for awards")


    tweets = [t['text'] for t in data]
    nominees = {award: [] for award in awards}

    has_p_award = False
    has_nonp_award = False

    for tweet in tqdm(tweets, desc="Checking tweets"):
        # Check if award was mentioned, otherwise skip the tweet
        tweet_awards = []
        for award, award_words in zip(awards, awards_words):
            if is_award_in_tweet(tweet.lower(), award_words, person_award[award]):
            # if award.lower() in tweet.lower():
                tweet_awards.append([award, award_words])
                has_p_award = (has_p_award or person_award[award])
                has_nonp_award = (has_nonp_award or (not person_award[award]))
        if len(tweet_awards) < 1: continue
                
        # Check if important words mentioned in tweet, otherwise skip the tweet
        has_imp_word = None
        for word in important_verbs:
            if word in tweet.lower():  
                has_imp_word = True
                break
        if not has_imp_word: continue 
        
        non_person += 1

        if has_p_award: person_entities_tweet = extract_person_ent(tweet)
        else: person_entities_tweet = []
        if has_nonp_award: 
            # nonperson_entities_tweet = extract_non_person_ent(tweet)
            nonperson_entities_tweet = extract_hastags(tweet)
            nonperson_entities_tweet = [h for h in nonperson_entities_tweet if is_good_match(h, False)]
        else: nonperson_entities_tweet = []

        # person_entities_tweet = []
        # person_entities_tweet = [h for h in hashtags if is_good_match(h, True)]

        # person_entities_tweet = [p for p in person_entities_tweet if not 'golden' in p.lower()]
        # nonperson_entities_tweet = [p for p in nonperson_entities_tweet if not 'golden' in p.lower()]

        for [award, award_words] in tweet_awards:
            entities = []
            if person_award[award]: entities.extend(person_entities_tweet)
            else: entities.extend(nonperson_entities_tweet)

            if len(entities) > 0: nominees[award].extend(entities)
    
    if verbose: print("Collected all nominees")
    for t in tqdm(nominees, desc='Exracting close match from database'):
        counter = Counter(nominees[t]).most_common(100)
        nominees[t] = counter
        if person_award[t]:
            combined_counter = Counter()
            nominees[t] = [c for c in counter if is_good_match(c[0], True)]
            for c0, c1 in nominees[t]:
                c0 = c0.lower()
                if c0 not in combined_counter: combined_counter[c0] = 0
                combined_counter[c0] += c1
            nominees[t] = combine_counters(combined_counter)
            #remove opposite gender
            if 'actor' in t or 'actress' in t:
                gender = "male" if 'actor' in t else "female"
                query = {"$or": [
                                { "deathYear": "\\N" },
                                { "deathYear": { "$gte": str(year - 1) } }
                            ],
                            "primaryName": "James",
                            "gender": gender
                        } #primaryName
                new_count = {}
                for h in nominees[t]:
                    query["primaryName"] = h.title() 
                    if config.actors.find_one(query) is not None:
                        new_count[h] = nominees[t][h]
                nominees[t] = new_count
        else:
            nominees[t] = combine_counters(dict(counter))
            # gender = "male" if 'actor' in t else "female"
            # query = {
            #     "startYear": {"$gte": str(year - 4), "$lte": str(year)}
            # } #primaryName
            # query = {}
            # new_count = {}
            # for h in nominees[t]:
            #     query["primaryName"] = {"$regex": h, "$options": "i"}
            #     if config.actors.find_one(query) is None:
            #         new_count[h] = nominees[t][h]
            # nominees[t] = new_count
        nominees[t] = sorted(nominees[t].items(),key= lambda a: (-a[1],a[0]))
        if category == 'NOMINEES':
            nominees[t] = nominees[t][:5]
        if category == 'WINNERS':
            nominees[t] = nominees[t][:1]
        print('\n', t, '\n', nominees[t], '\n')
        print('-' * 20)
    if verbose: print("Updated nominees with closest match")
    print(non_person)


if __name__ == '__main__':
    # nomin = get_entites(2013, True, nominees_verbs, 'NOMINEES')
    winners = get_entites(2013, True, nominees_verbs, 'WINNERS')
    # get_entites(2013, True, presenters_verbs)