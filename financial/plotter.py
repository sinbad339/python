#-------------------------------------------------------------------------------
# Name:        Plotter
# Purpose:
#
# Author:      jdilorenzo
#
# Created:     14/02/2018
# Copyright:   (c) jdilorenzo 2018
# Licence:     <your licence>
#-------------------------------------------------------------------------------
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from math import *
from pylab import *

import datetime
from datetime import date,timedelta
from dateutil.parser import parse

def base_plot(next_row, entries, timeline):

    bd1 = parse(entries[3][1].get())
    trial = entries[6][1].get()

    plt_total = []
    plt_dates = []
    plt_total.append(0)
    plt_dates.append(58)
    for my_row in range(0,next_row):
        plt_total.append(timeline[my_row][1] + timeline[my_row][2])
        plt_dates.append((date2num(timeline[my_row][0]) - date2num(bd1))/365.25)
    plt_total.append(0)
    plt_dates.append(86)
    plt.figure(0)
    plt.fill(plt_dates,plt_total, '.r-')

    plt_total = []
    plt_dates = []
    plt_total.append(0)
    plt_dates.append(58)
    for my_row in range(0,next_row):
        plt_total.append(timeline[my_row][1])
        plt_dates.append((date2num(timeline[my_row][0]) - date2num(bd1))/365.25)
    plt_total.append(0)
    plt_dates.append(86)
    plt.figure(0)
    plt.fill(plt_dates,plt_total, '.b-')
    title_str = trial

    grid(True)
    xgridlines = getp(gca(), 'xgridlines')
    ygridlines = getp(gca(), 'ygridlines')
    xlabel('Age')
    ylabel('$')
    axes = plt.gca()
    axes.set_ylim([0,2000000])
    plt.gcf().set_size_inches(12, 5.3)
    plt.title(title_str)
    plt.legend()
    plt.draw()

    plt.ioff()
    fig_name = 'figure -0.png'

    plt.savefig(fig_name)
    plt.show()      # blocking!

