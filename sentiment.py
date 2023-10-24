import os
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
from frames import load_json
import json
import re
from frames import is_actor, is_movie
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
        winners[(answers['award_data'][award]['winner'])] = [0]
        nominees[award] = answers['award_data'][award]['nominees']
    
    for text in data:
        sentiment = sia.polarity_scores(text)
        for winner in winners.keys():
            if re.search(winner, text, re.IGNORECASE):
                winners[winner].append(sentiment['compound'])
    winners = {w: sum(winners[w])/ len(winners[w]) for w in winners.keys()}
    best_winner = max(winners, key = winners.get)
    worst_winner = min(winners, key= winners.get)
    return {"best" : best_winner, "worst": worst_winner}

