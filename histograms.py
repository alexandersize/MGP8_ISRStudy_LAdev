from matplotlib import pyplot as plt
from matplotlib import cm
from matplotlib.colors import LightSource
import numpy as np
import ROOT
import array
import os
import pandas as pd
from ctypes import c_double
import re
import sys
import seaborn

def errorbar_ratioplot(mass, bins, mgpath, pythiapath, outputpath):
    '''
    :param mass: Gluino mass (GeV)
    :param bins: List of bins in the histogram
    :param mgpath: Path to the madgraph root file
    :param pythiapath: Path to the pythia root file
    :param outputpath: Filepath to save the ROOT file
    :return: ROOT file with the ratio systematic errors
    '''
    #Define the number of madgraph histograms that exist
    n_weights = 45

    #Open ROOT files
    pyfile = ROOT.TFile.Open(pythiapath)
    mgfile = ROOT.TFile.Open(mgpath)

    #Iterate through all madgraph histograms, return one numpy array with all max bins values + errors, another with all min values + errors
    pythiahist = pyfile.Get("pTsum;1")
    pythiahist.Scale(1. / pythiahist.Integral())
    pythiahist_rebinned = rebin(pythiahist, bins)
    mins, maxes = np.repeat(10000000., len(bins)-1), np.zeros(len(bins)-1)
    min_errors, max_errors = np.zeros(len(bins) - 1), np.zeros(len(bins) - 1)
    zeroth = 0
    for i in range(n_weights):
        mghist = mgfile.Get("pTsum {};1".format(i))
        mghist.Scale(1. / mghist.Integral())
        mghist_rebinned = rebin(mghist, bins)
        if i == 0:
            zeroth = mghist_rebinned
        for bin in range(len(bins)-1):
            n_entries_in_bin = mghist_rebinned.GetBinContent(bin+1)
            error = mghist_rebinned.GetBinError(bin+1)
            if n_entries_in_bin < mins[bin]:
                mins[bin] = n_entries_in_bin
                min_errors[bin] = error
            if n_entries_in_bin > maxes[bin]:
                maxes[bin] = n_entries_in_bin
                max_errors[bin] = error

    #Create the min/max histograms
    min_hist, max_hist = create_min_max_hists(bins, mins, maxes, min_errors, max_errors)

    #Get the min/max ratio plots (TGraphAsymmErrors)
    min_ratio = ROOT.TGraphAsymmErrors(min_hist, pythiahist_rebinned, "pois")
    max_ratio = ROOT.TGraphAsymmErrors(max_hist, pythiahist_rebinned, "pois")
    zeroth_ratio = ROOT.TGraphAsymmErrors(zeroth, pythiahist_rebinned, "pois")

    #Convert the TGraph ratios to histograms
    #min_ratio_hist = pythiahist_rebinned.Clone("MG/Pythia Ratio Minimum")
    #max_ratio_hist = pythiahist_rebinned.Clone("MG/Pythia Ratio Maximum")
    #zeroth_ratio_hist = pythiahist_rebinned.Clone("MG/Pythia Ratio Nominal")
    #ratioHistFill(min_ratio, min_ratio_hist, bins)
    #ratioHistFill(max_ratio, max_ratio_hist, bins)
    #ratioHistFill(zeroth_ratio, zeroth_ratio_hist, bins)

    #Create systematic error plot
    zeroth_ratio_sys = zeroth_ratio.Clone("MG/Pythia Ratio Systematic Errors")
    setSystematicErrors(zeroth_ratio_sys, min_ratio, max_ratio, bins)

    #Write to the ROOT file
    outputFile = ROOT.TFile(outputpath + ".root", 'RECREATE')
    zeroth_ratio.SetTitle("MG N={}, Pythia N={}, Stat Errors;gluglu pT (GeV);MG/Pythia".format(zeroth.GetEntries(), pythiahist_rebinned.GetEntries()))
    zeroth_ratio_sys.SetTitle("MG N={}, Pythia N={}, Systematic Errors;gluglu pT (GeV);MG/Pythia".format(zeroth.GetEntries(), pythiahist_rebinned.GetEntries()))
    zeroth_ratio.Write("mg_py_stat")
    zeroth_ratio_sys.Write("mg_py_sys")
    outputFile.Write()
    outputFile.Close()



def create_min_max_hists(bins, mindata, maxdata, minerrors, maxerrors):
    '''
    :param bins: List of bins to set the histograms
    :param mindata: Numpy array of min weights for each bin
    :param maxdata: Numpy array of max weights for each bin
    :param minerrors: Numpy array of errors for each minimum bin
    :param maxerrors: Numpy array of errors for each maximum bin
    :return: Minimum and maximum histograms
    '''
    #Create the raw histograms
    min_hist = ROOT.TH1F("Minimum Madgraph", "Minimum Madgraph", len(bins)-1, array.array('d', bins))
    max_hist = ROOT.TH1F("Maximum Madgraph", "Maximum Madgraph", len(bins)-1, array.array('d', bins))
    min_hist.GetXaxis().SetLimits(min(bins), max(bins))
    max_hist.GetXaxis().SetLimits(min(bins), max(bins))

    #Fill the histograms with the data
    for i in range(len(mindata)):
        min_hist.SetBinContent(i+1, mindata[i])
        min_hist.SetBinError(i+1, minerrors[i])
    for i in range(len(maxdata)):
        max_hist.SetBinContent(i+1, maxdata[i])
        max_hist.SetBinError(i+1, maxerrors[i])

    return min_hist, max_hist


def rebin(histogram, new_bins):
    '''
    :param histogram: Input TH1F histogram you would like to rebin
    :param new_bins: New bins to transform the histogram into
    :return: Returns new TH1F histogram with transformed bins
    '''
    newHist = histogram.Clone("newHistogram")
    double_type_bins = array.array('d', new_bins) #This fixes an error concering the type of the bins
    newHist = newHist.Rebin(len(new_bins)-1, "newHistogram", double_type_bins)

    return newHist


def ratioHistFill(ratioTempGraph, ratioHist, bins):
    '''
    :param ratioTempGraph: TRatioPlot
    :param ratioHist: TH1F with the expected format
    :param bins: Bins of the histogram
    :return: Fills a histogram with the ratio information
    '''
    for bin in range(len(bins)-1):
        x, y = c_double(1.), c_double(1.)
        y_error = ratioTempGraph.GetErrorY(bin)
        ratioTempGraph.GetPoint(bin, x, y)
        ratioHist.SetBinContent(ratioHist.FindBin(x.value), y.value)
        ratioHist.SetBinError(ratioHist.FindBin(x.value), y_error)


def setSystematicErrors(zeroth_ratio, min_ratio, max_ratio, bins):
    '''
    :param zeroth_ratio: TGraphAssymErrors plot for the zeroth ratio
    :param min_ratio: TGraphAssymErrors plot for the min ratio
    :param max_ratio: TGraphAssymErrors plot for the max ratio
    :param bins: Bins used in the plots
    :return: TGraphAssymErrors plot for the zeroth ratio with the systematic errors
    '''
    zeroth_y = zeroth_ratio.GetY()
    min_y = min_ratio.GetY()
    max_y = max_ratio.GetY()
    for bin in range(len(bins)-1):
        y_err_high = max_y[bin] - zeroth_y[bin]
        y_err_low = zeroth_y[bin] - min_y[bin]
        zeroth_ratio.SetPointEYhigh(bin, y_err_high)
        zeroth_ratio.SetPointEYlow(bin, y_err_low)


def fillcsv(rootpaths, bins):
    '''
    :param rootpaths: List of paths to ratio root files
    :param bins: Bins used in the ratio plots
    :return: Saves a csv containing the relevant information
    '''
    dictionary = {'mass': [], 'pT': [], 'ratio': [], 'stat': [], 'sysup': [], 'sysdown': [], 'delta': []}
    for root in rootpaths:
        mass = re.search(r'(\d+)GeV', root).group(1)
        file = ROOT.TFile.Open(root)
        stathist = file.Get('mg_py_stat')
        syshist = file.Get('mg_py_sys')
        x_values = stathist.GetX()
        y_values = stathist.GetY()
        for bin in range(len(bins)-1):
            ratio = y_values[bin]
            sysup = syshist.GetErrorYhigh(bin)
            sysdown = syshist.GetErrorYlow(bin)

            dictionary['mass'].append(mass)
            dictionary['pT'].append(x_values[bin])
            dictionary['ratio'].append(ratio)
            dictionary['stat'].append(stathist.GetErrorY(bin))
            dictionary['sysup'].append(sysup)
            dictionary['sysdown'].append(sysdown)

            #Check if the ratio + systematic error encapsulates 1. If so, return delta = 0. Otherwise, return the magnitude of the difference
            if ratio >= 1:
                dictionary['delta'].append((ratio - 1)/sysdown)
            else:
                dictionary['delta'].append((1 - ratio)/sysup)

    df = pd.DataFrame(dictionary)
    df.to_csv('ratio_information.csv', index=False)


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
    surf = ax.plot_surface(x, y, z, rstride=1, cstride=1, facecolors=rgb,
                           linewidth=0, antialiased=False, shade=False)

    plt.show()


def heatmap(csvpath, statistic='ratio'):
    '''
    :param csvpath: Path to the csv file created in the fillcsv function
    :param statistic: Statistic to plot on the z-axis. Can be one of four options: 'ratio' (defualt), 'stat', 'sysup', 'sysdown', or 'delta'.
                      These are 5 of the columns in the csv. pT and mass are plotted on the x and y axes respectively.
    :return: Creates a heatmap with the chosen statistic on the color scale, pT on the x-axis, and mass on the y-axis.
    '''
    #Check if statistic is an allowed option
    allowed_options = ['ratio', 'stat', 'sysup', 'sysdown', 'delta']
    if statistic not in allowed_options:
        print("Error: statistic must be one of the five options: 'ratio' (defualt), 'stat', 'sysup', 'sysdown', or 'delta'.")
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

    #Define z axis label
    if statistic == 'ratio':
        zlabel = 'MG/Pythia Ratio'
    elif statistic == 'stat':
        zlabel = 'Statistical Uncertainty'
    elif statistic == 'sysup':
        zlabel = 'Upper Systematic Uncertainty'
    elif statistic == 'sysdown':
        zlabel = 'Lower Systematic Uncertainty'
    else:
        zlabel = 'Sigma Away From 1'

    #Plot the data
    ax = seaborn.heatmap(z, cmap='coolwarm', xticklabels=x, yticklabels=y, cbar_kws={'label': zlabel})
    ax.invert_yaxis()
    plt.xticks(rotation=45)
    plt.xlabel('Di-Gluino pT (GeV)')
    plt.ylabel('Gluino Mass (GeV)')
    plt.show()
    #plt.savefig("histograms/" + statistic + "_heatmap.png")

def stackplot_ratios(csvpath, figpath=None, statistical=True, masses=None, error_bands=False):
    '''
    :param csvpath: Path to the csv file created in the fillcsv function
    :param figpath: Path to save the plot, if None just shows the plot
    :param statistical: If true, plots the stat errorbars, if false, plots the systematic errorbars
    :param masses: Allows for plotting of custom masses
    :param error_bands: If true, plots the error bands
    :return: Root file containing the ratio stat plots of each mass on one plot
    '''
    df = pd.read_csv(csvpath)
    if masses == None:
        masses = df['mass'].unique()

    if statistical:
        error = 'Statistical'
    else:
        error = 'Systematic'

    colors = {1000: 'dodgerblue', 1400: 'lightskyblue', 1600: 'paleturquoise', 1800: 'gainsboro', 2000: 'peachpuff', 2200: 'coral', 2400: 'orangered', 2600: 'indianred'}
    edgecolors = {1000: 'steelblue', 1400: 'deepskyblue', 1600: 'mediumturquoise', 1800: 'silver', 2000: 'sandybrown', 2200: 'tomato', 2400: 'red', 2600: 'firebrick'}
    alphas = {1000: 0.5, 1400: 0.5, 1600: 0.75, 1800: 0.75, 2000: 0.75, 2200: 0.75, 2400: 0.5, 2600: 0.5}
    for mass in masses:
        subdf = df[df['mass'] == mass]
        if error_bands:
            plt.plot(subdf['pT'], subdf['ratio'], label="{} GeV".format(mass), alpha=0.25, color=colors[mass])
            if statistical:
                yplus = np.add(subdf['ratio'], subdf['stat'])
                yminus = np.subtract(subdf['ratio'], subdf['stat'])
            else:
                yplus = np.add(subdf['ratio'], subdf['sysup'])
                yminus = np.subtract(subdf['ratio'], subdf['sysdown'])
            plt.fill_between(subdf['pT'], yplus, yminus, alpha=alphas[mass], antialiased=True, color=colors[mass], edgecolor=edgecolors[mass])
        else:
            if statistical:
                plt.errorbar(subdf['pT'], subdf['ratio'], subdf['stat'], capsize=5, label="{} GeV".format(mass), alpha=0.75, color=colors[mass])
            else:
                plt.errorbar(subdf['pT'], subdf['ratio'], (subdf['sysdown'], subdf['sysup']), capsize=5, label="{} GeV".format(mass), alpha=0.75, color=colors[mass])
    plt.xlabel('pT (GeV)')
    plt.ylabel('MG/Pythia')
    plt.suptitle('Mass Ratios with {} Uncertainties'.format(error))
    plt.legend()
    if figpath == None:
        plt.show()
    else:
        plt.savefig(figpath)


masses = [1000, 1400, 1600, 1800, 2000, 2200, 2400, 2600]
new_bins = [0,50,100,150,200,250,300,350,450,550,650,800,950,1150,1450,2800]
cwd = os.getcwd()

###Plot the ratio plots###
#mg_rootpath_base = cwd + "/output-files/gluglu_MGn50_GeV"
#pythia_rootpath_base = cwd + "/output-files/pythia-M-"
#for i in range(len(masses)):
#    mgpath = mg_rootpath_base + "{}.root".format(masses[i])
#    pypath = pythia_rootpath_base + "{}.root".format(masses[i])
#    errorbar_ratioplot(masses[i], new_bins, mgpath, pypath, 'histograms/mg-py_ratio-{}GeV'.format(masses[i]))

###Fill ratio information to csv###
#ratio_rootpaths = []
#for mass in masses:
#    ratio_rootpaths.append(cwd + "/histograms/mg-py_ratio-{}GeV.root".format(mass))
#fillcsv(ratio_rootpaths, new_bins)

###Create the heatmap###
#heatmap(cwd + "/ratio_information.csv", statistic='ratio')

###Create the ratio stackplot###
stackplot_ratios(cwd + "/ratio_information.csv", figpath=None, statistical=True, masses=[1000,2600], error_bands=True)