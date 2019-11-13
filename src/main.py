import sys
import json
import os.path
import copy
import pickle
import collections
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import KFold
from sklearn.metrics import accuracy_score
from sklearn.utils import shuffle
from sklearn.feature_extraction.text import TfidfVectorizer
from data_processing import parse_debates, filter_category
from user_features import *
from language_features import text_to_features


class LogRegModel:
    def __init__(self, category):
        """
        Creates a Logistic Regression Model instance.

        :param category: string or None, specifies the category of debates to
            filter for when processing the data for model input
        """
        self.model = LogisticRegression(solver="lbfgs", max_iter=1000)
        self.category = category

    def __call__(self, X):
        """
        Returns predicted labels for samples in X.
        """
        self.model.predict(X)

    def form_dict(self, debate_keys, text_features):
        """
        Convert debate key to feature into dict form
        """
        ret_map = {}
        for idx in range(len(debate_keys)):
            ret_map[debate_keys[idx]] = text_features[idx]
        return ret_map

    def extract_features(self, all_debates, users, bigissues_dict):
        """
        From the debates and users dictionaries, processes data into the form
        needed for model input. This includes:
            - filter debates for category
            - concatenate 'pro' and 'con' rounds text into two separate strings
            - transforms 'pro' and 'con' strings into linguistic features vec
            - generates user-based feature vecs for each voter/debater pair
            - concatenates all features into X
            - generates labels into Y: 0 for 'pro' debater win, 1 for 'con'
        """
        debates = filter_category(all_debates, self.category)
        debate_keys, debate_text, debaters, debate_voters, labels = parse_debates(
            debates, users
        )
        text_list = [item for sublist in debate_text for item in sublist]
        # check if pickle file exists
        # if does not exist
        if not os.path.isfile("ttf.pickle"):
            print("No pickle file found")
            text_features = []
            # i = 0
            for text in debate_text:
                # i = i + 1
                # print("processing:",i,"out of",len(debate_text))
                to_add = text_to_features(text)
                # print(to_add)
                # exit()
                text_features += [to_add]
            fileObject = open("ttf.pickle", "wb")
            print("Length of text_features", len(text_features))
            print("Length of debate_keys", len(debate_keys))
            text_features_dict = self.form_dict(debate_keys, text_features)
            pickle.dump(text_features_dict, fileObject)
            fileObject.close()
            # save to pickle
        else:
            print("\tPickle file found\n")
            fileObject = open("ttf.pickle", "rb")
            print("\tLoading pickle file ...\n")
            ttf = pickle.load(fileObject)
            text_features = [ttf[k] for k in debate_keys]
            print("\tPickle file loaded.\n")
            fileObject.close()

        vectorizer.fit(text_list)
        tfidf_features = np.array(vectorizer.transform(text_list).toarray())
        tfidf_features = tfidf_features.reshape((int(tfidf_features.shape[0] / 2), 100))

        X_userbased = []
        X_linguistic = []
        Y = []
        for debate_idx, voters in enumerate(debate_voters):
            # print(debate_idx)
            debater1, debater2 = debaters[debate_idx]
            for voter in voters:
                user_features = []
                user_features.append(get_bigissues(bigissues_dict, voter, debater1))
                user_features.append(get_bigissues(bigissues_dict, voter, debater2))
                user_features.append(get_matching(users, voter, debater1, "Politics"))
                user_features.append(get_matching(users, voter, debater2, "Politics"))
                user_features.append(get_matching(users, voter, debater1, "Religion"))
                user_features.append(get_matching(users, voter, debater2, "Religion"))
                user_features.extend(get_decidedness(bigissues_dict, voter))
                user_features.extend(get_gender(users, voter, debater1, debater2))
                X_userbased.append(user_features)
            t_features = np.concatenate(
                (text_features[debate_idx], tfidf_features[debate_idx])
            )
            X_linguistic.extend([t_features] * len(voters))
            Y.extend(labels[debate_idx])

        X = np.concatenate((X_userbased, X_linguistic), axis=1)
        Y = np.array(Y)
        voters = [item for sublist in debate_voters for item in sublist]
        print(
            "\tGenerated",
            X.shape[0],
            " samples from ",
            len(debate_text),
            " debates after filtering\n",
            "=" * 50,
        )
        return X, Y, voters

    def filter_features(self, X, feature_dicts):
        """
        Filters X, the inputs for model training, to contain only the features
        specified in feature_dict.
        """
        feature_bools = []
        user_features, ling_features = feature_dicts
        for incl_feat, num_vals in user_features.values():
            if incl_feat:
                feature_bools.extend([1] * num_vals)
            else:
                feature_bools.extend([0] * num_vals)
        for i in range(2):
            for incl_feat, num_vals in ling_features.values():
                if incl_feat:
                    feature_bools.extend([1] * num_vals)
                else:
                    feature_bools.extend([0] * num_vals)
        feature_idxs = np.nonzero(feature_bools)[0]
        return X[:, feature_idxs]

    def fit(self, X, Y):
        """
        Fits the model on the input training data and labels.
        """
        self.model.fit(X, Y)

    def evaluate(self, X, Y):
        """
        Returns the mean accuracy on the input test data and labels.
        """
        return self.model.score(X, Y)


def run_baseline(Y):
    """
    Calculates the accuracy of the majority baseline for true labels Y.
    """
    preds = np.zeros(len(Y))
    if np.mean(Y) > 0.5:
        preds = np.ones(len(Y))
    print("\tTesting majority baseline")
    print("\tAccuracy: ", accuracy_score(preds, Y), "\n")
    print("=" * 50, "\n")


def run_training(X, Y, voters, features, message):
    """
    Trains a logistic regression model on the specified set of features.
    Evaluates the model using 5-fold cross validation.

    :param X: array of all features
    :param Y: array of true labels
    :param voters: flattened list of voters in training set
    :param features: dictionary mapping feature name to boolean
    :param message: message to print when showing results
    """
    # FILTER FEATURES FOR TRAINING
    X = model.filter_features(X, features)
    print("\tModel: ", message, "\n")

    # SPLIT DATA FOR CROSS VALIDATION
    accuracy = []
    kf = KFold(n_splits=5, shuffle=True, random_state=1)
    for train_idx, test_idx in kf.split(X):
        X_train, X_test = X[train_idx], X[test_idx]
        Y_train, Y_test = Y[train_idx], Y[test_idx]

        # ADD PERSUADABILITY FEATURE FOR TRAINING GROUP
        # if features[0]['persuade'][0]:
        #     v_train = [voters[idx] for idx in train_idx]
        #     p = []
        #     for voter in v_train:
        #         p.append(get_persuadability(users, v_train, voter))
        #     X_train = np.insert(X_train,0,p,axis=1)
        #     v_test = [voters[idx] for idx in test_idx]
        #     p = []
        #     for voter in v_test:
        #         p.append(get_persuadability(users, v_test, voter))
        #     X_test = np.insert(X_test,0,p,axis=1)

        model.fit(X_train, Y_train)
        accuracy.append(model.evaluate(X_test, Y_test))
    print("\tAccuracy: ", np.mean(accuracy), "\n")
    print("=" * 50, "\n")


def parse_config(config_file):
    # Check if file exists
    if not os.path.isfile(config_file):
        print("Config file does not exist. Make sure path is correct.")
        exit()
    with open(config_file, "r") as f:
        config = json.load(f)
    # Validate category
    if config["category"] == "":
        config["category"] = None
    # Setup features in tuple format
    for k in config["user_features"]:
        config["user_features"][k] = (
            config["user_features"][k][0],
            config["user_features"][k][1],
        )
    for k in config["ling_features"]:
        config["ling_features"][k] = (
            config["ling_features"][k][0],
            config["ling_features"][k][1],
        )

    return config

def filter_samples(X, Y, majority_threshold):
    # change their mind = 1
    # stay the same = 0

    # LOGIC -----
    # count number of ones in Y
    one_count = collections.Counter(Y)[1]
    # that number should be minority
    # calculate number of 0s we need in the DS
    zero_count = ((one_count / (1 - majority_threshold)) - one_count)
    ret_X, ret_Y = [], []
    ctr = 0
    for i in range(len(X)):
    # iterate
        if Y[i] == 1:
            # add it
            ret_X += [X[i]]
            ret_Y += [Y[i]]
        else:
            if ctr < zero_count:
                ret_X += [X[i]]
                ret_Y += [Y[i]]
                ctr += 1
    print(zero_count, one_count)
    print(len(ret_X))
    print(len(ret_Y))
    exit()
    return np.array(ret_X), np.array(ret_Y)

if __name__ == "__main__":
    # if len(sys.argv) < 2:
    #     print("Config File not passed in. Quitting ...")
    #     exit()
    # configuration = parse_config(sys.argv[1])
    path = "./configs/"
    files = os.listdir(path)
    s = []
    for file in files:
        print("Configuration:",file)
        # configuration = parse_config(path+file)
        configuration = parse_config('./configs/user_features_only.json')
        # LOAD DATA
        prepend_path = "/Users/vedantpuri/Downloads/"
        print("\n", "=" * 50, "\n\tLoading Dataset...\n")
        with open(prepend_path + "users.json", "r") as f:
            users = json.load(f)
        with open(prepend_path + "debates.json", "r") as f:
            all_debates = json.load(f)
        print("\t", len(all_debates), " debates and ", len(users), " users loaded\n")

        # PROCESS DATA
        print("\tProcessing Data...\n")
        bigissues_dict = build_bigissues_dict(users)

        # SPECIFY CATEGORIES, CREATE MODEL, FORMAT FEATURES
        category = configuration[
            "category"
        ]  # one of: {None, 'Politics', 'Religion', 'Miscellaneous', ...}
        print("\tFiltered category of debates: ", category, "\n")
        model = LogRegModel(category)
        vectorizer = TfidfVectorizer(
            ngram_range=(1, 3), max_features=50, stop_words="english"
        )
        X, Y, voters = model.extract_features(all_debates, users, bigissues_dict)
        scaler = StandardScaler()
        X = scaler.fit_transform(X)
        print(X.shape)
        print(Y.shape)

        # SPECIFY FEATURES AND RUN MODEL
        user_features = configuration["user_features"]
        ling_features = configuration["ling_features"]
        features = (user_features, ling_features)
        # message = "+ user + persuade + orig linguistic"
        message = file
        X, Y = shuffle(X, Y)
        filter_samples(X, Y, 0.6)
        run_training(X, Y, voters, features, message)

        run_baseline(Y)
