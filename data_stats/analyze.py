import json, pickle, os.path
from utils import *

# file to load data from
user_data_file = "/Users/vedantpuri/Downloads/users.json"
users_dump_file = "loaded_users.pickle"
stats_dump_file = "stats.pickle"
analyze_dump_file = "user_analysis.pickle"

# map containing statistics of users, characteristic -> {stat for decisive -> , stat for undecisive ->}
statistics = {}
statistics["gender"] = {}
statistics["pol"] = {}
statistics["rel"] = {}
# threshold value to determine whether an user is decisive or not
threshold = 0.6

# Main
pickle_in = open(stats_dump_file, "rb")
stat_maps = pickle.load(pickle_in)
user_map = stat_maps["user_map"]
relevant_users = 0
# print_map(user_map)
if not os.path.isfile(analyze_dump_file):
    data = load_data(user_data_file, users_dump_file)
    for user_name in data:
        if user_name in user_map:
            user = data[user_name]
            user_data = user_map[user_name]
            gender = user["gender"]
            political_ideology = user["political_ideology"]
            religious_ideology = user["religious_ideology"]
            # num_debates = user["num_of_all_debates"]
            # num_votes = user["num_of_voted_debates"]
            # num_arguments = user["num_of_opinion_arguments"]
            decisiveness = ""
            if user_data["unchanged"]+user_data["changed"] > 1:
                relevant_users += 1
                if (user_data["changed"]/(user_data["unchanged"]+user_data["changed"])) > threshold:
                    decisiveness = "fickle"
                else:
                    decisiveness = "rigid"
                if gender not in ["Male", "Female", "Prefer not to say"]:
                    gender = "Other"
                if len(religious_ideology.split()) > 1 and religious_ideology != "Not Saying":
                    religious_ideology = religious_ideology.split()[0]
                if religious_ideology not in ["Christian", "Agnostic", "Buddhist", "Atheist", "Not Saying"]:
                    religious_ideology = "Other"
                if gender not in statistics["gender"]:
                    statistics["gender"][gender] = {"fickle": 0, "rigid": 0}
                if political_ideology not in statistics["pol"]:
                    statistics["pol"][political_ideology] = {"fickle": 0, "rigid": 0}
                if religious_ideology not in statistics["rel"]:
                    statistics["rel"][religious_ideology] = {"fickle": 0, "rigid": 0}
                statistics["gender"][gender][decisiveness] += 1
                statistics["pol"][political_ideology][decisiveness] += 1
                statistics["rel"][religious_ideology][decisiveness] += 1
    pickle_dict = {
                "statistics": statistics,
                "relevant_users": relevant_users
    }
    pickle_out = open(analyze_dump_file, "wb")
    pickle.dump(pickle_dict, pickle_out)
    pickle_out.close()

else:
    pickle_in = open(analyze_dump_file, "rb")
    data = pickle.load(pickle_in)
    statistics = data["statistics"]
    relevant_users = data["relevant_users"]

# Data analysis
print(f"Number of relevant users: {relevant_users}")
# print_map(statistics)

# gender
labels = []
fickle_vals = []
rigid_vals = []
for k in statistics["gender"]:
    labels += [k]
    fickle_vals += [statistics["gender"][k]["fickle"]]
    rigid_vals += [statistics["gender"][k]["rigid"]]

pie_plot(labels, fickle_vals, "gender_fickle.png")
pie_plot(labels, rigid_vals, "gender_rigid.png")

# Political
labels = []
fickle_vals = []
rigid_vals = []
for k in statistics["pol"]:
    if k != "Labor":
        labels += [k]
        fickle_vals += [statistics["pol"][k]["fickle"]]
        rigid_vals += [statistics["pol"][k]["rigid"]]

pie_plot(labels, fickle_vals, "pol_fickle.png")
pie_plot(labels, rigid_vals, "pol_rigid.png")


# Religious
labels = []
fickle_vals = []
rigid_vals = []
for k in statistics["rel"]:
    labels += [k]
    fickle_vals += [statistics["rel"][k]["fickle"]]
    rigid_vals += [statistics["rel"][k]["rigid"]]

pie_plot(labels, fickle_vals, "rel_fickle.png")
pie_plot(labels, rigid_vals, "rel_rigid.png")
