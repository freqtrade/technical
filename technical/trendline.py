"""
defines trendline based indicator logic
based on
https://github.com/dysonance/Trendy
"""


import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

def gentrends(dataframe, field="close", window=1 / 3.0, charts=False):
    x = np.array(dataframe[field])

    if window < 1:
        window = int(window * len(x))

    max1_idx = np.argmax(x)
    min1_idx = np.argmin(x)

    max1 = x[max1_idx]
    min1 = x[min1_idx]

    if max1_idx + window >= len(x):
        max2 = np.max(x[0 : (max1_idx - window)])
    else:
        max2 = np.max(x[(max1_idx + window) :])

    if min1_idx - window <= 0:
        min2 = np.min(x[(min1_idx + window) :])
    else:
        min2 = np.min(x[0 : (min1_idx - window)])

    max2_idx = np.where(x == max2)[0][0]
    min2_idx = np.where(x == min2)[0][0]

    maxslope = (max1 - max2) / (max1_idx - max2_idx)
    minslope = (min1 - min2) / (min1_idx - min2_idx)
    a_max = max1 - (maxslope * max1_idx)
    a_min = min1 - (minslope * min1_idx)
    b_max = max1 + (maxslope * (len(x) - max1_idx))
    b_min = min1 + (minslope * (len(x) - min1_idx))
    maxline = a_max + np.arange(len(x)) * maxslope
    minline = a_min + np.arange(len(x)) * minslope

    trends = pd.DataFrame(
        {"Data": x, "Max Line": maxline, "Min Line": minline}
    )

    if charts:
        plt.plot(trends)
        plt.grid()

        if isinstance(charts, str):
            plt.savefig(f"{charts}.png")
        else:
            plt.savefig(f"{x[0]}_{x[-1]}.png")

    plt.close()

    return trends

def segtrends(dataframe, field="close", segments=2, charts=False):
    x = np.array(dataframe[field])

    segments = int(segments)
    segsize = len(x) // segments
    maxima = np.array([np.max(x[i:i+segsize]) for i in range(0, len(x), segsize)])
    minima = np.array([np.min(x[i:i+segsize]) for i in range(0, len(x), segsize)])

    x_maxima = np.array([np.argmax(x[i:i+segsize]) + i for i in range(0, len(x), segsize)])
    x_minima = np.array([np.argmin(x[i:i+segsize]) + i for i in range(0, len(x), segsize)])

    if charts:
        plt.plot(x)
        plt.grid()

    for i in range(segments - 1):
        maxslope = (maxima[i + 1] - maxima[i]) / (x_maxima[i + 1] - x_maxima[i])
        a_max = maxima[i] - (maxslope * x_maxima[i])
        b_max = maxima[i] + (maxslope * (len(x) - x_maxima[i]))
        maxline = a_max + np.arange(len(x)) * maxslope

        minslope = (minima[i + 1] - minima[i]) / (x_minima[i + 1] - x_minima[i])
        a_min = minima[i] - (minslope * x_minima[i])
        b_min = minima[i] + (minslope * (len(x) - x_minima[i]))
        minline = a_min + np.arange(len(x)) * minslope

        if charts:
            plt.plot(maxline, "g")
            plt.plot(minline, "r")

    if charts:
        plt.show()

    trends = pd.DataFrame(
        {"Data": x, "Max Line": maxline, "Min Line": minline}
    )

    return trends
