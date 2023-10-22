from unidecode import unidecode
from langdetect import detect
from tqdm import tqdm
import ftfy
import re
import json

def isEnglish(s):
    res = False
    try:
        res = (detect(s) == 'en')
    except: 
        res = False
    return res
    
def initial_preprocessing(data):
    # define regular expressions to remove hashtags, emojis, links, and usernames
    hashtag_pattern = re.compile(r'#\w+\s?')
    emoji_pattern = re.compile('[\U00010000-\U0010ffff]', flags=re.UNICODE)
    link_pattern = re.compile(r'http\S+')
    username_pattern = re.compile(r'@\w+\s?')
    rt_pattern = re.compile(r'RT\s')
    punctuation_pattern = re.compile(r'[^\w\s]')
    space_pattern = re.compile(r'\s+')

    data_preproc = []

    # preprocess the text field of each record
    for record in tqdm(data):
        text = record['text']
        if not isEnglish(text): continue
        text = ftfy.fix_text(text)
        text = re.sub(hashtag_pattern, '', text)
        text = re.sub(emoji_pattern, '', text)
        text = re.sub(link_pattern, '', text)
        text = re.sub(username_pattern, '', text)
        text = re.sub(rt_pattern, '', text)
        text = re.sub(punctuation_pattern, '', text)
        text = re.sub(space_pattern, ' ', text)
        text = text.replace('_', '')
        
        text = unidecode(text)
        if len(text) <= 3: continue
        record['text'] = text.lower()
        data_preproc.append(record)

    # save the preprocessed data to a new JSON file
    with open('./data/gg2013_preprocessed_01.json', 'w') as f:
        json.dump(data_preproc, f)


if __name__ == "__main__":
    # load the raw data
    with open('./data/gg2013.json') as f:
        data = json.load(f)
    initial_preprocessing(data)