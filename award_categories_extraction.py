import re
import nltk
import json 
import spacy
from nltk import RegexpParser, pos_tag
from config import config
from collections import Counter

spacy_model = spacy.load("en_core_web_sm")  
nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')

def award_categories(): 
    with open (config.award_extraction) as f:
        data = json.load(f)

    patterns = """ P: {<JJS>{1}<JJ>?.*<NN>{2}.*<JJ>?<CC>?<NN>{1} | <JJS><NN>{2}<:><NN><CC><JJ> | \
    <JJS>{1}<NN>{1}.*<IN>{1}<DT>{1}.*<NN>{2,}.*<NN>{1} | <RBS><NN><IN><DT><NN><IN><DT><JJ><NN> | \
    <JJS><JJ><:><NN>{2} | <JJS><NN><:><NN>{2} | <RBS><NNS><CC><NN>{2}<VBN><IN><NN> | \
    <RBS><NN><IN><DT><NN><IN><DT><NN>{2}<NN> | \
    <RBS><NN><IN><DT><NN><IN><DT><JJ><NN><IN><DT><NN><NNS><CC><NN>{2}<VBN><IN><NN> | <JJS><JJ><NN>{2}}"""
    
    chunk_pattern_list = [RegexpParser(patterns)]
    categories = []
    award_verbs = ['won', 'wins', 'got', 'goes to', 'receives', 'accepts', 'accepted', 'received']

    for sentence in data:
        has_verb = False 
        for verb in award_verbs:
            if verb in sentence['text'].lower():
                has_verb = True
                break
        if not has_verb: continue
        if len(sentence['text'].lower()) <= 3: continue

        # Perform POS tagging on the words in the sentence
        tokens = nltk.word_tokenize(sentence['text'].lower())
        pos_tags = pos_tag(tokens)

        sent_patters = []
        for chunk_parser in chunk_pattern_list:
            tree = chunk_parser.parse(pos_tags)
            for subtree in tree.subtrees():
                if subtree.label() == 'P':
                    category = " ".join(word for word, tag in subtree.leaves())

                    if 'best' not in category:
                        continue
                    sent_patters.append(category)

        categories.extend(list(set(sent_patters)))

    categories_no_people = []
    for i in range(len(categories)):
 
        output = spacy_model(categories[i])
        has_human_name = False
        for entity in output.ents:
            if entity.label_ == "PERSON":
                has_human_name = True
                break
            else:
                continue
        if not has_human_name: 
            categories_no_people.append(categories[i])
    
    for i in range(len(categories_no_people)):
        categories_no_people[i] = categories_no_people[i].replace('-', '')
        if 'tv' in categories_no_people[i]:
            categories_no_people[i] = categories_no_people[i].replace('tv', 'television series').replace('series series', 'series')
        categories_no_people[i] = categories_no_people[i].replace('  ', ' ')

    sw = ['win', 'award', 'red']
    categories_no_people = [x for x in categories_no_people if sw[0] not in x]
    categories_no_people = [x for x in categories_no_people if sw[1] not in x]
    categories_no_people = [x for x in categories_no_people if sw[2] not in x]
    categories_no_people = [x.replace('comedy or musical', 'comedy').replace('comedy musical', 'comedy').replace('musical', 'comedy')
                             for x in categories_no_people]
    
    categories_no_people = [x.replace('for a', 'in a') for x in categories_no_people]

    cou = Counter(categories_no_people)
    top40 = cou.most_common(40)

    new_counter = {}
    added = []
    for i in range(len(top40)):
        if i in added: continue
        new_counter[top40[i][0]] = top40[i][1]
        che_str_i = top40[i][0].replace('in a ', '')
        words_i = che_str_i.split()
        for j in range(i + 1, len(top40)):
            if j in added: continue
            che_str_j = top40[j][0].replace('in a ', '')
            words_j = che_str_j.split()
            if Counter(words_j) == Counter(words_i) or \
                che_str_i in che_str_j or che_str_j in che_str_i or \
                top40[i][0] in top40[j][0] or top40[j][0] in top40[i][0]:
                new_counter[top40[i][0]] += top40[j][1]
                added.append(j)

    # with open('./data/award_categories.txt', 'w') as f:
    #     for c in new_counter:
    #         f.write(str(c) + '\n')

    only_categories = []
    for c in top40[0:26]:
        only_categories.append(c[0])

    return only_categories

def get_human_named_awards():
    with open (config.preproc_special_datapath) as f:
        data = json.load(f)

    award_sentences = []
    award_hashtags = []

    for sentence in data:
        if len(sentence['text'].lower()) <= 3: continue

        if '#' in sentence['text'].lower():
            hashtag = sentence['text'].split('#')[1].split(' ')[0]

        if hashtag.endswith('Award') and len(hashtag) > 6:
            award_sentences.append(sentence['text'])
            award_hashtags.append(hashtag)

    count = Counter(award_hashtags)
    top1 = count.most_common(1)
    award = re.sub(r'(?<!^)(?=[A-Z])', ' ', top1[0][0])

    final_list = []
    final_list.append(award)

    award_categories_list = award_categories()
    for category in award_categories_list:
        final_list.append(category)

    return award_categories_list


if __name__ == '__main__':
    
    award_categories()
    get_human_named_awards()