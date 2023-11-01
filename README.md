## Preprocessing steps
Prior to 
### Database
### Twitter data clean up
## Extraction
In order to work with fixed files we use [config.py](https://github.com/NatDeni/cs337_project1/blob/master/config.py) file. When testing our work on different year please update namings in this file to correspond to the new names of files with answers and twitter data.  
### Hosts, awards, nominees, winners, 
In order to extract any of the categories refer to [gg_api.py](https://github.com/NatDeni/cs337_project1/blob/master/gg_api.py)
#### Additional categories: sentiment and red carpet
**Reb carpet** - In addition to regular categories we also extract 3 best and worst dressed actors. In order to extract this information please see [red_carpet.py](https://github.com/NatDeni/cs337_project1/blob/master/red_carpet.py). is_it_best_or_worst(True) will return three best dressed actors and is_it_best_or_worst(False) - worst. 
**Sentiment** - In order to see what was the most popular emotion corresponfing to each winner please use [sentiment.py](https://github.com/NatDeni/cs337_project1/blob/master/sentiment.py). Currently it randomly samples 50 tweets for each winner due to the long run time of the text2emotion library.
### Readable format
In order to generate readable format along with json for all regular and additional categories please use [save_all_outputs.py](https://github.com/NatDeni/cs337_project1/blob/master/save_all_outputs.py)