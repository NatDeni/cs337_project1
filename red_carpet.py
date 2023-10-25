import spacy
import json
from nltk import pos_tag
from config import config
import re
from collections import Counter
spacy_model = spacy.load("en_core_web_sm")

def is_it_best_or_worst(is_best = True):
    with open (config.preproc_datapath) as f:
        data = json.load(f)

    name_pattern = r'[A-Z][a-z]{1,25} [A-Z][a-z]{1,25}'
    if is_best:
        important_words = ['best dress', 'love the look', 'stunning']
    else:
        important_words = ['worst dress', 'disgusting', 'hate the look']

    stop_words = ['golden', 'golden globes', 'globe', 'the', 'dress', 'ok', 'yes', 'fashion', 'red', 'carpet']

    entities = []
    for sentence in data:
        if 'dress' not in sentence['text'].lower(): continue
        for word in important_words:
            if word in sentence['text'].lower():
                for match_name in re.findall(name_pattern, sentence['text']):
                    has_stop_word = False
                    for stop_word in stop_words:
                        if stop_word in match_name.lower():
                            has_stop_word = True 
                            break
                    if has_stop_word: continue
                    # output = spacy_model(match_name)
                    # has_human_name = False
                    # for entity in output.ents:
                    #     if entity.label_ == "PERSON":
                    #         has_human_name = True
                    #         break
                    #     else:
                    #         continue
                    # if not has_human_name: 
                    entities.append(match_name)
                break

    counter = Counter(entities)
    print(counter.most_common(3))
    # print(entities)
    

if __name__ == '__main__':
    is_it_best_or_worst(True)
    is_it_best_or_worst(False)