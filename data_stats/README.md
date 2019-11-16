# Statistics

## Figures

*Note:* 60% is a threshold **variable**, one could change that in the code to set a custom threshold. Also users having only voted once have been filtered out.

Figure file name keys:


| Key        | Meaning|
|:-------------:|:-------------:|
| pol      | Political ideologies |
| rel      | Religious ideologies     |
| fickle | Changing stance more often than unchanging (changing >= 60% of the time)|
| rigid | Not changing stance more often than changing (changing <= 40% of the time) |


## Output Logs

Output from running analyze.py to get the statistics

```terminal
==================================================
Age wise statistics
==================================================
20-29 :   {'fickle': 5, 'rigid': 5}
30-39 :   {'fickle': 1, 'rigid': 3}
10-19 :   {'fickle': 1, 'rigid': 0}
50-59 :   {'fickle': 0, 'rigid': 1}
Total users for which age available: 16

==================================================
Gender-wise statistics
==================================================
Male
fickle :   0.2914798206278027
rigid :   0.7085201793721974
sample size :   223

Prefer not to say
fickle :   0.2727272727272727
rigid :   0.7272727272727273
sample size :   99

Female
fickle :   0.37037037037037035
rigid :   0.6296296296296297
sample size :   54

Other
fickle :   0.0
rigid :   1.0
sample size :   2

==================================================
Political ideology-wise statistics
==================================================
Libertarian
fickle :   0.20689655172413793
rigid :   0.7931034482758621
sample size :   29

Apathetic
fickle :   0.375
rigid :   0.625
sample size :   8

Conservative
fickle :   0.27906976744186046
rigid :   0.7209302325581395
sample size :   43

Not Saying
fickle :   0.3333333333333333
rigid :   0.6666666666666666
sample size :   132

Undecided
fickle :   0.2222222222222222
rigid :   0.7777777777777778
sample size :   27

Moderate
fickle :   0.3333333333333333
rigid :   0.6666666666666666
sample size :   30

Liberal
fickle :   0.2391304347826087
rigid :   0.7608695652173914
sample size :   46

Socialist
fickle :   0.21428571428571427
rigid :   0.7857142857142857
sample size :   14

Other
fickle :   0.3181818181818182
rigid :   0.6818181818181818
sample size :   22

Anarchist
fickle :   0.25
rigid :   0.75
sample size :   12

Progressive
fickle :   0.4166666666666667
rigid :   0.5833333333333334
sample size :   12

Green
fickle :   0.0
rigid :   1.0
sample size :   1

Communist
fickle :   1.0
rigid :   0.0
sample size :   2

==================================================
Religious ideology-wise statistics
==================================================
Atheist
fickle :   0.21428571428571427
rigid :   0.7857142857142857
sample size :   42

Not Saying
fickle :   0.34459459459459457
rigid :   0.6554054054054054
sample size :   148

Christian
fickle :   0.27
rigid :   0.73
sample size :   100

Agnostic
fickle :   0.3023255813953488
rigid :   0.6976744186046512
sample size :   43

Other
fickle :   0.21951219512195122
rigid :   0.7804878048780488
sample size :   41

Buddhist
fickle :   0.75
rigid :   0.25
sample size :   4

==================================================
Number of relevant users: 4348
==================================================
```
