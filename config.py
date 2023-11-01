import os
from pymongo import MongoClient
conn = MongoClient('localhost', 27017)
db = conn.awards

class config:
    max_presenters = 2
    num_noms = 5         
    num_hosts = 2
    answers = os.path.join(os.curdir, "data/gg2013answers.json")
    datapath = os.path.join(os.curdir, "data/gg2013.json")
    preproc_datapath = os.path.join(os.curdir, "data/gg2013_preprocessed_03.json")
    preproc_special_datapath = os.path.join(os.curdir, "data/gg2013_preprocessed_special.json")
    award_extraction = os.path.join(os.curdir, "data/gg2013_preprocessed_special_01.json")
    json_output = os.path.join(os.curdir, "data/our_output_json.json")
    readable_output = os.path.join(os.curdir, "data/our_output_readable.txt")
    sentiment_file = os.path.join(os.curdir,"data/sentiment.json")
    actors = db.actors
    movies = db.movies