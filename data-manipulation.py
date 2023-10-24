# data manipulation only for the database information on movies and actors

import pandas as pd
import numpy as np
import csv 
import json

def modify_actors_data(filename):
    df = pd.read_csv(filename)
    print("Initial length: ", len(df))

    #  drop columns where there is no information on the movies
    filtered_df = df.dropna(subset=['knownForTitles', 'primaryProfession'])
    print("First filtering length: ", len(filtered_df)) 

    filtered_df = filtered_df.drop(filtered_df[(filtered_df['knownForTitles'] == '\\N') | (filtered_df['primaryProfession'] == '\\N')].index)
    print("Second filtering length: ", len(filtered_df))

    #collecting records where birthdates and dead dates are numeric
    numeric_df = filtered_df[(filtered_df['birthYear'].str.isnumeric()) & (filtered_df['deathYear'].str.isnumeric())]
    numeric_df = numeric_df[numeric_df['deathYear'].astype(int) < 2005]
    print(len(numeric_df))

    unknown_dates = filtered_df[(filtered_df['birthYear'] == '\\N') | (filtered_df['deathYear'] == '\\N')]
    final_df = pd.concat([numeric_df, unknown_dates], ignore_index=True)
    print("Final length: ", len(final_df))
    print(final_df)

    final_df = final_df.drop(columns=['Unnamed: 0'])
    final_df.to_csv('./database_data/filtered_actors.csv', index=False)

def assign_genders(filename):
    df = pd.read_csv(filename)

    # Use the apply method to conditionally assign genders
    df['gender'] = df['primaryProfession'].apply(lambda profession: 'male' if 'actor' in profession else ('female' if 'actress' in profession else 'unknown'))
    df.to_csv('./database_data/filtered_actors.csv', index=False)

def modify_movies_data(filename):
    df = pd.read_csv(filename)
    print("Initial length: ", len(df))

    numeric_df = df[(df['endYear'].str.isnumeric())]

    filtered_df = numeric_df[numeric_df['endYear'].astype(int) < 2000]
    print("First filtering length: ", len(filtered_df))

    unknown_dates = df[(df['endYear'] == '\\N')]
    final_df = pd.concat([filtered_df, unknown_dates], ignore_index=True)
    print("Final length: ", len(final_df))

    final_df = final_df.drop(columns=['isAdult', 'runtimeMinutes'])
    final_df.to_csv('./database_data/filtered_movies.csv', index=False)

def convert_to_json(csv_file, json_file):
    data = []
    
    with open(csv_file, mode='r', encoding='utf-8') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:
            data.append(row)


    with open(json_file, mode='w', newline='') as json_file:
        json.dump(data, json_file, indent=4)

if __name__ == "__main__":
    
    # modify_actors_data('./database_data/actors.csv')
    # modify_movies_data('./database_data/movies.csv')
    # assign_genders('./database_data/filtered_actors.csv')

    csv_file_movies = './database_data/filtered_movies.csv'
    json_file_movies = './database_data/filtered_movies.json'

    csv_file_actors = './database_data/filtered_actors.csv'
    json_file_actors = './database_data/filtered_actors.json'

    convert_to_json(csv_file_movies, json_file_movies)
    convert_to_json(csv_file_actors, json_file_actors)



