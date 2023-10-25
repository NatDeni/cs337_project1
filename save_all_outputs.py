import json
from config import config
from frames import get_hosts
from nominees_extraction_regex import get_entites
from award_categories_important_words import import_awards_from_answers
from award_categories_extraction import award_categories


def collect_data(year, verbose=False):
    hosts = get_hosts()
    if verbose: print("Got hosts")
    our_awards_list = award_categories()
    # our_awards_list = []
    if verbose: 
        print("Got awards")
        print(our_awards_list)
    answer_award_list = import_awards_from_answers()
    nominees = get_entites(answer_award_list, year, verbose=False, category='NOMINEES')
    if verbose: print("Got nominees")
    # winners = nominees
    winners = get_entites(answer_award_list, year, verbose=False, category='WINNERS')
    if verbose: print("Got winners")

    json_dict = {}
    json_dict['Hosts'] = hosts
    json_dict['Awards'] = our_awards_list
    # print(answer_award_list)
    # print(nominees.keys())
    for award in answer_award_list:
        json_dict[award] = {'Nominees': nominees[award], 'Winner': winners[award], 'Presenters': []}

    with open(config.json_output, 'w') as f:
        json.dump(json_dict, f)
    with open(config.readable_output, 'w') as f:
        f.write('Hosts: '+ ', '.join(json_dict['Hosts']) + '\n\n')
        f.write('Our Awards: '+ '; '.join(json_dict['Awards']) + '\n\n')
        for award in answer_award_list:
            f.write('Award: '+ str(award)+ '\n')
            if len(nominees[award]) < 1: f.write('Nominees: \n')
            else: f.write('Nominees: '+ ', '.join(nominees[award])+ '\n')
            if len(winners[award]) < 1: f.write('Winner: \n')
            else: f.write('Winner: '+ winners[award][0]+ '\n')
            f.write('Presenters: '+ ''+ '\n')
            f.write('\n')
        # json.dump(json_dict)

if __name__ == '__main__':
    collect_data(2013, True)
    
