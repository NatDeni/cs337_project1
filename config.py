import os
from pymongo import MongoClient
conn = MongoClient('localhost', 27017)
db = conn.awards
class config:
    max_presenters = 2
    num_noms = 5         
    num_hosts = 2
    datapath = os.path.join(os.curdir, "data/gg2013.json")
    preproc_datapath = os.path.join(os.curdir, "data/gg2013_preprocessed.json")
    actors = db.actors
    movies = db.movies                                                                                                                                                                                                                                                   