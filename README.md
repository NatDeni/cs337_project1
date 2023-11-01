## Preprocessing steps
Prior to working with the Golden Globes data, we utilize IMDb datasets of movies and actors, which due to their large size cannot be commited to Github, therefore please download it here: https://drive.google.com/file/d/1r88BrMWtXOrIFSX-1bfiJPdjDrbhgcQH/view?usp=sharing and add the files to the dataset_data folder of the project. The data in these files has already been pre-processed by the modify_movies_data(), modify_actors_data() and assign_genders() functions located in data-manipulation.py, removing redundant information (from the original actors and movies files of IMDB found here https://datasets.imdbws.com/ respectively name.basics.tsv.gz and title.akas.tsv.gz which were converted to csv and named actors and movies.csv) on actors that died before 2005 or movies that ended production before 2000.

### Database
Having added filtered_movies.csv and filtered_actors.csv to the dataset_data folder, please run data_manipulation.py to convert the files into json format, necessary for the MongoDB connection. Once the files have been created (assuming MongoDB Compass is installed in your local machine and you have connected to MongoDB), run driver.py. The script establishes a connection with the database on the following host and port MongoClient('localhost', 27017). If this differs from your local connection, please change the string accordingly. In particular, driver.py will create an award database that contains two collections, movies and actors, in which the filtered_movies.json and filtered_actors.json files will be uploaded to.

### Twitter data clean up
We have multiple versions of the clean up twitter dataset as for different tasks we had different needs. The gg2013_preprocessed_03 - Removed punctuation, hashtags, emojis, and retweets.
The ..._special_01 -  removed retweets, emojis and all punctuation other than '-'. Kept hashtags in
The ..._special - removed everything but hashtags.

The reason for the need to have different variations of the preprocessed tweets dataset came as a result of all the team members working on the tasks in parallel with each following somewhat of a different strategy where the presence (or abstence) of certain punctuation marks was helpful for the given task.

Use tweet-dataset-preprocessing.py to generate preprocessed files. In order to repeat this process on the other year please change all the names accordingly to the year (gg2013 to ggAAAA where AAAA is a year)

## Extraction
In order to work with fixed files we use [config.py](https://github.com/NatDeni/cs337_project1/blob/master/config.py) file. When testing our work on different year please update namings in this file to correspond to the new names of files with answers and twitter data.  
### Hosts, awards, nominees, winners, 
In order to extract any of the categories refer to [gg_api.py](https://github.com/NatDeni/cs337_project1/blob/master/gg_api.py)
#### Additional categories: sentiment and red carpet
**Reb carpet** - In addition to regular categories we also extract 3 best and worst dressed actors. In order to extract this information please see [red_carpet.py](https://github.com/NatDeni/cs337_project1/blob/master/red_carpet.py). is_it_best_or_worst(True) will return three best dressed actors and is_it_best_or_worst(False) - worst. 
**Sentiment** - In order to see what was the most popular emotion corresponfing to each winner please use [sentiment.py](https://github.com/NatDeni/cs337_project1/blob/master/sentiment.py)
### Readable format
In order to generate readable format along with json for all regular and additional categories please use [save_all_outputs.py](https://github.com/NatDeni/cs337_project1/blob/master/save_all_outputs.py)