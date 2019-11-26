# NLP - Persuasion Research
Repo for Research work (CornellNLP) on the DDO dataset.

## Goal
To determine which features play an important role in predicting that a debate voter will change his stance after the debate ***v.s.*** a debate voter will **not** change his stance after the debate.

## Software pre-requisites
- python >= 3
- scikit learn
- nltk

## Usage
- **Step 1:** Navigate to ```src/```
- **Step 2:** Run the following command:
```bash
python main.py /path/to/data output_file
```
where the first argument is path to the directory containing the ```users.json``` and ```debates.json``` files from the DDO dataset. The output file is simply a **csv** where the results of the ablation tests will be published.

**Note:** Currently the code internally runs all config files by default while spitting out progress. We would in the future probably extract out this to control this externally.

## Filtering Mechanisms

### Equal split from debate
In this approach filtering was done at the debate processing level. I hoped to have equal number of positive and negative labels in the dataset and took a greedy approach per debate, i.e. I collected equal number of positive and negative samples from each debate, if a debate did not have such a split, that debate was discarded. The results were not so great and hence we tried another filtering mechanism.

### Parametric majority
In this approach filtering was done at the very last stage before training. What that means is that all the examples were processed and colelcted (thus using all debates) and then were shuffled. The minority (fickle users) were all collected and a pre-determined majority % was used to calculate how many rigid users were to be collected. At each rigid sample the sample was chosen with some pre-set probability thus adding some randomness. Currently the experiments for this are in progress but look promising.

## Prediction Task
Given: A combination of user features and linguistic features of the debate

Lables:
- 1: User changes his stance after the debate
- 0: User stays on the same side after the debate


Model Type: Logistic Regression

Hyperparameters:

| Hyperparameter | Explanation| Range/Values tested |
|:-------------:|:-------------:|:-------------:|
| min_votes | Minimum number of votes in a debate for it to be considered a part of the dataset  | TBD |
| majority threshold      | % of unchanged voters wanted in entire dataset | TBD |
| randomness threshold | Randomness with which a sample of unchanged voter is chosen| TBD |
