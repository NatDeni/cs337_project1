import nltk
nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')
from nltk import RegexpParser, pos_tag
import json 
from config import config
from collections import Counter
import spacy
spacy_model = spacy.load("en_core_web_sm")  

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

    patterns = """ <NN>{4} | <JJS>{1}<JJ>?.*<NN>{2}.*<JJ>?<CC>?<NN>{1} | <JJS>{1}<NN>{1}.*<IN>{1}<DT>{1}.*<NN>{2,}.*<NN>{1}"""

    chunk_pattern_list = [RegexpParser('P: {'+pattern.strip()+'}') for pattern in patterns.split('|')]
    categories = []

    award_verbs = ['won', 'wins', 'got', 'goes to']

    for sentence in data:
        # if 'best' not in sentence['text']: continue
        has_verb = False 
        for verb in award_verbs:
            if verb in sentence['text']:
                has_verb = True
                break
        if not has_verb: continue
        if len(sentence['text']) <= 3: continue

        # Perform POS tagging on the words in the sentence
        tokens = nltk.word_tokenize(sentence['text'].lower())
        pos_tags = pos_tag(tokens)

        sent_patters = []
        for chunk_parser in chunk_pattern_list:
            tree = chunk_parser.parse(pos_tags)
            # print('\n||', sentence['text'], '||\n')

            # Extract and print the matching category
            for subtree in tree.subtrees():
                if subtree.label() == 'P':
                    category = " ".join(word for word, tag in subtree.leaves())
                    # categories.append(category)
                    # ToDo remove person

                    # print(category)
                    if 'best' not in category:
                        continue
                    sent_patters.append(category)
                    # print("Category:", category)
        categories.extend(list(set(sent_patters)))

    categories_no_people = []

    for i in range(len(categories)):
 
        output = spacy_model(categories[i])
        has_human_name = False
        for entity in output.ents:
            if entity.label_ == "PERSON":
                has_human_name = True
                print(entity.text)
                break
            else:
                continue
        if not has_human_name: 
            categories_no_people.append(categories[i])
    print(categories_no_people)

    # categories = list(set(categories))
    cou = Counter(categories_no_people)
    top26 = cou.most_common(26)
    top50 = cou.most_common(50)

    # print(top26)
    # with open('tmp4.txt', 'w') as f:
    #     for c in top26:
    #         f.write(str(c) + '\n')
    #     f.write('-' * 20 + '\n')
    #     for c in top50:
    #         f.write(str(c) + '\n')

    # Save the top26 and top50 lists as a JSON file
    with open('./data/categories.json', 'w') as f:
        json.dump({'top26': {c[0]: c[1] for c in top26},
                'top50': {c[0]: c[1] for c in top50}}, f)

if __name__ == '__main__':
    intial_categories()