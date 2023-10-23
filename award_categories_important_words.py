import json

important_words = [['best']]
person_word = [['actor'], ['actress'], ['director']]
special_word = [['score'], ['song']]
role_word = [['supporting']]
movie_genre_word = [['drama'], ['comedy', 'musical'], ['animated'], ['screenplay']]
movie_type_word = [['series'], ['picture', 'film', 'feature'], ['mini', 'mini-series', 'miniseries']]


def define_important_words(category):
    list_words = []
    for words_cat in [important_words, person_word, special_word, role_word, movie_genre_word, movie_type_word]:
        for word in words_cat:
            for i in range(len(word)):
                if word[i].lower() in category.lower(): 
                    list_words.append(word)
                    break
    return list_words


def is_award_in_tweet(tweet, award_words):
    for words in award_words:
        tmp = False
        for word in words:
            if word.lower() in tweet.lower():
                tmp = True
                break
        if not tmp:
            return False
    return True