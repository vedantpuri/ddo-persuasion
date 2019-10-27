import json, pickle, os.path
from utils import *

# file to load data from
data_file = "/Users/uniwei/Downloads/users.json"
users_dump_file = "loaded_users.pickle"
stats_dump_file = "stats.pickle"
analyze_dump_file = "analyze.pickle"

# map containing statistics of users, characteristic -> {stat for decisive -> , stat for undecisive ->}
statistics = {}
# threshold value to determine whether an user is decisive or not
threshold = 0.6

def load_data():
"""
Load the users either from scratch or from a pickle dump
:return: The loaded users
"""
if not os.path.isfile(users_dump_file):
    print("No pickle dump found. Loading data from scratch ...")
    with open(data_file) as json_file:
        data = json.load(json_file)
    pickle_out = open(users_dump_file, "wb")
    pickle.dump(data, pickle_out)
    pickle_out.close()
    print(f"Data Loaded. Dumped to:{users_dump_file}")
else:
    print(f"Pickle file found: {users_dump_file } Loading from pickle ...")
    pickle_in = open(users_dump_file, "rb")
    data = pickle.load(pickle_in)
    print("Data Loaded.")

return data

# Main
pickle_in = open(stats_dump_file, "rb")
stat_maps = pickle.load(pickle_in)
user_map = stat_maps["user_map"]

if not os.path.isfile(analyze_dump_file):
    data = load_data()
    for user_name in data:
        user = data[user_name]
        u = user_map[user_name]
        gender = user["gender"]
        num_debates = user["num_of_all_debates"]
        num_votes = user["num_of_voted_debates"]
        num_arguments = user["num_of_opinion_arguments"]
        political_ideology = user["political_ideology"]
        religious_ideology = user["religious_ideology"]
        decisiveness = ""
        if (u["changed"]/(u["unchanged"]+u["changed"])) > threshold:
            decisiveness = "decisive"
        else:
            decisiveness = "undecisive"
        statistics["headcount"][decisiveness] += 1
        statistics["num_debates"][decisiveness] += num_debates
        statistics["num_votes"][decisiveness] += num_votes
        statistics["num_arguments"][decisiveness] += num_arguments
        if gender == "Male":
            statistics["male"][decisiveness] += 1
        if political_ideology == "Conservative":
            statistics["conservative"][decisiveness] += 1
        if religious_ideology == "Christian":
            statistics["christian"][decisiveness] += 1

    pickle_dict = {
        "statistics": statistics,
    }
    pickle_out = open(analyze_dump_file, "wb")
    pickle.dump(pickle_dict, pickle_out)
    pickle_out.close()

else:
    pickle_in = open(analyze_dump_file, "rb")
    statistics = pickle.load(pickle_in)

# Data analysis
print(f"Number of users analyzed {len(user_map)}")

# Plot user data
user_data = []
total_users = statistics["headcount"]["decisive"] + statistics["headcount"]["undecisive"]
for k in statistics:
    user_data.append(["decisive", statistics[k]["decisive"]/total_users])
    user_data.append(["undecisive", statistics[k]["undecisive"]/total_users])

group_plot(user_data, ['decisiveness', 'features', 'val'], 'user_stats.png')
