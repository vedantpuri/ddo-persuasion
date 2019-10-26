import matplotlib.pyplot as plt
import pandas as pd
import os.path
from matplotlib import rcParams
rcParams.update({'figure.autolayout': True})

def print_map(h_map):
    for k in h_map:
        print(f"{k} :   {h_map[k]}")

def group_plot(data, data_key, fig_name):
    df = pd.DataFrame(data, columns=data_key)
    df.pivot(data_key[1], data_key[0], data_key[2]).plot(kind='bar', figsize=(15,10))
    if not os.path.isdir('../../Figures/'):
        os.makedirs('../../Figures/')
    plt.savefig('../../Figures/' + fig_name)
