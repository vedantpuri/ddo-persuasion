import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import scipy.spatial as sp
from data_processing import changed_mind, was_flipped, was_convinced

def build_persuade_counts(debates_dict, from_middle=False):
    '''
    Takes the original dictionary of debates and returns the following:
    persuade_counts: {user_name: {category1: number of times user was convinced
        in a debate of category 1, ...}, ...}
    participate_counts: {user_name: {category1: number of debates of category 1
        user voted on, ...}, ...}
    '''
    persuade_counts = {}
    participate_counts = {}
    for _, debate in debates_dict.items():
        for vote in debate['votes']:
            user = vote['user_name']
            category = debate['category']

            if user not in participate_counts.keys():
                participate_counts[user] = {category:1}
            else:
                participate_counts[user][category] = participate_counts[user].get(category,0) + 1

            if from_middle:
                persuade_check = was_convinced
            else:
                persuade_check = changed_mind

            if persuade_check(vote):
                if user not in persuade_counts.keys():
                    persuade_counts[user] = {category:1}
                else:
                    persuade_counts[user][category] = persuade_counts[user].get(category,0) + 1

    return persuade_counts, participate_counts

def build_bigissues_dict(users):
    '''
    Takes the original dictionary of users and returns a dictionary with
    user_name as key and the big issues encoding vector or a user as value.
    '''
    issues_dict = {}
    encoding = ['Pro', 'Con', 'Und', 'N/O']
    for user in users:
        issue_vec = np.zeros((48,4))
        for idx, issue in enumerate(users[user]['big_issues_dict'].values()):
            issue_vec[idx] += np.array([int(issue == e) for e in encoding])
        issues_dict[user] = issue_vec
    return issues_dict

def get_persuadability(user_dict, debate_voters, user_name):
    '''
    Returns the persuadability score of a user for an input list of debate_voters
    in the training set.

    Persuadability score = number of times the user changed their mind in a
    debate in the training set / total number of times the user voted in a debate.
    '''
    persuade_count = debate_voters.count(user_name)
    total_participated = int(user_dict[user_name]['number_of_voted_debates'])
    if total_participated == 0:
        return 0
    return persuade_count / total_participated

def count_persuadability(persuade_counts, participate_counts, user_name, category=None):
    '''
    Returns the persuadability score of a user in a specified category. If
    no category is specified, returns persuadability score over all categories.

    Persuadability score = number of times the user changed their mind in a
    debate of specified category / total number of times the user voted in
    a debate of specified category.
    '''
    if user_name not in persuade_counts.keys():
        return 0
    elif not category:
        persuade_count = sum(persuade_counts[user_name].values())
        total_participated = sum(participate_counts[user_name].values())
    elif category not in persuade_counts[user_name].keys():
        return 0
    else:
        persuade_count = persuade_counts[user_name][category]
        total_participated = participate_counts[user_name][category]
    return persuade_count / total_participated

def get_matching(users, voter_name, debater_name, category):
    '''
    For category 'Politics' or 'Religion', returns 1 if users have equivalent
    ideologies, 0 if different or either indicated 'Not Saying'.
    '''
    if category == 'Politics':
        user_ideology = users[voter_name]['political_ideology']
        debater_ideology = users[debater_name]['political_ideology']
    elif category == 'Religion':
        user_ideology = users[voter_name]['political_ideology']
        debater_ideology = users[debater_name]['political_ideology']
    if user_ideology == 'Not Saying' or debater_ideology == 'Not Saying':
        return 0
    return int(user_ideology == debater_ideology)

def get_gender(users, voter_name, debater_1, debater_2):
    '''
    Returns [voter gender, matches debater 1, matches debater 2]
    where voter gender is a 1-hot encoding of the voter's gender,
    and matches debater is 1 if voter and debater have the same
    gender, 0 otherwise.
    '''
    if users[voter_name]['gender'] == users[debater_1]['gender']:
        match1 = 1
    else:
        match1 = 0
    if users[voter_name]['gender'] == users[debater_2]['gender']:
        match2 = 1
    else:
        match2 = 0
    matches = [match1,match2]

    if users[voter_name]['gender'] == 'Female':
        voter_gender = [1,0]
    elif users[voter_name]['gender'] == 'Male':
        voter_gender = [0,1]
    else:
        voter_gender = [0,0]
        matches = [0,0]

    return voter_gender + matches

def get_bigissues(issues_dict, voter_name, debater_name):
    '''
    Computes the cossine similarities of each issue for two users' big issues
    vectors, returning the average.
    '''
    voter_issues = issues_dict[voter_name]
    debater_issues = issues_dict[debater_name]
    sims = []
    for v,d in zip(voter_issues,debater_issues):
        sims.append(cosine_similarity([v], [d]))
    return np.mean(sims)

def get_decidedness(issues_dict, voter_name):
    voter_issues = issues_dict[voter_name]
    voter_sums = np.sum(voter_issues, axis=0)
    return voter_sums[0]+voter_sums[1], voter_sums[2]+voter_sums[3]
