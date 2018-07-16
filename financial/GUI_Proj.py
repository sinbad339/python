#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      jdilorenzo
#
# Created:     01/02/2018
# Copyright:   (c) jdilorenzo 2018
# Licence:     <your licence>
#-------------------------------------------------------------------------------
import sys
import csv
import copy
from copy import deepcopy

import datetime
from datetime import date,timedelta
from dateutil.parser import parse
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from math import *
from pylab import *
import random
from Tkinter import *
import Tkinter as tk

from ret_states import *
from plotter import *

fields = 'Name', 'Qual Contr', 'Non-Q Cont', 'Birthday', 'Retirement Age', 'Take Home'
common_fields = 'Trial Name', 'Start Date', 'Avg Return', 'Return SD', 'CPI', 'Proj Expenses', 'Collect SS Date', 'Annual SS Benefit', 'Healthcare Exp', 'Healthcare CPI', 'Qual Total', 'NonQ Total', 'Liab @ Ret'

def my_quit():
    root.destroy()  # code to exit

def save_base(entries):

    wr_tuple = []

    for entry in entries:
        field = entry[0]
        text  = entry[1].get()
        text2 = entry[2].get()
        wr_tuple.append((field, text, text2))

    res_f = open('fin_base.sav', "wb")
    writer = csv.writer(res_f)
    writer.writerows(wr_tuple)
    res_f.close()

    return()

def load_base(entries):

   doub_flds = 6    #this is lame

   index = 1
   with open('fin_base.sav', 'r') as f:
      reader = csv.reader(f)
      for entry in entries:
         row = next(reader)
         entry[1].delete(0,END)
         entry[1].insert(0,row[1])
         if index <= doub_flds:
            entry[2].delete(0,END)
            entry[2].insert(0,row[2])
         index += 1

   return entries

def fetch(entries, timeline, new_tax):

    for entry in entries:
        field = entry[0]
        text  = entry[1].get()
        text2 = entry[2].get()
        print('%s: "%s", "%s"' % (field, text, text2))

    print 'Tax rate is ', new_tax

    name1 = entries[0][1].get()
    name2 = entries[0][2].get()
    qual_cont = float(entries[1][1].get().replace("$","").replace(",",""))
    qual_cont += float(entries[1][2].get().replace("$","").replace(",",""))
    nonq_cont = float(entries[2][1].get().replace("$","").replace(",",""))
    nonq_cont += float(entries[2][2].get().replace("$","").replace(",",""))
    bd1 = parse(entries[3][1].get())
    bd2 = parse(entries[3][2].get())
    ret1 = float(entries[4][1].get())
    ret2 = float(entries[4][2].get())
    takehome1 = float(entries[5][1].get().replace("$","").replace(",",""))
    takehome2 = float(entries[5][2].get().replace("$","").replace(",",""))

    trial = entries[6][1].get()
    start_date = parse(entries[7][1].get())
    avg_ret = float(entries[8][1].get().strip('%'))/100
    sd_ret = float(entries[9][1].get().strip('%'))/100
    cpi = float(entries[10][1].get().strip('%'))/100
    proj_exp = float(entries[11][1].get().replace("$","").replace(",",""))
    file_ss = parse(entries[12][1].get())
    soc_sec = float(entries[13][1].get().replace("$","").replace(",",""))
    hc = float(entries[14][1].get().replace("$","").replace(",",""))
    hc_cpi = float(entries[15][1].get().strip('%'))/100
    qual_tot = float(entries[16][1].get().replace("$","").replace(",",""))
    nonq_tot = float(entries[17][1].get().replace("$","").replace(",",""))
    liabilities = float(entries[18][1].get().replace("$","").replace(",",""))

##    ret_list = [avg_ret for i in range(50)]
    sd_ret = 0

    next_row = state0(entries, timeline, sd_ret)
    next_row = state1(next_row, entries, timeline, sd_ret)
    next_row = state2(next_row, entries, timeline, sd_ret, new_tax)
    next_row = state3(next_row, entries, timeline, sd_ret, new_tax)

    base_plot(next_row, ents, timeline)

    return()

def probab(entries, timeline, new_tax):
    name1 = entries[0][1].get()
    name2 = entries[0][2].get()
    qual_cont = float(entries[1][1].get().replace("$","").replace(",",""))
    qual_cont += float(entries[1][2].get().replace("$","").replace(",",""))
    nonq_cont = float(entries[2][1].get().replace("$","").replace(",",""))
    nonq_cont += float(entries[2][2].get().replace("$","").replace(",",""))
    bd1 = parse(entries[3][1].get())
    bd2 = parse(entries[3][2].get())
    ret1 = float(entries[4][1].get())
    ret2 = float(entries[4][2].get())
    takehome1 = float(entries[5][1].get().replace("$","").replace(",",""))
    takehome2 = float(entries[5][2].get().replace("$","").replace(",",""))

    trial = entries[6][1].get()
    start_date = parse(entries[7][1].get())
    avg_ret = float(entries[8][1].get().strip('%'))/100
    sd_ret = float(entries[9][1].get().strip('%'))/100
    cpi = float(entries[10][1].get().strip('%'))/100
    proj_exp = float(entries[11][1].get().replace("$","").replace(",",""))
    file_ss = parse(entries[12][1].get())
    soc_sec = float(entries[13][1].get().replace("$","").replace(",",""))
    hc = float(entries[14][1].get().replace("$","").replace(",",""))
    hc_cpi = float(entries[15][1].get().strip('%'))/100
    qual_tot = float(entries[16][1].get().replace("$","").replace(",",""))
    nonq_tot = float(entries[17][1].get().replace("$","").replace(",",""))
    liabilities = float(entries[18][1].get().replace("$","").replace(",",""))

##    ret_list = [avg_ret for i in range(50)]

    next_row = state0(entries, timeline, 0)
    next_row = state1(next_row, entries, timeline, 0)
    next_row = state2(next_row, entries, timeline, 0, new_tax)
    next_row = state3(next_row, entries, timeline, 0, new_tax)

    nom_tl = deepcopy(timeline)
    nom_last_row = next_row - 1
    worst_tl = deepcopy(timeline)
    worst_lst = [i[1] for i in nom_tl]
    worst_val = next((index for index,value in enumerate(worst_lst) if value < 0), 47)
    worst_end = nom_tl[worst_val][1]
    worst_date = nom_tl[worst_val][0]
    fails = 0
    passes = 0

##    ret_list = [[random.gauss(avg_ret, sd_ret) for j in range(1000)] for i in range(50)]

    for mc_cnt in range(1000):
        next_row = state0(entries, timeline, sd_ret)
        next_row = state1(next_row, entries, timeline, sd_ret)
        next_row = state2(next_row, entries, timeline, sd_ret, new_tax)
        next_row = state3(next_row, entries, timeline, sd_ret, new_tax)

        if timeline[32][1] < 0:
            fails += 1
        else:
            passes += 1

        worst_lst = [i[1] for i in timeline]
        val = next((index for index,value in enumerate(worst_lst) if value < 0), 47)
        if val < worst_val:
            worst_tl = deepcopy(timeline)
            worst_end = nom_tl[val][1]
            worst_date = nom_tl[val][0]
            worst_val = val

        plt_dates = []
        plt_total = []
        for my_row in range(0,next_row):
            plt_dates.append((date2num(timeline[my_row][0]) - date2num(bd1))/365.25)
            plt_total.append(timeline[my_row][1] + timeline[my_row][2])
        plt.figure(0)
        plt.plot(plt_dates,plt_total, '-', color=(0.5, 0.5, 0.5), linewidth=1)

    print 'Total passes is ', passes
    print 'Total failes is ', fails

    plt_total = []
    for my_row in range(0,next_row):
        plt_total.append(worst_tl[my_row][1] + worst_tl[my_row][2])
    plt.figure(0)
    plt.plot(plt_dates,plt_total, '.r-', linewidth=2)

    plt_total = []
    plt_dates = []
    for my_row in range(0,next_row):
        plt_total.append(nom_tl[my_row][1] + nom_tl[my_row][2])
        plt_dates.append((date2num(timeline[my_row][0]) - date2num(bd1))/365.25)
    plt.figure(0)
    plt.plot(plt_dates,plt_total, '.b-', linewidth=2)
    title_str = trial + ' \nConfidence to not be broke @ 90 is ' + str(float(passes)/10) +'%'

    grid(True)
    xgridlines = getp(gca(), 'xgridlines')
    ygridlines = getp(gca(), 'ygridlines')
    xlabel('Age')
    ylabel('$')
    axes = plt.gca()
    axes.set_ylim([0,5000000])
    plt.gcf().set_size_inches(12, 5.3)
    plt.title(title_str)
    plt.legend()
    plt.draw()

    plt.ioff()

    plt.show()      # blocking!

    return()

def makeform(root, fields):
   entries = []
   doub_flds = 6    #this is lame

   for field in fields:
      row = Frame(root)
      lab = Label(row, width=15, text=field, anchor='w')
      ent = Entry(row)
      ent2 = Entry(row)
      row.pack(side=TOP, fill=X, padx=15, pady=5)
      lab.pack(side=LEFT)
      ent.pack(side=LEFT, expand=YES, fill=X)
      ent2.pack(side=RIGHT, expand=YES, fill=X)
      entries.append((field, ent, ent2))

   for field in common_fields:
      row = Frame(root)
      lab = Label(row, width=15, text=field, anchor='w')
      ent = Entry(row)
      row.pack(side=TOP, fill=X, padx=15, pady=5)
      lab.pack(side=LEFT)
      ent.pack(side=LEFT, expand=YES, fill=X)
      entries.append((field, ent, ent))

   index = 1
   with open('fin_base.sav', 'r') as f:
      reader = csv.reader(f)
      for entry in entries:
         row = next(reader)
         entry[1].insert(0,row[1])
         if index <= doub_flds:
            entry[2].insert(0,row[2])
         index += 1

   return entries

def ShowTax():
    print"Selected tax is ", new_tax.get()

if __name__ == '__main__':

   timeline = [[0 for j in range(11)] for i in range(50)]

   root = Tk()
   root.title("Interactive Retirement Projector")

   new_tax = tk.IntVar()

   ents = makeform(root, fields)

   b1 = tk.Button(root, text='Show Baseline',
          command=(lambda e=ents: fetch(e, timeline, new_tax.get())))
   b1.pack(side=LEFT, padx=5, pady=5)
##   b1.grid(row=0, column=0)

   b4 = tk.Button(root, text='Prbability',
          command=(lambda e=ents: probab(e, timeline, new_tax.get())))
   b4.pack(side=LEFT, padx=5, pady=5)
##   b4.grid(row=1, column=0)

   b2 = tk.Button(root, text='Save Baseline',
          command=(lambda e=ents: save_base(e)))
   b2.pack(side=LEFT, padx=5, pady=5)
##   b2.grid(row=0, column=1)

   b3 = tk.Button(root, text='Load Baseline',
          command=(lambda e=ents: load_base(e)))
   b3.pack(side=LEFT, padx=5, pady=5)
##   b3.grid(row=1, column=1)

   button = tk.Button(root,
                      text="QUIT",
                      fg="red",
                      command=my_quit)

   button.pack(side=tk.LEFT)

   C1 = Checkbutton(root, text = "Tax Cuts and Jobs Act of 2017", variable = new_tax, \
                 onvalue = 1, offvalue = 0, height=5, width = 30, command=ShowTax)
   C1.pack()

   root.mainloop()
