import json
import os
import re

tweet_json_path = os.path.join('data', 'gg2013.json')

f = open(tweet_json_path)
data = json.load(f)

keys_data = ['text', 'user', 'id', 'timestamp_ms']

name_pattern = r"([A-Z][a-z]*)[\s-]([A-Z][a-z]*)" # two capitalized words separated by space

matches = []
for comment_text in [s['text'] for s in data[:100]]:
    matches.extend(re.findall(name_pattern, comment_text))

for match in matches[:30]:
    print(match)