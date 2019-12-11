import numpy as np
import copy


def filter_category(debates_dict, category):
    """
    Takes the original dictionary of debates and returns a dictionary of same
    structure with only debates of desired category.
    """
    if not category:
        return copy.deepcopy(debates_dict)
    else:
        return {
            k: v
            for k, v in debates_dict.items()
            if v["category"] == category and len(v["votes"]) > 0
        }


def changed_mind(vote):
    """
    Returns true if the user changed their agreement before the debate and
    after the debate.
    """
    if "Tied" not in vote["votes_map"].keys():
        return False
    for debater, vote_data in vote["votes_map"].items():
        if (
            vote_data["Agreed with after the debate"]
            and not vote_data["Agreed with before the debate"]
        ):
            return True
    return False


def get_winner(votes_map):
    """
    Returns username of debate winner for an individual vote.
    1: User changed their mind
    0: User did not change their mind
    """
    for user, v in votes_map.items():
        if "Agreed with after the debate" in v and "Agreed with before the debate" in v:
            if (
                v["Agreed with after the debate"]
                and not v["Agreed with before the debate"]
            ):
                return 1
    return 0


def votes_to_labels(users, votes):
    """
    Takes a list of votes and returns a list of voter usernames and a list of
    winner usernames, with corresponding indices. Output list is dependent on
    voter_function, a function that takes a username as input and outputs a
    boolean, e.g. was_flipped, was_convinced
    Return equal number of changed and unchanged votes and labels from each debate
    """
    voters, labels = [], []
    for vote in votes:
        if vote["user_name"] in users.keys():
            winner = get_winner(vote["votes_map"])
            voters += [vote["user_name"]]
            labels += [winner]

    return voters, labels


def parse_debates(debate_dict, users):
    """
    Parses the original debate dictionary based on voter_function, which specifies
    which voters to generate examples for (e.g. convinced from the middle).
    Returns the following lists, with corresponding indices for each debate in debate_dict:
    debate_text: list of [concatenated 'pro' texts, concatenated 'con' texts]
    debaters: list of ['pro' debater name, 'con' debater name]
    debate_voters: list of voter name lists (if voter was convinced in this debate)
    debate_winners: list of index of winner lists (0 for 'pro' debater, 1 for 'con')
    """
    debate_text = []
    debaters = []
    debate_voters = []
    debate_labels = []
    debate_keys = []

    for name, debate in debate_dict.items():
        voters, labels = votes_to_labels(users, debate["votes"])

        if debate["participant_1_position"] == "Pro":
            pro_debater = debate["participant_1_name"]
            con_debater = debate["participant_2_name"]
        else:
            pro_debater = debate["participant_2_name"]
            con_debater = debate["participant_1_name"]

        if (
            len(voters) > 10
            and pro_debater in users.keys()
            and con_debater in users.keys()
        ):
            debate_keys += [name]
            pro_text = ""
            con_text = ""
            for r in debate["rounds"]:
                for side in r:
                    if side["side"] == "Pro":
                        pro_text += side["text"]
                    else:
                        con_text += side["text"]
            debate_text.append([pro_text, con_text])
            debater_list = (pro_debater, con_debater)
            debaters.append(debater_list)
            debate_voters.append(voters)
            debate_labels.append(labels)

    return debate_keys, debate_text, debaters, debate_voters, debate_labels
