import nltk
nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')
from nltk import RegexpParser
from nltk import pos_tag
import json 
from config import config
from collections import Counter

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
# chunk_parser = RegexpParser(patterns)

categories = []

for sentence in data:
    if 'best' not in sentence['text']: continue
    if len(sentence['text']) <= 3: continue
    # Perform POS tagging on the words in the sentence
    tokens = nltk.word_tokenize(sentence['text'].lower())
    pos_tags = pos_tag(tokens)

    # print(pos_tags)

    # Parse the sentence to find the specified pattern
    # try:
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
                sent_patters.append(category)
                print("Category:", category)
    categories.extend(list(set(sent_patters)))


# categories = list(set(categories))
cou = Counter(categories)
top26 = cou.most_common(26)
top50 = cou.most_common(50)
print(top26)
with open('tmp.txt', 'w') as f:
    for c in top26:
        f.write(str(c) + '\n')
    f.write('-' * 20 + '\n')
    for c in top50:
        f.write(str(c) + '\n')
    # f.write(str(categories))
    