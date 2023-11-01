from pymongo import MongoClient
import json

def create_db_and_collections(conn):
    try:
        db = conn['awards']
        collection1 = db.create_collection('actors')
        collection2 = db.create_collection('movies')

        print("Successfully created database and collections.")
        return db, collection1, collection2
    except Exception as e:
        print(f"Error: {e}")
        return None

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

    db, collection1, collection2 = create_db_and_collections(conn)

    if db is not None:
        print("Inserting actor data into MongoDB.")
        insert_actors_into_db('./database_data/filtered_actors.json', collection1)
        
        print("Inserting movie data into MongoDB.")
        insert_movies_into_db('./database_data/filtered_movies.json', collection2)
    else:
        print("Database creation failed.")

    conn.close()