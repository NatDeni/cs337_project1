'''Version 0.4'''
import frames
from award_categories_extraction import award_categories
from award_categories_important_words import import_awards_from_answers
from nominees_extraction_regex import get_entites
from save_all_outputs import save_to_json, save_to_readable

def get_hosts(year):
    '''Hosts is a list of one or more strings. Do NOT change the name
    of this function or what it returns.'''
    hosts = frames.get_hosts()
    return hosts

def get_awards(year):
    '''Awards is a list of strings. Do NOT change the name
    of this function or what it returns.'''
    return award_categories()

def get_nominees(year):
    '''Nominees is a dictionary with the hard coded award
    names as keys, and each entry a list of strings. Do NOT change
    the name of this function or what it returns.'''
    answer_award_list = import_awards_from_answers()
    nominees = get_entites(answer_award_list, year, verbose=False, category='NOMINEES')
    return nominees

def get_winner(year):
    '''Winners is a dictionary with the hard coded award
    names as keys, and each entry containing a single string.
    Do NOT change the name of this function or what it returns.'''
    answer_award_list = import_awards_from_answers()
    winners = get_entites(answer_award_list, year, verbose=False, category='WINNERS')
    return winners

def get_presenters(year):
    '''Presenters is a dictionary with the hard coded award
    names as keys, and each entry a list of strings. Do NOT change the
    name of this function or what it returns.'''
    presenters = frames.get_presenter()
    return presenters

def pre_ceremony():
    '''This function loads/fetches/processes any data your program
    will use, and stores that data in your DB or in a json, csv, or
    plain text file. It is the first thing the TA will run when grading.
    Do NOT change the name of this function or what it returns.'''
    # Your code here
    print("Pre-ceremony processing complete.")
    return

def main():
    '''This function calls your program. Typing "python gg_api.py"
    will run this function. Or, in the interpreter, import gg_api
    and then run gg_api.main(). This is the second thing the TA will
    run when grading. Do NOT change the name of this function or
    what it returns.'''
    year = 2013
    hosts = get_hosts(year)
    our_awards_list = get_awards(year)
    answer_award_list = import_awards_from_answers()
    nominees = get_nominees(year)
    winners = get_winner(year)
    presenters = get_presenters(year)

    save_to_json(hosts, answer_award_list, our_awards_list, 
                 nominees, winners, presenters) # save data to file announced in config.json_output
    save_to_readable(hosts, answer_award_list, our_awards_list, 
                 nominees, winners, presenters) # save data to file announced in config.readable_output

    return

if __name__ == '__main__':
    main()