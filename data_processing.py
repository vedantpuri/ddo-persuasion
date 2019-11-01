import numpy as np
import copy

def filter_category(debates_dict, category):
    '''
    Takes the original dictionary of debates and returns a dictionary of same
    structure with only debates of desired category.
    '''
    if not category:
        return copy.deepcopy(debates_dict)
    else:
        return {k:v for k,v in debates_dict.items() if v['category']==category and len(v['votes'])>0}

def was_convinced(vote):
    '''
    Returns true if the user was undecided before the debate and agrees with
    one side after the debate.
    '''
    if 'Tied' not in vote['votes_map'].keys():
        return False
    undecided_before = vote['votes_map']['Tied']['Agreed with before the debate'] == True
    undecided_after = vote['votes_map']['Tied']['Agreed with after the debate'] == True
    return undecided_before and not undecided_after

def was_flipped(vote):
    '''
    Returns true if the user was on one side before the debate and agrees with
    the opposite side after the debate.
    '''
    #TODO
    if 'Tied' not in vote['votes_map'].keys():
        return False
    undecided_before = vote['votes_map']['Tied']['Agreed with before the debate'] == True
    undecided_after = vote['votes_map']['Tied']['Agreed with after the debate'] == True
    if not undecided_after and not undecided_before:
        for username, vote_data in vote['votes_map'].items():
            if vote_data['Agreed with before the debate'] != vote_data['Agreed with after the debate']:
                return True
    return False

def changed_mind(vote):
    '''
    Returns true if the user changed their agreement before the debate and
    after the debate.
    '''
    if 'Tied' not in vote['votes_map'].keys():
        return False
    for debater,vote_data in vote['votes_map'].items():
        if vote_data['Agreed with after the debate'] and not vote_data['Agreed with before the debate']:
            return True
    return False

def get_winner(votes_map):
    '''
    Returns username of debate winner for an individual vote.
    '''
    wins = [user for user,v in votes_map.items() if v['Agreed with after the debate']]
    return wins[0]

def votes_to_labels(users, votes, voter_function):
    '''
    Takes a list of votes and returns a list of voter usernames and a list of
    winner usernames, with corresponding indices. Output list is dependent on
    voter_function, a function that takes a username as input and outputs a
    boolean, e.g. was_flipped, was_convinced
    '''
    voters = []
    winners = []
    for vote in votes:
        if voter_function(vote) and vote['user_name'] in users.keys():
            voters.append(vote['user_name'])
            winners.append(get_winner(vote['votes_map']))
    return voters, winners

def parse_debates(debate_dict, users, voter_function):
    '''
    Parses the original debate dictionary based on voter_function, which specifies
    which voters to generate examples for (e.g. convinced from the middle).
    Returns the following lists, with corresponding indices for each debate in debate_dict:
    debate_text: list of [concatenated 'pro' texts, concatenated 'con' texts]
    debaters: list of ['pro' debater name, 'con' debater name]
    debate_voters: list of voter name lists (if voter was convinced in this debate)
    debate_winners: list of index of winner lists (0 for 'pro' debater, 1 for 'con')
    '''
    debate_text = []
    debaters = []
    debate_voters = []
    debate_winners = []

    for name, debate in debate_dict.items():
        voters, winners = votes_to_labels(users, debate['votes'], voter_function)

        if debate['participant_1_position'] == 'Pro':
            pro_debater = debate['participant_1_name']
            con_debater = debate['participant_2_name']
        else:
            pro_debater = debate['participant_2_name']
            con_debater = debate['participant_1_name']

        if len(voters)>0 and pro_debater in users.keys() and con_debater in users.keys():
            pro_text = ''
            con_text = ''
            for r in debate['rounds']:
                for side in r:
                    if side['side'] == 'Pro':
                        pro_text += side['text']
                    else:
                        con_text += side['text']
            debate_text.append([pro_text,con_text])
            debater_list = (pro_debater,con_debater)
            debaters.append(debater_list)
            debate_voters.append(voters)
            winner_idxs = [debater_list.index(user) for user in winners]
            debate_winners.append(winner_idxs)

    return debate_text, debaters, debate_voters, debate_winners
