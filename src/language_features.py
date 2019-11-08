import numpy as np
import nltk
import re
from spellchecker import SpellChecker
import string
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import re

arg_lex_folder = "lexicons/argument_lexicons/"

spell = SpellChecker()
sentiment = SentimentIntensityAnalyzer()

opponent_words = ["opponent", "contendor", "pro", "con"]

hedges = [
    "think",
    "thought",
    "thinking",
    "almost",
    "apparent",
    "apparently",
    "appear",
    "appeared",
    "appears",
    "approximately",
    "around",
    "assume",
    "assumed",
    "certain amount",
    "certain extent",
    "certain level",
    "claim",
    "claimed",
    "doubt",
    "doubtful",
    "essentially",
    "estimate",
    "estimated",
    "feel",
    "felt",
    "frequently",
    "from our perspective",
    "generally",
    "guess",
    "in general",
    "in most cases",
    "in most instances",
    "in our view",
    "indicate",
    "indicated",
    "largely",
    "likely",
    "mainly",
    "may",
    "maybe",
    "might",
    "mostly",
    "often",
    "on the whole",
    "ought",
    "perhaps",
    "plausible",
    "plausibly",
    "possible",
    "possibly",
    "postulate",
    "postulated",
    "presumable",
    "probable",
    "probably",
    "relatively",
    "roughly",
    "seems",
    "should",
    "sometimes",
    "somewhat",
    "suggest",
    "suggested",
    "suppose",
    "suspect",
    "tend to",
    "tends to",
    "typical",
    "typically",
    "uncertain",
    "uncertainly",
    "unclear",
    "unclearly",
    "unlikely",
    "usually",
    "broadly",
    "tended to",
    "presumably",
    "suggests",
    "from this perspective",
    "from my perspective",
    "in my view",
    "in this view",
    "in our opinion",
    "in my opinion",
    "to my knowledge",
    "fairly",
    "quite",
    "rather",
    "argue",
    "argues",
    "argued",
    "claims",
    "feels",
    "indicates",
    "supposed",
    "supposes",
    "suspects",
    "postulates",
]

evidence_list = [
    "evidence",
    "show",
    "shows",
    "say",
    "says",
    "state",
    "states",
    "according to",
    "showed",
    "stated",
    "according",
]

pos_filename = "lexicons/liu-positive-words.txt"
neg_filename = "lexicons/liu-negative-words.txt"
offensive_filename = "lexicons/offensive.txt"

polar_set = set(
    [
        "is",
        "are",
        "was",
        "were",
        "am",
        "have",
        "has",
        "had",
        "can",
        "could",
        "shall",
        "should",
        "will",
        "would",
        "may",
        "might",
        "must",
        "do",
        "does",
        "did",
        "ought",
        "need",
        "dare",
        "if",
        "when",
        "which",
        "who",
        "whom",
        "how",
    ]
)

first_person = ["i", "me", "my", "mine"]
second_person = ["you", "your", "yours"]

positive_words = set(map(lambda x: x.strip(), open(pos_filename).read().splitlines()))
negative_words = set(map(lambda x: x.strip(), open(neg_filename).read().splitlines()))
offensive_words = set(
    map(lambda x: x.strip(), open(offensive_filename).read().splitlines())
)


def read_mpqa_data():
    lexicon_dic = {}
    with open("lexicons/mpqa_lexicon.tff", encoding="utf8") as f:
        line_list = f.read().splitlines()
    for line in line_list:
        tokens = line.split()
        word = tokens[2][6:]
        pos_tag = tokens[3][5:]
        sub_type = tokens[0][5:]
        polarity = tokens[5][14:]
        if (word, pos_tag) not in lexicon_dic:
            lexicon_dic[(word, pos_tag)] = {"type": sub_type, "priorpolarity": polarity}

    return lexicon_dic


mpqa_lexicon_dic = read_mpqa_data()


def includes_sentiment_words(
    text, priorpolarity="positive", polarity_type="strongsubj"
):
    count = 0
    token_list = nltk.pos_tag(text)
    for tok in token_list:

        pos = "none"
        if tok[1] == "NN" or tok[1] == "NNP" or tok[1] == "NNS":
            pos = "noun"
        if (
            tok[1] == "VB"
            or tok[1] == "VBD"
            or tok[1] == "VBG"
            or tok[1] == "VBN"
            or tok[1] == "VBP"
            or tok[1] == "VBZ"
        ):
            pos = "verb"
        if tok[1] == "JJR" or tok[1] == "JJS" or tok[1] == "JJ":
            pos = "adj"

        if (tok[0].lower(), pos) in mpqa_lexicon_dic:
            if (
                mpqa_lexicon_dic[(tok[0].lower(), pos)]["type"] == polarity_type
                and mpqa_lexicon_dic[(tok[0].lower(), pos)]["priorpolarity"]
                == priorpolarity
            ):
                count += 1
        if (tok[0].lower(), "anypos") in mpqa_lexicon_dic:
            if (
                mpqa_lexicon_dic[(tok[0].lower(), "anypos")]["type"] == polarity_type
                and mpqa_lexicon_dic[(tok[0].lower(), "anypos")]["priorpolarity"]
                == priorpolarity
            ):
                count += 1
    if count > 0:
        return count
    else:
        return 0


def get_modals(text):

    could_count = 0
    can_count = 0
    would_count = 0
    shall_count = 0
    should_count = 0
    will_count = 0
    must_count = 0
    may_count = 0
    might_count = 0

    for word in text:
        if word.lower() == "could":
            could_count += 1
        if word.lower() == "can":
            can_count += 1
        if word.lower() == "would":
            would_count += 1
        if word.lower() == "shall":
            shall_count += 1
        if word.lower() == "should":
            should_count += 1
        if word.lower() == "will":
            will_count += 1
        if word.lower() == "must":
            must_count += 1

        if word.lower() == "may":
            may_count += 1
        if word.lower() == "might":
            might_count += 1

    return [
        could_count,
        can_count,
        would_count,
        shall_count,
        should_count,
        will_count,
        must_count,
        may_count,
        might_count,
    ]


def type_token_ratio(text):
    text_len = 0
    num_q = 0
    word_set = set()
    text_len = len(text)
    if text_len == 0:
        return 0.0
    for word in text:
        word_set.add(word)

    return len(word_set) / text_len


def get_lexicon_features(text, lexicon_type):
    """
    given a tokenized word list and lexicon list, counts how many words are in the lexicon.
    """
    occurance = 0
    for word in text:
        if word.lower() in lexicon_type:
            occurance += 1
    return occurance


def person_count(text):
    """
    counts first, person, third pronouns in a tokenized word list.
    """
    first_count = 0
    second_count = 0
    third_count = 0
    for token in text:
        if (
            token.lower() == "i"
            or token.lower() == "us"
            or token.lower() == "my"
            or token.lower() == "mine"
            or token.lower() == "we"
            or token.lower() == "our"
            or token.lower() == "us"
            or token.lower() == "myself"
            or token.lower() == "ourselves"
            or token.lower() == "me"
        ):
            first_count += 1
        if (
            token.lower() == "you"
            or token.lower() == "yours"
            or token.lower() == "your"
            or token.lower() == "yourself"
            or token.lower() == "yourselves"
        ):
            second_count += 1
        if (
            token.lower() == "he"
            or token.lower() == "she"
            or token.lower() == "his"
            or token.lower() == "her"
            or token.lower() == "hers"
            or token.lower() == "they"
            or token.lower() == "them"
            or token.lower() == "him"
            or token.lower() == "himself"
            or token.lower() == "herself"
            or token.lower() == "themselves"
        ):
            third_count += 1
    return [first_count, second_count, third_count]


def get_length(text):
    return len(text)


def question_count(text):
    occurance = 0
    for i, token in enumerate(text):
        if i > 0 and token == "?" and not text[i - 1] == "?":
            occurance += 1
    return occurance


def number_count(text):
    r = re.compile("^[0-9]*$")
    return len(list(filter(r.match, text)))


def get_sentiment(text_untokenized):
    score = sentiment.polarity_scores(text_untokenized)
    return score["pos"], score["neu"], score["neg"]


def misspellings(text):
    r = re.compile("^((?![.,'\"!?\\-:\[\]]).)*$")
    text = list(filter(r.match, text))
    misspelled = spell.unknown(text)
    return len(misspelled)


def get_urls(text):
    urls = re.findall("https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+", text)
    return len(urls)


def read_macros():
    macros = []
    macro_files = [
        "lexicons/argument_lexicons/modals.tff",
        "lexicons/argument_lexicons/spoken.tff",
        "lexicons/argument_lexicons/wordclasses.tff",
        "lexicons/argument_lexicons/pronoun.tff",
        "lexicons/argument_lexicons/intensifiers.tff",
    ]
    for fname in macro_files:
        with open(fname) as f:
            content = f.readlines()
            macros.extend([cont.strip() for cont in content if cont[0] == "@"])
    macro_dict = {}
    for macro in macros:
        macro_name = macro.split("=")[0]
        macro_name = "(" + macro_name + ")"
        options = macro.split("{")[1]
        options = options.split("}")[0]
        options = options.split(",")
        macro_dict[macro_name] = options
    return macro_dict


def read_arg_regex(fname, macros):
    with open(fname) as f:
        cont_list = []
        content = [regex.strip() for regex in f.readlines() if regex[0] != "#"]
        # print(content)
        # print("\n")
        for cont in content:
            if "@" in cont:
                for word in cont.split():
                    if "@" in word and word in macros.keys():
                        # print(word)
                        for options in macros[word]:
                            new_string = cont.replace(word, options)
                            cont_list.append(new_string)
            else:
                cont_list.append(cont)

    return cont_list


macros = read_macros()


def arg_lexicon_check(string, lexicon_name):
    cont_list = read_arg_regex(lexicon_name, macros)
    count = 0
    for regex in cont_list:
        regexp = re.compile(regex)
        if bool(regexp.search(string)):
            count += 1
    return count


def text_to_features(debate_text):
    """
    Transforms text into linguistic features, concatenated into one vector.
    Input 'text' is a list of 2 strings, containing the concatenated 'pro' and
    'con' texts, respectively, for all rounds in one debate.
    """
    features = []
    for text in debate_text:
        feature_array = []
        tokenized_text = nltk.word_tokenize(text)
        feature_array.append(get_length(tokenized_text))
        feature_array.append(get_lexicon_features(tokenized_text, opponent_words))
        feature_array.append(get_lexicon_features(tokenized_text, hedges))
        feature_array.append(get_lexicon_features(tokenized_text, evidence_list))
        feature_array.extend(get_sentiment(text))
        feature_array.append(includes_sentiment_words(tokenized_text))
        feature_array.append(
            includes_sentiment_words(
                tokenized_text, priorpolarity="positive", polarity_type="weaksubj"
            )
        )
        feature_array.append(
            includes_sentiment_words(
                tokenized_text, priorpolarity="negative", polarity_type="strongsubj"
            )
        )
        feature_array.append(
            includes_sentiment_words(
                tokenized_text, priorpolarity="negative", polarity_type="weaksubj"
            )
        )
        feature_array.append(get_lexicon_features(tokenized_text, offensive_words))
        feature_array.append(get_lexicon_features(tokenized_text, positive_words))
        feature_array.append(get_lexicon_features(tokenized_text, negative_words))
        feature_array.extend(person_count(tokenized_text))
        feature_array.extend(get_modals(tokenized_text))
        feature_array.append(misspellings(tokenized_text))
        feature_array.append(number_count(tokenized_text))
        feature_array.append(get_lexicon_features(tokenized_text, ["!"]))
        feature_array.append(question_count(tokenized_text))
        feature_array.append(type_token_ratio(tokenized_text))
        feature_array.append(get_urls(text))
        feature_array.append(
            arg_lexicon_check(text, arg_lex_folder + "assessments.tff")
        )
        feature_array.append(arg_lexicon_check(text, arg_lex_folder + "doubt.tff"))
        feature_array.append(arg_lexicon_check(text, arg_lex_folder + "authority.tff"))
        feature_array.append(arg_lexicon_check(text, arg_lex_folder + "emphasis.tff"))
        feature_array.append(arg_lexicon_check(text, arg_lex_folder + "necessity.tff"))
        feature_array.append(arg_lexicon_check(text, arg_lex_folder + "causation.tff"))
        feature_array.append(
            arg_lexicon_check(text, arg_lex_folder + "generalization.tff")
        )
        feature_array.append(arg_lexicon_check(text, arg_lex_folder + "structure.tff"))
        feature_array.append(
            arg_lexicon_check(text, arg_lex_folder + "conditionals.tff")
        )
        feature_array.append(
            arg_lexicon_check(text, arg_lex_folder + "inconsistency.tff")
        )
        feature_array.append(
            arg_lexicon_check(text, arg_lex_folder + "possibility.tff")
        )
        feature_array.append(arg_lexicon_check(text, arg_lex_folder + "wants.tff"))
        feature_array.append(arg_lexicon_check(text, arg_lex_folder + "contrast.tff"))
        feature_array.append(arg_lexicon_check(text, arg_lex_folder + "priority.tff"))
        feature_array.append(arg_lexicon_check(text, arg_lex_folder + "difficulty.tff"))
        feature_array.append(
            arg_lexicon_check(text, arg_lex_folder + "inyourshoes.tff")
        )
        feature_array.append(
            arg_lexicon_check(text, arg_lex_folder + "rhetoricalquestion.tff")
        )
        features.extend(feature_array)
    return features
