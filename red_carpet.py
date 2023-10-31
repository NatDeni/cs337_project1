import json
from config import config
import re
from collections import Counter

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
                    entities.append(match_name)
                break

    counter = Counter(entities)
    top_3 = counter.most_common(3)

    top_3_list = []
    for c in top_3:
        top_3_list.append(c[0])
        
    return top_3_list

if __name__ == '__main__':
    is_it_best_or_worst(True)
    is_it_best_or_worst(False)