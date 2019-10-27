import json, pickle, os.path
from utils import *

# file to load debate data from
data_file = "/Users/vedantpuri/Downloads/debates.json"
debates_dump_file = "loaded_debates.pickle"
stats_dump_file = "stats.pickle"

# debate_id -> {c -> , u->}
debate_map = {}
# category_id -> {c -> , u->}
category_map = {}
# user_name -> {c -> , u->}
user_map = {}


# Main
if not os.path.isfile(stats_dump_file):
    data = load_data(data_file, debates_dump_file)
    for topic in data:
        debate = data[topic]
        debate_id = debate["title"]
        # print(debate_id)
        if debate_id not in debate_map:
            debate_map[debate_id] = {"changed": 0, "unchanged": 0}

        category = debate["category"]
        if category not in category_map:
            category_map[category] = {"changed": 0, "unchanged": 0}

        debate_votes = debate["votes"]
        participants = debate["participant_1_name"], debate["participant_2_name"]
        for vote in debate_votes:
            user_name = vote["user_name"]
            if user_name not in user_map:
                user_map[user_name] = {"changed": 0, "unchanged": 0}

            user_vote = vote["votes_map"]
            if len(user_vote) == 3:
                if user_name not in participants:
                    if analyze_vote(user_vote):
                        debate_map[debate_id]["unchanged"] += 1
                        user_map[user_name]["unchanged"] += 1
                        category_map[category]["unchanged"] += 1
                    else:
                        debate_map[debate_id]["changed"] += 1
                        user_map[user_name]["changed"] += 1
                        category_map[category]["changed"] += 1

    pickle_dict = {
        "user_map": user_map,
        "debate_map": debate_map,
        "category_map": category_map,
    }
    pickle_out = open(stats_dump_file, "wb")
    pickle.dump(pickle_dict, pickle_out)
    pickle_out.close()

else:
    pickle_in = open(stats_dump_file, "rb")
    stat_maps = pickle.load(pickle_in)


# Data analysis
debate_map = stat_maps["debate_map"]
category_map = stat_maps["category_map"]
user_map = stat_maps["user_map"]

print(f"Number of debates analyzed {len(debate_map)}")
print(f"Number of categories analyzed {len(category_map)}")
print(f"Number of users analyzed {len(user_map)}")

# Plot category data
category_data = []
for k in category_map:
     category_data.append(["changed", k, category_map[k]["changed"]])
     category_data.append(["unchanged", k, category_map[k]["unchanged"]])

group_plot(category_data, ['stance', 'category', 'val'], 'category_stats.png')
