import matplotlib.pyplot as plt
import pandas as pd
import os.path
import json, pickle, os.path
from matplotlib import rcParams
rcParams.update({'figure.autolayout': True})


def load_data(data_path, pickle_path):
    """
    Load the debates either from scratch or from a pickle dump
    :return: The loaded debates
    """
    if not os.path.isfile(pickle_path):
        print("No pickle dump found. Loading data from scratch ...")
        with open(data_path) as json_file:
            data = json.load(json_file)
        pickle_out = open(pickle_path, "wb")
        pickle.dump(data, pickle_out)
        pickle_out.close()
        print(f"Data Loaded. Dumped to:{pickle_path}")
    else:
        print(f"Pickle file found: {pickle_path} Loading from pickle ...")
        pickle_in = open(pickle_path, "rb")
        data = pickle.load(pickle_in)
        print("Data Loaded.")

    return data


def analyze_vote(vote):
    """
    Analyze the stance of voter before and after
    :param vote: The vote map of a user
    :return: True if the stance was unchanged, False otherwise
    """
    before, after = "", ""
    for k in vote:
        vote_dict = vote[k]
        if vote_dict["Agreed with before the debate"]:
            before = k
        if vote_dict["Agreed with after the debate"]:
            after = k
    return before == after


def print_map(h_map):
    for k in h_map:
        print(f"{k} :   {h_map[k]}")

def save_fig(fig_name):
    if not os.path.isdir('../Figures/'):
        os.makedirs('../Figures/')
    plt.savefig('../Figures/' + fig_name)
    plt.close()


def group_plot(data, data_key, fig_name):
    df = pd.DataFrame(data, columns=data_key)
    df.pivot(data_key[1], data_key[0], data_key[2]).plot(kind='bar', figsize=(15,10))
    save_fig(fig_name)

def pie_plot(labels, values, fig_name):
    plt.pie(values, labels=labels)
    save_fig(fig_name)
