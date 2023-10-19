from unidecode import unidecode
import ftfy
import re
import json

# load the JSON file
with open('./data/gg2013.json', 'r') as f:
    data = json.load(f)

# define regular expressions to remove hashtags, emojis, links, and usernames
hashtag_pattern = re.compile(r'#\w+\s?')
emoji_pattern = re.compile('[\U00010000-\U0010ffff]', flags=re.UNICODE)
link_pattern = re.compile(r'http\S+')
username_pattern = re.compile(r'@\w+\s?')
rt_pattern = re.compile(r'RT\s')
punctuation_pattern = re.compile(r'([^\w\s]|_)+')
space_pattern = re.compile(r'\s+')

# preprocess the text field of each record
for record in data:
    text = record['text']
    text = ftfy.fix_text(text)
    text = re.sub(hashtag_pattern, '', text)
    text = re.sub(emoji_pattern, '', text)
    text = re.sub(link_pattern, '', text)
    text = re.sub(username_pattern, '', text)
    text = re.sub(rt_pattern, '', text)
    text = re.sub(punctuation_pattern, '', text)
    text = re.sub(space_pattern, ' ', text)
    text = unidecode(text)
    record['text'] = text

# save the preprocessed data to a new JSON file
with open('./data/gg2013_preprocessed.json', 'w') as f:
    json.dump(data, f)