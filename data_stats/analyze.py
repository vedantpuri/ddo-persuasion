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
statistics["age"] = {}
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
            bday = user["birthday"]
            political_ideology = user["political_ideology"]
            religious_ideology = user["religious_ideology"]
            # num_debates = user["num_of_all_debates"]
            # num_votes = user["num_of_voted_debates"]
            # num_arguments = user["num_of_opinion_arguments"]
            decisiveness = ""
            if user_data["unchanged"]+user_data["changed"] > 1:
                relevant_users += 1
                frac_changed = user_data["changed"]/(user_data["unchanged"]+user_data["changed"])
                # If user changes his mind more than 60% (threshold) of the times
                if frac_changed > threshold:
                    decisiveness = "fickle"
                # If user changes his mind less than 40% (100 - 60)% of the times
                elif frac_changed > 1 - threshold:
                    decisiveness = "rigid"
                else:
                    # Irrelevant user
                    continue

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

                if bday != "- Private -":
                    bday_arr = bday.split()
                    _, _, yr = bday_arr
                    age = 2019 - int(yr)
                    if age < 100:
                        age_group = age // 10
                        if age_group not in statistics["age"]:
                            statistics["age"][age_group] = {"fickle": 0, "rigid":0}
                        statistics["age"][age_group][decisiveness] += 1

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

def calc_proportions(key, statistics):
    decisiveness = ["fickle", "rigid"]
    ret_map = {}
    for k in statistics[key]:
        total = statistics[key][k]["fickle"] + statistics[key][k]["rigid"]
        ret_map[k] = {"fickle": 0, "rigid": 0}
        ret_map[k]["fickle"] = statistics[key][k]["fickle"] / total
        ret_map[k]["rigid"] = statistics[key][k]["rigid"] / total
        ret_map[k]["sample size"] = total

    return ret_map

DIVIDER = "="*50

age_map = {}
total_age_available = 0
for k in statistics["age"]:
    total_age_available += statistics["age"][k]["fickle"] + statistics["age"][k]["rigid"]
    group = str(k*10) + "-" + str(k*10 + 9)
    age_map[group] = statistics["age"][k]

print(DIVIDER + "\nAge wise statistics\n" + DIVIDER)
print_map(age_map)
print(f"Total users for which age available: {total_age_available}\n")

print(DIVIDER + "\nGender-wise statistics\n"  + DIVIDER)
gender_props = calc_proportions("gender", statistics)
print_map_rec(gender_props)

print(DIVIDER + "\nPolitical ideology-wise statistics\n" + DIVIDER)
pol_props = calc_proportions("pol", statistics)
print_map_rec(pol_props)

print(DIVIDER + "\nReligious ideology-wise statistics\n" + DIVIDER)
rel_props = calc_proportions("rel", statistics)
print_map_rec(rel_props)

# Data analysis
print(DIVIDER + f"\nNumber of relevant users: {relevant_users}\n" + DIVIDER)
# print_map(statistics)

# gender
group_plot(prepare_for_plot(gender_props), ['firmness', 'Gender', 'val'], 'gender_firmness.png')
aggregate_and_plot(statistics, "gender")

# Political
group_plot(prepare_for_plot(pol_props), ['firmness', 'Pol Ideology', 'val'], 'pol_firmness.png')
aggregate_and_plot(statistics, "pol", "Labor")

# Religious
group_plot(prepare_for_plot(rel_props), ['firmness', 'Rel Ideology', 'val'], 'rel_firmness.png')
aggregate_and_plot(statistics, "rel")


# Age
labels, fickle_vals, rigid_vals = [], [], []
for k in age_map:
    labels += [k]
    fickle_vals += [age_map[k]["fickle"]]
    rigid_vals += [age_map[k]["rigid"]]
pie_plot(labels, fickle_vals, "age_fickle.png")
pie_plot(labels, rigid_vals, "age_rigid.png")



for k in age_map:
    total = age_map[k]["fickle"] + age_map[k]["rigid"]
    age_map[k]["fickle"] /= total
    age_map[k]["rigid"] /= total
group_plot(prepare_for_plot(age_map), ['firmness', 'Age range', 'val'], 'age_firmness.png')
