
import json, pickle, os.path

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

def load_data():
    if not os.path.isfile(debates_dump_file):
        print("No pickle dump found. Loading data from scratch ...")
        with open(data_file) as json_file:
            data = json.load(json_file)
        pickle_out = open(debates_dump_file,"wb")
        pickle.dump(data, pickle_out)
        pickle_out.close()
        print(f"Data Loaded. Dumped to:{debates_dump_file}")
    else:
        print(f"Pickle file found: {debates_dump_file } Loading from pickle ...")
        pickle_in = open(debates_dump_file,"rb")
        data = pickle.load(pickle_in)
        print("Data Loaded.")

    return data

def analyze_vote(vote):
    before, after = "", ""
    for k in vote:
        vote_dict = vote[k]
        if vote_dict["Agreed with before the debate"]:
            before = k
        if vote_dict["Agreed with after the debate"]:
            after = k
    # print(before, after)
    return before == after

def print_map(h_map):
    for k in h_map:
        print(f"{k} :   {h_map[k]}")


# Main
if not os.path.isfile(stats_dump_file):
    data = load_data()
    for topic in data:
        debate = data[topic]
        debate_id = debate["title"]
        # print(debate_id)
        if debate_id not in debate_map:
            debate_map[debate_id] = {"changed": 0, "unchanged":0}

        category = debate["category"]
        if category not in category_map:
            category_map[category] = {"changed": 0, "unchanged":0}

        debate_votes = debate["votes"]
        participants = debate["participant_1_name"], debate["participant_2_name"]
        for vote in debate_votes:
            user_name = vote["user_name"]
            if user_name not in user_map:
                user_map[user_name] = {"changed": 0, "unchanged":0}

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

    pickle_dict = {"user_map": user_map, "debate_map": debate_map, "category_map": category_map}
    pickle_out = open(stats_dump_file,"wb")
    pickle.dump(pickle_dict, pickle_out)
    pickle_out.close()

else:
    pickle_in = open(stats_dump_file,"rb")
    stat_maps = pickle.load(pickle_in)
