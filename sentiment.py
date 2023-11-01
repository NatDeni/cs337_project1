import os
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
from frames import load_json
import json
import re
from frames import is_actor, is_movie
import text2emotion
import random

from config import config
def winner_sentiment(load = False):
    # if(load):
    #     with open(config.sentiment_path, "r") as json_file:
    #         loaded_data = json.load(json_file)
    #         return loaded_data
        
    nltk.download('vader_lexicon')
    sia = SentimentIntensityAnalyzer()
    answers_path = config.answers
    data = load_json()
    data = [d['text'] for d in data]
    
    f = open(answers_path)
    answers = json.load(f)
    winners = {}
    for award in answers['award_data']:
        winners[(answers['award_data'][award]['winner'])] = []
    winner_names = []
    for winner in winners.keys():
        winner_names.append(winner)
    escaped_strings = [re.escape(s) for s in winner_names]
    winner_filter = "|".join(escaped_strings)
    data = [d for d in data if re.search(winner_filter, d, re.IGNORECASE)]
    # emotions = get_emotions(data)
    for winner in winners.keys():
        # filter = [bool(re.search(winner, d, re.IGNORECASE)) for d in data]
        # winner_tweets = [t for t, f in zip(data, filter) if f]
        # emotions = [e for e, f in zip(emotions, filter) if f]
        print(winner)
        
        winner_tweets = random.sample([d for d in data if re.search(winner, d, re.IGNORECASE)], min(50,len([d for d in data if re.search(winner, d, re.IGNORECASE)])))
        emotion =get_emotions(winner_tweets)
        best_emotion = calc_max_emotion(emotion)
        polarity = get_polarity(winner_tweets)
        winners[winner] = (polarity, best_emotion)
        print(winners[winner])
    # file_path = config.sentiment_file
    # with open(file_path, "w") as json_file:
    #     json.dump(winners, json_file)
    return winners

def avg_emotions(emotions, key):
    emotions = [t[key] for t in emotions]
    try: # protects against no tweets found
        avg1 = sum(emotions)/len(emotions)
        return avg1
    except:
        return 0 
def get_emotions(data):
    return [text2emotion.get_emotion(t) for t in data]
    

def get_polarity(data):
    sia = SentimentIntensityAnalyzer()
    scores = [sia.polarity_scores(d)['compound'] for d in data]
    try:
        avg = sum(scores)/len(scores)
        return avg
    except:
        return 0
def calc_max_emotion(emotions):
    emotions = [avg_emotions(emotions, i) for i in ['Happy', 'Angry', 'Surprise', 'Sad', 'Fear']]
    emotion_canidates = ['Happy', 'Angry', 'Surprise', 'Sad', 'Fear']
    return emotion_canidates[emotions.index(max(emotions))]
    

if __name__ == "__main__":
    print(winner_sentiment())