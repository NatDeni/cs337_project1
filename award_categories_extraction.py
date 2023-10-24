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

def award_categories(): 
    with open (config.preproc_datapath) as f:
        data = json.load(f)

    # patterns = """
    #     <JJS><NN><NN>{2} | \
    #     <JJS><JJ><NN>{2} | <RBS><NN><IN><DT><NN><IN><DT><NN>{2}<NN><CC><JJ> | \
    #     <RBS><NN><IN><DT><NN><IN><DT><JJ><NN><IN><DT><NN><NN>
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

    patterns = """<JJS>{1}<JJ>?.*<NN>{2}.*<JJ>?<CC>?<NN>{1} | <JJS>{1}<NN>{1}.*<IN>{1}<DT>{1}.*<NN>{2,}.*<NN>{1}"""

    chunk_pattern_list = [RegexpParser('P: {'+pattern.strip()+'}') for pattern in patterns.split('|')]
    
    # chunk_pattern_list = [RegexpParser(patterns)]
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

    print(top50)

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

    print(no_substring)

    for i, string in enumerate(no_substring):
        if string[0] in combinations_dict.keys():
            # print(string[0])
            continue
            
        for key, value in combinations_dict.items():
            exists = value.find(string[0])
            if exists != -1:
                lst_string = list(string)
                lst_string[0] = key
                no_substring[i] = tuple(lst_string)
                # print(no_substring[i])
                break
    # print(no_substring)
  
    unique_strings = {}
    for string, num in no_substring:
        if string in unique_strings:
            unique_strings[string] += num
        else:
            unique_strings[string] = num

    no_substring = [(string, num) for string, num in unique_strings.items()]
    # print(no_substring)

# Group tuples by number of words in first part
    groups = defaultdict(list)
    for string, num in no_substring:
        num_words = len(string.split())
        groups[num_words].append((string, num))

    # Remove duplicates within each group
    for num_words, tuples in groups.items():
        for i, (string1, num1) in enumerate(tuples):
            for j in range(i+1, len(tuples)):
                string2, num2 = tuples[j]
                if set(string1.split()) <= set(string2.split()):
                    tuples[i] = (string1, num1+num2)
                    tuples.pop(j)
                    break

    # Flatten groups back into a list of tuples
    no_substring = [(string, num) for tuples in groups.values() for string, num in tuples]

    no_substring = sorted(no_substring, key=lambda x: x[1], reverse=True)
    print(no_substring[:26])

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
    award_categories()
    # get_human_named_awards()
