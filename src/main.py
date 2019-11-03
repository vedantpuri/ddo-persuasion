import json
import copy
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import KFold
from sklearn.metrics import accuracy_score
from sklearn.feature_extraction.text import TfidfVectorizer
from data_processing import parse_debates, filter_category
from user_features import *
from language_features import text_to_features

class LogRegModel():
    def __init__(self, category):
        '''
        Creates a Logistic Regression Model instance.

        :param category: string or None, specifies the category of debates to
            filter for when processing the data for model input
        '''
        self.model = LogisticRegression(solver='lbfgs',max_iter=1000)
        self.category = category

    def __call__(self, X):
        '''
        Returns predicted labels for samples in X.
        '''
        self.model.predict(X)

    def extract_features(self, voter_function, all_debates, users, bigissues_dict):
        '''
        From the debates and users dictionaries, processes data into the form
        needed for model input. This includes:
            - filter debates for category
            - concatenate 'pro' and 'con' rounds text into two separate strings
            - transforms 'pro' and 'con' strings into linguistic features vec
            - generates user-based feature vecs for each voter/debater pair
            - concatenates all features into X
            - generates labels into Y: 0 for 'pro' debater win, 1 for 'con'
        '''
        debates = filter_category(all_debates, self.category)
        debate_text, debaters, debate_voters, debate_winners = parse_debates(debates, users, voter_function)
        text_list = [item for sublist in debate_text for item in sublist]
        text_features = [text_to_features(text) for text in debate_text]
        vectorizer.fit(text_list)
        tfidf_features = np.array(vectorizer.transform(text_list).toarray())
        tfidf_features = tfidf_features.reshape((int(tfidf_features.shape[0]/2),100))

        X_userbased = []
        X_linguistic = []
        Y = []
        for debate_idx,voters in enumerate(debate_voters):
            debater1, debater2 = debaters[debate_idx]
            for voter in voters:
                user_features = []
                user_features.append(get_bigissues(bigissues_dict,voter,debater1))
                user_features.append(get_bigissues(bigissues_dict,voter,debater2))
                user_features.append(get_matching(users,voter,debater1,'Politics'))
                user_features.append(get_matching(users,voter,debater2,'Politics'))
                user_features.append(get_matching(users,voter,debater1,'Religion'))
                user_features.append(get_matching(users,voter,debater2,'Religion'))
                user_features.extend(get_decidedness(bigissues_dict,voter))
                user_features.extend(get_gender(users,voter,debater1,debater2))
                X_userbased.append(user_features)
            t_features = np.concatenate((text_features[debate_idx], tfidf_features[debate_idx]))
            X_linguistic.extend([t_features]*len(voters))
            Y.extend(debate_winners[debate_idx])

        X = np.concatenate((X_userbased, X_linguistic), axis=1)
        Y = np.array(Y)
        voters = [item for sublist in debate_voters for item in sublist]
        print('\tGenerated',X.shape[0],' samples from ',len(debate_text),' debates after filtering\n','='*50)
        return X, Y, voters

    def filter_features(self, X, feature_dicts):
        '''
        Filters X, the inputs for model training, to contain only the features
        specified in feature_dict.
        '''
        feature_bools = []
        user_features, ling_features = feature_dicts
        for incl_feat, num_vals in user_features.values():
            if incl_feat:
                feature_bools.extend([1]*num_vals)
            else:
                feature_bools.extend([0]*num_vals)
        for i in range(2):
            for incl_feat, num_vals in ling_features.values():
                if incl_feat:
                    feature_bools.extend([1]*num_vals)
                else:
                    feature_bools.extend([0]*num_vals)
        feature_idxs = np.nonzero(feature_bools)[0]
        return X[:,feature_idxs]

    def fit(self, X, Y):
        '''
        Fits the model on the input training data and labels.
        '''
        self.model.fit(X,Y)

    def evaluate(self, X, Y):
        '''
        Returns the mean accuracy on the input test data and labels.
        '''
        return self.model.score(X,Y)

def run_baseline(Y):
    '''
    Calculates the accuracy of the majority baseline for true labels Y.
    '''
    preds = np.zeros(len(Y))
    if np.mean(Y) > 0.5:
        preds = np.ones(len(Y))
    print('\tTesting majority baseline')
    print('\tAccuracy: ',accuracy_score(preds,Y),'\n')
    print('='*50,'\n')

def run_training(X, Y, voters, features, message):
    '''
    Trains a logistic regression model on the specified set of features.
    Evaluates the model using 5-fold cross validation.

    :param X: array of all features
    :param Y: array of true labels
    :param voters: flattened list of voters in training set
    :param features: dictionary mapping feature name to boolean
    :param message: message to print when showing results
    '''
    # FILTER FEATURES FOR TRAINING
    X = model.filter_features(X, features)
    print('\tModel: ',message,'\n')

    # SPLIT DATA FOR CROSS VALIDATION
    accuracy = []
    kf = KFold(n_splits=5, shuffle=True, random_state=1)
    for train_idx, test_idx in kf.split(X):
        X_train, X_test = X[train_idx], X[test_idx]
        Y_train, Y_test = Y[train_idx], Y[test_idx]

        # ADD PERSUADABILITY FEATURE FOR TRAINING GROUP
        if features[0]['persuade'][0]:
            v_train = [voters[idx] for idx in train_idx]
            p = []
            for voter in v_train:
                p.append(get_persuadability(users, v_train, voter))
            X_train = np.insert(X_train,0,p,axis=1)
            v_test = [voters[idx] for idx in test_idx]
            p = []
            for voter in v_test:
                p.append(get_persuadability(users, v_test, voter))
            X_test = np.insert(X_test,0,p,axis=1)

        model.fit(X_train, Y_train)
        accuracy.append(model.evaluate(X_test, Y_test))
    print('\tAccuracy: ',np.mean(accuracy),'\n')
    print('='*50,'\n')


if __name__=="__main__":
    # LOAD DATA
    print('\n','='*50,'\n\tLoading Dataset...\n')
    with open('debate_dataset/users.json', 'r') as f:
        users = json.load(f)
    with open('debate_dataset/debates.json', 'r') as f:
        all_debates = json.load(f)
    print('\t',len(all_debates),' debates and ',len(users),' users loaded\n')

    # PROCESS DATA
    print('\tProcessing Data...\n')
    bigissues_dict = build_bigissues_dict(users)

    # SPECIFY CATEGORIES, CREATE MODEL, FORMAT FEATURES
    category = 'Politics' # one of: {None, 'Politics', 'Religion', 'Miscellaneous', ...}
    voter_function = was_convinced # one of: {was_convinced, was_flipped}
    print('\tFiltered category of debates: ',category,'\n')
    model = LogRegModel(category)
    vectorizer = TfidfVectorizer(ngram_range=(1,3),max_features=50,stop_words='english')
    X,Y,voters = model.extract_features(voter_function, all_debates, users, bigissues_dict)
    scaler = StandardScaler()
    X = scaler.fit_transform(X)

    # SPECIFY FEATURES AND RUN MODEL
    user_features = { # userbased features
                'persuade'      :(True,0),
                'opinion'       :(True,2),
                'pol_ideology'  :(True,2),
                'rel_ideology'  :(True,2),
                'decidedness'   :(True,1),
                'undecidedness' :(True,1),
                'gender'        :(True,4)}
    ling_features = { # linguistic features
                'length'        :(True,1),
                'ref_opp'       :(True,1),
                'politeness'    :(True,1),
                'evidence'      :(True,1),
                'sentiment'     :(True,3),
                'subjectivity'  :(True,4),
                'swear'         :(True,1),
                'connotation'   :(True,2),
                'pronouns'      :(True,3),
                'modals'        :(True,9),
                'spelling'      :(True,1),
                'numbers'       :(True,1),
                'excl_marks'    :(True,1),
                'questions'     :(True,1),
                'type_ratio'    :(True,1),
                'links'         :(True,1),
                'arg_lex'       :(True,17),
                'tfidf'         :(True,50)}
    features = (user_features, ling_features)
    message = '+ user + persuade + orig linguistic'
    run_training(X, Y, voters, features, message)

    run_baseline(Y)
