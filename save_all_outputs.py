import json
from config import config
from frames import get_hosts, get_presenter
from nominees_extraction_regex import get_entites
from award_categories_important_words import import_awards_from_answers
from award_categories_extraction import award_categories
from red_carpet import is_it_best_or_worst
from sentiment import winner_sentiment

def create_json(hosts, answer_award_list, our_awards_list, 
                 nominees, winners, presenters, best_dressed, worst_dressed, winner_sentiment):
    json_dict = {}
    json_dict['Hosts'] = hosts
    json_dict['Awards'] = our_awards_list
    for award in answer_award_list:
        json_dict[award] = {'Nominees': nominees[award], 
                            'Winner': winners[award], 
                            'Presenters': presenters[award],
                            'Polarity' : winner_sentiment[winners[award]][0],
                            'Sentiment': winner_sentiment[winners[award]][1]}
    json_dict['Best dressed'] = best_dressed
    json_dict['Worst dressed'] = worst_dressed
    return json_dict


def save_to_json(hosts, answer_award_list, our_awards_list, 
                 nominees, winners, presenters, best_dressed, worst_dressed, winner_sentiment):
    json_dict = create_json(hosts, answer_award_list, our_awards_list, 
                 nominees, winners, presenters, best_dressed, worst_dressed, winner_sentiment)
    
    with open(config.json_output, 'w') as f:
        json.dump(json_dict, f)


def save_to_readable(hosts, answer_award_list, our_awards_list, 
                 nominees, winners, presenters, best_dressed, worst_dressed):
    json_dict = create_json(hosts, answer_award_list, our_awards_list, 
                 nominees, winners, presenters, best_dressed, worst_dressed)
    with open(config.readable_output, 'w') as f:
        f.write('Hosts: '+ ', '.join(json_dict['Hosts']) + '\n\n')
        f.write('Our Awards: '+ '; '.join(json_dict['Awards']) + '\n\n')
        for award in answer_award_list:
            f.write('Award: '+ str(award)+ '\n')
            if len(nominees[award]) < 1: f.write('Nominees: \n')
            else: f.write('Nominees: '+ ', '.join(json_dict[award]['Nominees'])+ '\n')
            if len(winners[award]) < 1: f.write('Winner: \n')
            else: f.write('Winner: '+ json_dict[award]['Winner']+ '\n')
            f.write('Presenters: '+ ', '.join(json_dict[award]['Presenters'])+ '\n')
            f.write('\n')
        f.write('Best Dressed: '+ ', '.join(json_dict['Best dressed'])+ '\n')
        f.write('Worst Dressed: '+ ', '.join(json_dict['Worst dressed'])+ '\n')
        for winner in winner_sentiment.keys():
            f.write(f'Winner: {winner}, Polarity: {winner_sentiment[winner][0]} Sentiment: {winner_sentiment[winner][1]}')


def collect_data(year, verbose=False):
    hosts = get_hosts(str(year))
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

    presenters = get_presenter(str(year))

    best_dressed = is_it_best_or_worst(True)
    worst_dressed = is_it_best_or_worst(False)
    winner_sentiment = winner_sentiment(str(year))
    save_to_json(hosts, answer_award_list, 
                 our_awards_list, nominees, winners, presenters, best_dressed, worst_dressed)
    save_to_readable(hosts, answer_award_list, 
                 our_awards_list, nominees, winners, presenters, best_dressed, worst_dressed)

if __name__ == '__main__':
    collect_data(2013, True)
    
