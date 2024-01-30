import os

from matplotlib import pyplot as plt
from matplotlib import cm
from matplotlib.colors import LightSource
import numpy as np
import pandas as pd
import sys

def plot3D(csvpath, statistic='ratio'):
    '''
    :param csvpath: Path to the csv file created in the fillcsv function
    :param statistic: Statistic to plot on the z-axis. Can be one of four options: 'ratio' (defualt), 'stat', 'sysup', or 'sysdown'.
                      These are 4 of the columns in the csv. pT and mass are plotted on the x and y axes respectively.
    :return: Creates a 3D plot with the chosen statistic on the z-axis, pT on the x-axis, and mass on the y-axis.
    '''
    #Check if statistic is an allowed option
    allowed_options = ['ratio', 'stat', 'sysup', 'sysdown']
    if statistic not in allowed_options:
        print("Error: statistic must be one of the four options: 'ratio' (defualt), 'stat', 'sysup', or 'sysdown'.")
        sys.exit()

    #Clean the data
    df = pd.read_csv(csvpath)
    x, y, z_df = list(set(df['pT'])), list(set(df['mass'])), df.groupby('mass')[statistic].apply(list).reset_index()[statistic]
    l = []
    for arr in z_df:
        l.append(arr)
    z = np.array(l)
    x.sort()
    y.sort()
    x, y = np.meshgrid(x, y)

    #Define z axis label
    if statistic == 'ratio':
        zlabel = 'MG/Pythia Ratio'
    elif statistic == 'stat':
        zlabel = 'Statistical Uncertainty'
    elif statistic == 'sysup':
        zlabel = 'Upper Systematic Uncertainty'
    else:
        zlabel = 'Lower Systematic Uncertainty'

    #Plot the data
    fig, ax = plt.subplots(subplot_kw=dict(projection='3d'))
    plt.xlabel('Di-Gluino pT (GeV)')
    plt.ylabel('Gluino Mass (GeV)')
    ax.set_zlabel(zlabel)
    ls = LightSource(270, 45)
    rgb = ls.shade(z, cmap=cm.gist_earth, vert_exag=0.1, blend_mode='soft')
    #surf = ax.plot_surface(x, y, z, rstride=1, cstride=1, facecolors=rgb,
    #                       linewidth=0, antialiased=False, shade=False)
    ax.bar3d(x, y, z, 50, 150, 0.1, zsort='average')

    plt.show()

cwd = os.getcwd()
plot3D(cwd + "/ratio_information.csv", statistic='ratio')