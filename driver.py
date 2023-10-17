from pymongo import MongoClient
import json

#Insert JSON into MongoDB

def insert_actors_into_db(filename, collection):
    with open(filename, 'r') as file:
        data = json.load(file)

    collection.insert_many(data)
    print("Successfully inserted actor data into MongoDB.")


def insert_movies_into_db(filename, collection):
    with open(filename, 'r') as file:
        data = json.load(file)

    collection.insert_many(data)
    print("Successfully inserted movie data into MongoDB.")

if __name__ == "__main__":

    conn = MongoClient('localhost', 27017)
    db = conn.awards
    collection1 = db.actors
    collection2 = db.movies

    insert_actors_into_db('./database_data/filtered_actors.json', collection1)
    insert_movies_into_db('./database_data/filtered_movies.json', collection2)

    conn.close()