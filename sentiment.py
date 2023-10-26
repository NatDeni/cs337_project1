import os
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
from frames import load_json
import json
import re
from frames import is_actor, is_movie
import text2emotion
def winner_sentiment():
    nltk.download('vader_lexicon')
    sia = SentimentIntensityAnalyzer()
    answers_path = os.path.join(os.curdir, "data/gg2013answers.json")
    data = load_json()
    data = [d['text'] for d in data]
    f = open(answers_path)
    answers = json.load(f)
    hosts = answers['hosts']
    winners = {}
    nominees = {}
    for award in answers['award_data']:
        winners[(answers['award_data'][award]['winner'])] = []
        nominees[award] = answers['award_data'][award]['nominees']
    
    for winner in winners.keys:
        winner_tweets = [d for d in data if(re.search(winner, d, re.IGNORECASE))]
        emotions = get_emotions(winner_tweets)
        best_emotion = calc_max_emotion(emotions)
        polarity = get_polarity(winner_tweets)
        winners[winner] = (polarity, best_emotion)
    best_winner = max(winners, key = winners.get)
    worst_winner = min(winners, key= winners.get)
    
    return winners

def avg_emotions(emotions, key):
    emotions = [t[key] for t in emotions]
    try: # protects against no tweets found
        avg1 = sum(emotions)/len(emotions)
    except:
        return 0 
def get_emotions(data):
    emotions = [text2emotion.get_emotion(t) for t in data]
    return [avg_emotions(emotions, i) for i in ['Happy', 'Angry', 'Surprise', 'Sad', 'Fear']]

def get_polarity(data):
    sia = SentimentIntensityAnalyzer()
    scores = [sia.polarity_scores(d)['compound'] for d in data]
    try:
        avg = sum(scores)/len(scores)
    except:
        return 0
def calc_max_emotion(emotions):
    emotion_canidates = ['Happy', 'Angry', 'Surprise', 'Sad', 'Fear']
    return emotion_canidates[emotions.index(max(emotions))]
if __name__ == "__main__":
    winner_sentiment()