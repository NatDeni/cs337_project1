import json
import spacy
import re
from config import config
from tqdm import tqdm
from collections import Counter
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
from award_categories_important_words import define_important_words, is_award_in_tweet
# from nltk.corpus import wordnet as wn
# import nltk
# from better_profanity import profanity

# nltk.download('wordnet')
nlp = spacy.load('en_core_web_sm')
# nouns = {x.name().split('.', 1)[0] for x in wn.all_synsets('n')}

name_pattern = r'[A-Z][a-z]{1,25}(?:\s+[A-Z][a-z]{1,25})*'

# movie_pattern = r'[[A-Z][a-z]{1,25}[ ]*]*'
movie_pattern = r'[A-Z][a-z]{1,25}(?:[A-Z][a-z]{1,25})*'
hash_pattern = r'#\w+'

repeat_pattern = r'(.)\\1{3,}'

person_award_words = ['actor', 'actress', 'director', 'supporting']

stop_words = ['golden', 'globe', 'globes', 'oscar',
              'best', 
              'actor', 'actress', 'director', 'supporting', 
              'score', 'song',
              'drama', 'comedy', 'musical', 'animated', 'screenplay',
              'series', 'picture', 'film', 'feature', 'movie', 'mini', 'miniseries',
              'television', 'tv', 'animated',
              'wins', 'award']
stop_wrods_split = ['is', 'by', 'a', 'to', 'if', 'for', 'of', 'no', 'yes', 'the', 'wow', 'yay', 'are', 'you', 'yeah',
                    'on', 'as']

profanity = ['fuck']

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
    if len(match) < 2 or len(re.findall(repeat_pattern, match)) > 0: return False
    for sw in stop_words:
        if sw.lower() in match.lower():  return False 
    for sw in profanity:
        if sw.lower() in match.lower():  return False
        
    if shoud_be_person:  
        for sw in stop_wrods_split:
            if sw.lower() in match.lower().split():  return False
        
        doc = nlp(match)
        for tok in doc:
            if (tok.ent_type_ == 'PERSON') == shoud_be_person: return shoud_be_person
        return False
    
    return True
 
def extract_person_ent(tweet, nlp_check=False):
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

def extract_hastags(tweet):
    # if 'cong' not in tweet.lower(): return []
    hashtags = re.findall(hash_pattern, tweet)
    hashtags = [h[1:] for h in hashtags]
    new_hashtags = []
    for h in hashtags:
        new_hashtags.extend(re.findall(movie_pattern, h))
    split_words = new_hashtags
    # split_words = [' '.join(re.sub('([a-z0-9])([A-Z])', r'\1 \2', h).split()) for h in new_hashtags]
    split_words = [s.lower() for s in split_words if 'golden' not in s.lower()]
    split_words = [s for s in split_words if is_good_match(s, False)]
    return split_words


def combine_counters(counter):
    new_counter = {}
    added_counters = []
    for i, first_count in enumerate(counter):
        split_first_words = first_count.lower().split()
        if first_count in added_counters: continue
        new_counter[first_count] = counter[first_count]
        for j, second_count in enumerate(counter):
            if j <= i or second_count in added_counters: continue
            split_second_words = second_count.lower().split()
            for w in split_first_words:
                if w in split_second_words:
                    added_counters.append(second_count)
                    new_counter[first_count]['count'] += counter[second_count]['count']
                    new_counter[first_count]['category'] += counter[second_count]['category']
                    break
    counter = new_counter.copy()
    new_counter = {}
    added_counters = []
    for i, first_count in enumerate(counter):
        # break
        if first_count in added_counters: continue
        split_first_words = first_count.lower().replace(' ', '')
        # print('\n', split_first_words, end=' - ')
        new_counter[first_count] = counter[first_count]
        for j, second_count in enumerate(counter):
            if j <= i or second_count in added_counters: continue
            split_second_words = second_count.lower().replace(' ', '')
            # print(split_second_words, end='|')
            if split_second_words in split_first_words or split_first_words in split_second_words:
                added_counters.append(second_count)
                new_counter[first_count]['count'] += counter[second_count]['count']
                new_counter[first_count]['category'] += counter[second_count]['category']
    return new_counter


def get_entites(awards_list, year, verbose=True, category='NOMINEES'):
    year = int(year)
    important_verbs = {"NOMINEES": nominees_verbs, "WINNERS": winner_verbs}
    # if category == 'NOMINEES':
    #     important_verbs = nominees_verbs
    # if category == 'WINNERS':
    #     important_verbs = winner_verbs
        
    if verbose: print("Extracted movie titles")
    
    f = open(config.preproc_special_datapath)
    data = json.load(f)
    f.close()
    if verbose: print("Extracted processed twitter data")

    pattern_recognised = 0
    
    awards = []
    awards_words = {}
    person_award = {}
    for award in awards_list:
        p_a = False
        for word in person_award_words:
            if word in award.lower(): p_a = True
        awards.append(award)
        awards_words[award] = define_important_words(award)
        person_award[award] = p_a
    if verbose: print("Collected important words for awards")

    tweets = [t['text'] for t in data]
    nominees_winners = {award: {'NOMINEES': [], 'WINNERS': []} for award in awards}

    for tweet in tqdm(tweets, desc="Checking tweets"):
        # Check if award was mentioned, otherwise skip the tweet
        has_p_award = False
        has_nonp_award = False

        tweet_awards = []
        for award in awards:
            if is_award_in_tweet(tweet.lower(), awards_words[award], person_award[award]):
                tweet_awards.append([award, awards_words[award]])
                has_p_award = (has_p_award or person_award[award])
                has_nonp_award = (has_nonp_award or (not person_award[award]))
        if len(tweet_awards) < 1: continue
                
        # Check if important words mentioned in tweet, otherwise skip the tweet
        has_imp_word_nom = any([w in tweet.lower() for w in important_verbs['NOMINEES']])
        has_imp_word_win = any([w in tweet.lower() for w in important_verbs['WINNERS']])
        if not has_imp_word_win and not has_imp_word_nom: continue 
        
        pattern_recognised += 1

        if has_p_award: person_entities_tweet = extract_person_ent(tweet)
        else: person_entities_tweet = []
        if has_nonp_award: 
            nonperson_entities_tweet = extract_hastags(tweet)
            nonperson_entities_tweet = [h for h in nonperson_entities_tweet if is_good_match(h, False)]
        else: nonperson_entities_tweet = []
        for [award, _] in tweet_awards:
            entities = []
            if person_award[award]: entities.extend(person_entities_tweet)
            else: entities.extend(nonperson_entities_tweet)

            if len(entities) > 0: 
                if has_imp_word_nom: nominees_winners[award]['NOMINEES'].extend(entities)
                if has_imp_word_win: nominees_winners[award]['WINNERS'].extend(entities)
    
    if verbose: print("Collected all nominees")
    for t in tqdm(nominees_winners, desc='Exracting close match from database'):
        nominees_winners[t]['NOMINEES'] = Counter(nominees_winners[t]['NOMINEES']).most_common(1000)
        nominees_winners[t]['WINNERS'] = Counter(nominees_winners[t]['WINNERS']).most_common(1000)
        
        combined_counter = {}
        for c0, c1 in nominees_winners[t]['NOMINEES']:
            c0 = c0.lower()
            if c0 not in combined_counter: combined_counter[c0] = {'count': 0, 'category': 'n'}
            combined_counter[c0]['count'] += c1
        for c0, c1 in nominees_winners[t]['WINNERS']:
            c0 = c0.lower()
            if c0 not in combined_counter: combined_counter[c0] = {'count': 0, 'category': 'w'}
            else: combined_counter[c0]['category'] += 'w'
            combined_counter[c0]['count'] += c1
        combine_all = combine_counters(combined_counter)
        nominees_winners[t]['COMBINED'] = combine_all

        if person_award[t]:
            #remove opposite gender
            if 'actor' in t or 'actress' in t:
                run_query = (category == 'WINNERS')
                gender = "male" if 'actor' in t else "female"
                query = {"$or": [
                                { "deathYear": "\\N" },
                                { "deathYear": { "$gte": str(int(year) - 1) } }
                            ],
                            "primaryName": "James",
                            "gender": gender
                        } #primaryName
                new_count = {}
                for h in combine_all:
                    query["primaryName"] = h.title() 
                    if run_query and config.actors.find_one(query) is None: continue
                    new_count[h] = combine_all[h]
                nominees_winners[t]['COMBINED'] = new_count
        
        if len(nominees_winners[t]['COMBINED'].items()) > 0:
            category_winner = sorted([[tmp[0], tmp[1]['count']] 
                                    for tmp in nominees_winners[t]['COMBINED'].items() if 'w' in tmp[1]['category']],
                                    key= lambda a: (-a[1],a[0]))[:1]
            if len(category_winner) > 0:
                category_nominees = sorted([[tmp[0], tmp[1]['count']] 
                                        for tmp in nominees_winners[t]['COMBINED'].items() if tmp[0].lower() != category_winner[0][0].lower()],
                                        key= lambda a: (-a[1],a[0]))[:5]
            else:
                category_nominees = sorted([[tmp[0], tmp[1]['count']] 
                                        for tmp in nominees_winners[t]['COMBINED'].items()],
                                        key= lambda a: (-a[1],a[0]))[:5]
            # nominees[t] = sorted(nominees[t].items(),key= lambda a: (-a[1],a[0]))
            if category == 'NOMINEES':
                nominees_winners[t] = category_nominees
            if category == 'WINNERS':
                nominees_winners[t] = category_winner
            nominees_winners[t] = [n[0] for n in nominees_winners[t]]

        else:
            nominees_winners[t] = []
            # category_nominees = [[]]

        if verbose:
            if person_award[t]:continue
            print('\n', t, '\n', nominees_winners[t], '\n')
            print('-' * 20)
    if verbose: 
        print("Updated nominees with closest match")
        print("Tweets matched", pattern_recognised)
    if category == 'WINNERS':
        for key in nominees_winners:
            if len(nominees_winners[key]) > 0: nominees_winners[key] = nominees_winners[key][0]
            else: nominees_winners[key] = ''
    return nominees_winners


if __name__ == '__main__':
    f = open(config.award_datapath)
    f = open('./tmp.json')
    awards_data = json.load(f)
    f.close()

    awards_list = []
    for award in awards_data['top26']:
        awards_list.append(award)
    # nomin = get_entites(awards_list, 2013, True, 'NOMINEES')
    winners = get_entites(awards_list, 2013, True, 'NOMINEES')
    # get_entites(2013, True, presenters_verbs)