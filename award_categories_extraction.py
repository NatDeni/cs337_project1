import re
import nltk
import json 
import spacy
from nltk import RegexpParser, pos_tag
from config import config
from collections import Counter, defaultdict

spacy_model = spacy.load("en_core_web_sm")  
nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')

def intial_categories(): 
    with open (config.preproc_datapath) as f:
        data = json.load(f)

    # patterns = """
    #     P: {<JJS><NN><:><NN>{2} | \
    #     <JJS><JJ><NN>{2} | <RBS><NN><IN><DT><NN><IN><DT><NN>{2}<:><NN><CC><JJ> | \
    #     <RBS><NN><IN><DT><NN><IN><DT><JJ><NN><IN><DT><NN><NN>}
    # """

    # patterns = """
    #     <JJS><NN><NN>{2} | <RBS><NN><IN><DT><NN><IN><DT><NN>{2}<NN><CC><JJ> | \
    #     <RBS><NN><IN><DT><NN><IN><DT><JJ><NN><IN><DT><NN>{2} | \
    #     <RBS><NN><IN><DT><NN><IN><DT><JJ><NN><IN><DT><NN><NNS><CC><NN>{2}<VBN><IN><NN> | \
    #     <JJS><NN>{2}<NN><CC><JJ> | <RBS><NNS><CC><NN>{2}<VBN><IN><NN> | \
    #     <JJS><JJ><NN><NN>{2} | <RBS><NN><IN><DT><NN><IN><DT><NN>{2}<NN> | \
    #     <NN>{2}<VBZ><NN> | \
    #     <RBS><NN><IN><DT><NN><IN><DT><NNS><CC><NN>{2}<VBN><IN><NN>
    # """

    patterns = """P: {<JJS>{1}<JJ>?.*<NN>{2}.*<JJ>?<CC>?<NN>{1} | <JJS>{1}<NN>{1}.*<IN>{1}<DT>{1}.*<NN>{2,}.*<NN>{1}}"""

    # chunk_pattern_list = [RegexpParser('P: {'+pattern.strip()+'}') for pattern in patterns.split('|')]
    
    chunk_pattern_list = [RegexpParser(patterns)]
    categories = []
    award_verbs = ['won', 'wins', 'got', 'goes to']

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

    cou = Counter(categories_no_people)
    top26 = cou.most_common(26)
    top50 = cou.most_common(50)

    combinations = []
    larger_categories = []
    combinations_dict = defaultdict(list)

    for category in top50:
        if ' or ' in category[0]:
            larger_categories.append(category[0])
            combinations.append(category[0])
            combinations_dict[category[0]] = category[0]
        else:
            continue

    for i in range(len(larger_categories)):
        first_part, second_part = larger_categories[i].split('or')
        # print(first_part, "-", second_part)

        first_part = first_part.strip()
        second_part = second_part.strip()
        first_part_list = list(first_part.split(" "))
        length_first = len(first_part_list)

        first_part_list_copy = first_part_list.copy()
        first_part_list_copy[length_first - 1] = second_part
        second_combination  = " ".join(first_part_list_copy) + ' or ' + first_part_list[length_first - 1]
        combinations.append(second_combination)

        if larger_categories[i] in combinations_dict.keys():
            combinations_dict[larger_categories[i]] += ', ' + second_combination 

    # print(top50)

    # print("------------------------------------------------------------")
    is_it_substring = False
    no_substring = []
    for category in top50:
        for combination in combinations:
            exists = combination.find(category[0])
            if exists != -1 and category[0] != combination:
                is_it_substring = True
                
                category = list(category)
                category[0] = combination
                top50.append(category)
                top50.remove(category)
                no_substring.append(tuple(category))
                break
            else:
                is_it_substring = False
                continue
        if not is_it_substring:
            no_substring.append(category)

    # print(no_substring)

    final = []
    values = combinations_dict.values()
    sum = 0
    for element in no_substring:
        for key, values in combinations_dict.items():
            exists = values.find(element[0])
            if exists !=-1:
                print(element[0])


    #     if element[0] in combinations_dict.keys():
    #     for values in combinations_dict.values():
    #         print
    #         print(element[0])

    # with open('tmp5.txt', 'w') as f:
    #     for c in top50:
    #         f.write(str(c) + '\n')

    # print(top26)
    # with open('tmp4.txt', 'w') as f:
    #     for c in top26:
    #         f.write(str(c) + '\n')
    #     f.write('-' * 20 + '\n')
    #     for c in top50:
    #         f.write(str(c) + '\n')

    # with open('./data/categories.json', 'w') as f:
    #     json.dump({'top26': {c[0]: c[1] for c in top26},
    #             'top50': {c[0]: c[1] for c in top50}}, f)

def get_human_named_awards():
    with open ('./data/gg2013_preprocessed_special.json') as f:
        data = json.load(f)

    award_sentences = []
    award_hashtags = []

    for sentence in data:
        if len(sentence['text'].lower()) <= 3: continue

        if '#' in sentence['text'].lower():
            hashtag = sentence['text'].split('#')[1].split(' ')[0]

        if hashtag.endswith('Award') and len(hashtag) > 6:
            print(sentence['text'], '-----------', hashtag)
            award_sentences.append(sentence['text'])
            award_hashtags.append(hashtag)

    count = Counter(award_hashtags)
    top1 = count.most_common(1)
    print(top1)

    award = re.sub(r'(?<!^)(?=[A-Z])', ' ', top1[0][0])
    print(award)


if __name__ == '__main__':
    # intial_categories()
    get_human_named_awards()
