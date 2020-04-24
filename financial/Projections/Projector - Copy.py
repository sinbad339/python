#-------------------------------------------------------------------------------
# Name:        Laurel Tree
# Purpose:
#
# Author:      jdilorenzo
#
# Created:     20/10/2017
# Copyright:   (c) jdilorenzo 2017
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

#--------------------------------------------------------
# Calculate Income Taxes
#-------------------------------------------------------
def calc_taxes(income):
    if new_tax == 0:
        taxable = income - 13000    # standard deduction

        if taxable > 0:
            taxes = min(taxable, 18550)*0.1
        else:
            taxes = 0

        if taxable > 18550:
            taxes += (min(taxable, 75300)-18550)*0.15

        if taxable > 75300:
            taxes += (min(taxable, 151900)-75300)*0.25

        if taxable > 151900:
            taxes += (min(taxable, 231450)-151900)*0.28

        if taxable > 231450:
            taxes += (min(taxable,413350)-231450)*0.33

        if taxable > 413350:
            taxes += (min(taxable,466950) - 413350)*0.35

        if taxable > 466950:
            taxes += (taxable - 466950)* 0.396

    else:   # new_tax == 1

        taxable = income - 24000    # standard deduction

        if taxable > 0:
            taxes = min(taxable, 19050)*0.1
        else:
            taxes = 0

        if taxable > 19050:
            taxes += (min(taxable, 77400)-19050)*0.12

        if taxable > 77400:
            taxes += (min(taxable, 165000)-77400)*0.22

        if taxable > 165000:
            taxes += (min(taxable, 315000)-165000)*0.24

        if taxable > 315000:
            taxes += (min(taxable - 400000)-315000)*0.32

        if taxable > 400000:
            taxes += (min(taxable,600000) - 400000)*0.35

        if taxable > 600000:
            taxes += (taxable - 400000)* 0.37

    return(taxes)

#-------------------------------------------------------------------------------
# state 0 is our current state of
# Both employed and fully contributing to retirement accounts
#-------------------------------------------------------------------------------
def state0():
    global timeline

    state0_end = mar_bd + datetime.timedelta(days = mar_ret*365.25)

    timeline[0][0] = start_date
    timeline[0][1] = qual_tot
    timeline[0][2] = nonq_tot
    timeline[0][3] = 0      #SS income
    timeline[0][4] = 0      #Expenses
    timeline[0][5] = 0      #NQ Taxable Income
    timeline[0][6] = 0      #Q Taxable Income
    timeline[0][7] = 0      #Taxes
    timeline[0][8] = 0      #Healthcare
    age = timeline[0][0] - jon_bd
    timeline[0][9] = age.days/365.25
    timeline[0][10] = timeline[0][4] + timeline[0][7] + timeline[0][8]
    timeline[0][11] = 0     #RMD

    row_cnt = 1

    my_date = start_date + datetime.timedelta(days = 365.25)

    cum_cpi = 1
    ret_index = my_date.year - start_date.year - 1
    for i in range(ret_index + 1):
        cum_cpi = cum_cpi * (1 + cpi_list[i] [mc_cnt])

    while my_date <= state0_end:
##        act_ret = random.gauss(avg_ret, sd_ret)
        ret_index = my_date.year - start_date.year - 1
        act_ret = ret_list[ret_index] [mc_cnt]
        act_cpi = cpi_list[ret_index] [mc_cnt]
        delta_time = my_date - start_date
        timeline[row_cnt][0] = my_date
        timeline[row_cnt][1] = timeline[row_cnt-1][1]*(1+act_ret) + (cont_403b + cont_401k)
        timeline[row_cnt][2] = timeline[row_cnt-1][2]*(1+act_ret) + (cont_espp + cont_rsu)
        timeline[row_cnt][3] = 0      #SS income
        timeline[row_cnt][4] = 0      #Expenses
        timeline[row_cnt][5] = 0      #NQ Taxable Income
        timeline[row_cnt][6] = 0      #Q Taxable Income
        timeline[row_cnt][7] = 0      #Taxes
        timeline[row_cnt][8] = 0      #Healthcare
        age = timeline[row_cnt][0] - jon_bd
        timeline[row_cnt][9] = age.days/365.25
        timeline[row_cnt][10] = timeline[row_cnt][4] + timeline[row_cnt][7] + timeline[row_cnt][8]
        timeline[row_cnt][11] = 0       #RMD
        row_cnt = row_cnt + 1
        my_date = my_date + datetime.timedelta(days = 365.25)

    timeline[row_cnt][0] = state0_end
    age = timeline[row_cnt][0] - jon_bd
    timeline[row_cnt][9] = age.days/365.25
    timeline[row_cnt][10] = timeline[row_cnt][4] + timeline[row_cnt][7] + timeline[row_cnt][8]
    timeline[row_cnt][11] = 0       #RMD
##    act_ret = random.gauss(avg_ret, sd_ret)
    ret_index = my_date.year - start_date.year - 1
    act_ret = ret_list[ret_index] [mc_cnt]
    act_cpi = cpi_list[ret_index] [mc_cnt]
    delta_time = state0_end - (my_date - datetime.timedelta(days = 365.25))
##    jjd = delta_time.days/365.25
    timeline[row_cnt][1] = timeline[row_cnt-1][1]*((1+act_ret)**(delta_time.days/365.25)) + (cont_403b + cont_401k)*delta_time.days/365.25
    timeline[row_cnt][2] = timeline[row_cnt-1][2]*((1+act_ret)**(delta_time.days/365.25)) + (cont_espp + cont_rsu)*delta_time.days/365.25

    return(row_cnt + 1)

#-------------------------------------------------------------------------------
# state 1 is Martha retired, me working and contributing tomy accounts
# Expenses are to make up for Martha's take-home pay.
#-------------------------------------------------------------------------------
def state1(row_cnt):
    global timeline

    state1_end = jon_bd + datetime.timedelta(days = jon_ret*365.25)

    my_date = timeline[row_cnt-1][0] + datetime.timedelta(days = 365.25)
    delta_time = my_date - start_date
    ret_index = my_date.year - start_date.year - 1
    cum_cpi = 1
    for i in range(ret_index + 1):
        cum_cpi = cum_cpi * (1 + cpi_list[i] [mc_cnt])
    expenses = mar_th*cum_cpi   # initial expenses

    while my_date <= state1_end:
##        act_ret = random.gauss(avg_ret, sd_ret)
        ret_index = my_date.year - start_date.year - 1
        act_ret = ret_list[ret_index] [mc_cnt]
        act_cpi = cpi_list[ret_index] [mc_cnt]
        delta_time = my_date - start_date
        timeline[row_cnt][0] = my_date
        timeline[row_cnt][1] = timeline[row_cnt-1][1]*(1+act_ret) + 0 + cont_401k
        timeline[row_cnt][2] = timeline[row_cnt-1][2]*(1+act_ret) + (cont_espp + cont_rsu - expenses)
        timeline[row_cnt][3] = 0      #SS income
        timeline[row_cnt][4] = expenses      #Expenses
        timeline[row_cnt][5] = 0      #NQ Taxable Income
        timeline[row_cnt][6] = 0      #Q Taxable Income
        timeline[row_cnt][7] = 0      #Taxes
        timeline[row_cnt][8] = 0      #Healthcare
        age = timeline[row_cnt][0] - jon_bd
        timeline[row_cnt][9] = age.days/365.25
        timeline[row_cnt][10] = timeline[row_cnt][4] + timeline[row_cnt][7] + timeline[row_cnt][8]
        timeline[row_cnt][11] = 0       #RMD
        row_cnt = row_cnt + 1
        my_date = my_date + datetime.timedelta(days = 365.25)
        expenses = expenses*(1+act_cpi)

    timeline[row_cnt][0] = state1_end
    age = timeline[row_cnt][0] - jon_bd
    timeline[row_cnt][9] = age.days/365.25
    timeline[row_cnt][10] = timeline[row_cnt][4] + timeline[row_cnt][7] + timeline[row_cnt][8]
    timeline[row_cnt][11] = 0       #RMD
##    act_ret = random.gauss(avg_ret, sd_ret)
    ret_index = my_date.year - start_date.year - 1
    act_ret = ret_list[ret_index] [mc_cnt]
    act_cpi = cpi_list[ret_index] [mc_cnt]

    frac_time = state1_end - (my_date - datetime.timedelta(days = 365.25))
    timeline[row_cnt][1] = timeline[row_cnt-1][1]*((1+act_ret)**(frac_time.days/365.25)) + (0 + cont_401k)*frac_time.days/365.25
    timeline[row_cnt][2] = timeline[row_cnt-1][2]*((1+act_ret)**(frac_time.days/365.25)) + (cont_espp + cont_rsu - expenses)*frac_time.days/365.25
    timeline[row_cnt][3] = 0      #SS income
    timeline[row_cnt][4] = expenses*frac_time.days/365.25      #Expenses
    timeline[row_cnt][5] = 0      #NQ Taxable Income
    timeline[row_cnt][6] = 0      #Q Taxable Income
    timeline[row_cnt][7] = 0      #Taxes
    timeline[row_cnt][8] = 0      #Healthcare
    timeline[row_cnt][10] = timeline[row_cnt][4] + timeline[row_cnt][7] + timeline[row_cnt][8]
    timeline[row_cnt][11] = 0       #RMD

    return(row_cnt + 1)

#-------------------------------------------------------------------------------
# state 2 is both of us retired, no more contributions.
# SS not filed for yet
# Projected expenses adjusted for inflation PLUS Health Care
# Taxes now included
#-------------------------------------------------------------------------------
def state2(row_cnt):
    global timeline
    global liabilities

    state2_end = file_ss

    my_date = timeline[row_cnt-1][0] + datetime.timedelta(days = 365.25)
    delta_time = my_date - start_date
    ret_index = my_date.year - start_date.year - 1
    cum_cpi = 1
    cum_hc_cpi = 1
    for i in range(ret_index + 1):
        cum_cpi = cum_cpi * (1 + cpi_list[i] [mc_cnt])
        cum_hc_cpi = cum_hc_cpi * (1.04 + cpi_list[i] [mc_cnt])
    expenses = proj_exp*cum_cpi - anu_pmt  # initial expenses
    health_care = hc*cum_hc_cpi
##    taxes = calc_taxes(timeline[row_cnt-1][2] * act_ret)

    while my_date <= state2_end:
##        act_ret = random.gauss(avg_ret, sd_ret)
        ret_index = my_date.year - start_date.year - 1
        act_ret = ret_list[ret_index] [mc_cnt]
        act_cpi = cpi_list[ret_index] [mc_cnt]

        taxes = calc_taxes(timeline[row_cnt-1][2] * act_ret)
        timeline[row_cnt][0] = my_date
        timeline[row_cnt][1] = timeline[row_cnt-1][1]*(1+act_ret) + 0 + 0
        timeline[row_cnt][2] = timeline[row_cnt-1][2]*(1+act_ret) + 0 + 0 - expenses - taxes - health_care - liabilities
        liabilities = 0
        timeline[row_cnt][3] = 0      #SS income
        timeline[row_cnt][4] = expenses      #Expenses
        timeline[row_cnt][5] = timeline[row_cnt-1][2] * act_ret       #NQ Taxable Income
        timeline[row_cnt][6] = 0      #Q Taxable Income
        timeline[row_cnt][7] = taxes      #Taxes
        timeline[row_cnt][8] = health_care      #Healthcare
        age = timeline[row_cnt][0] - jon_bd
        timeline[row_cnt][9] = age.days/365.25
        timeline[row_cnt][10] = timeline[row_cnt][4] + timeline[row_cnt][7] + timeline[row_cnt][8]
        timeline[row_cnt][11] = 0       #RMD

        if timeline[row_cnt][2] < 0:
##            back_add_taxes = timeline[row_cnt][1] + timeline[row_cnt][2] + taxes
            taxes = calc_taxes(expenses + anu_pmt + timeline[row_cnt - 1][7] + health_care + liabilities)
            timeline[row_cnt][1] = timeline[row_cnt][1] - expenses - taxes - health_care - liabilities
            timeline[row_cnt][1] = timeline[row_cnt][1] + timeline[row_cnt-1][2]
            timeline[row_cnt][2] = 0
            timeline[row_cnt][5] = 0      #NQ Taxable Income
##            timeline[row_cnt][6] = expenses     #Q Taxable Income
            timeline[row_cnt][6] = expenses + anu_pmt + timeline[row_cnt - 1][7] + health_care + liabilities
            timeline[row_cnt][7] = taxes      #Taxes
            timeline[row_cnt][8] = health_care      #Healthcare
            timeline[row_cnt][10] = timeline[row_cnt][4] + timeline[row_cnt][7] + timeline[row_cnt][8]
            timeline[row_cnt][11] - 0       #RMD

        row_cnt = row_cnt + 1
        my_date = my_date + datetime.timedelta(days = 365.25)
        delta_time = my_date - start_date
        expenses = expenses*(1+act_cpi)
        health_care = health_care*(1.04+act_cpi)
        taxes = calc_taxes(timeline[row_cnt-1][2] * act_ret)

##    act_ret = random.gauss(avg_ret, sd_ret)
    ret_index = my_date.year - start_date.year - 1
    act_ret = ret_list[ret_index] [mc_cnt]
    act_cpi = cpi_list[ret_index] [mc_cnt]

    taxes = calc_taxes(timeline[row_cnt-1][2] * act_ret)
    timeline[row_cnt][0] = state2_end
    age = timeline[row_cnt][0] - jon_bd
    timeline[row_cnt][9] = age.days/365.25
    timeline[row_cnt][10] = timeline[row_cnt][4] + timeline[row_cnt][7] + timeline[row_cnt][8]
    frac_time = state2_end - (my_date - datetime.timedelta(days = 365.25))
    timeline[row_cnt][1] = timeline[row_cnt-1][1]*((1+act_ret)**(frac_time.days/365.25)) + (0 + 0)*frac_time.days/365.25
    if timeline[row_cnt-1][2] > 0:
        timeline[row_cnt][2] = timeline[row_cnt-1][2]*((1+act_ret)**(frac_time.days/365.25)) + (0 + 0 - expenses - taxes - health_care)*frac_time.days/365.25 - liabilities
    else:
        timeline[row_cnt][2] = 0
        taxes = calc_taxes(expenses + anu_pmt + timeline[row_cnt - 1][7] + health_care + liabilities)
        timeline[row_cnt][1] = timeline[row_cnt-1][1]*((1+act_ret)**(frac_time.days/365.25)) + (0 + 0 -expenses - taxes)*frac_time.days/365.25 - liabilities
    liabilities = 0
    timeline[row_cnt][3] = 0      #SS income
    timeline[row_cnt][4] = expenses*frac_time.days/365.25      #Expenses
    timeline[row_cnt][5] = (timeline[row_cnt-1][2] * act_ret)*frac_time.days/365.25       #NQ Taxable Income
    timeline[row_cnt][6] = 0      #Q Taxable Income
    timeline[row_cnt][7] = taxes*frac_time.days/365.25      #Taxes
    timeline[row_cnt][8] = health_care*frac_time.days/365.25      #Healthcare
    timeline[row_cnt][10] = timeline[row_cnt][4] + timeline[row_cnt][7] + timeline[row_cnt][8]
    timeline[row_cnt][11] = 0       #RMD

    return(row_cnt + 1)

#-------------------------------------------------------------------------------
# state 3 is both of us retired, no more contributions.
# Now we're gertting SS
# Projected expenses adjusted for inflation
# This is the state where non-qulified funds run out, and we drawing from the qualified accounts
# No RMDs yet (starts @ 70
#-------------------------------------------------------------------------------
def state3(row_cnt):
    global timeline

    state3_end = jon_bd + datetime.timedelta(days = rmd_start*365.25)

    ss_income = 0
    my_date = timeline[row_cnt-1][0] + datetime.timedelta(days = 365.25)
    ret_index = my_date.year - start_date.year - 1
    cum_cpi = 1
    cum_hc_cpi = 1
    for i in range(ret_index + 1):
        cum_cpi = cum_cpi * (1 + cpi_list[i] [mc_cnt])
        cum_hc_cpi = cum_hc_cpi*(1.04 + cpi_list[i] [mc_cnt])
    expenses = proj_exp*cum_cpi - anu_pmt  # initial expenses
    health_care = hc*cum_hc_cpi

    while my_date <= state3_end:
##        act_ret = random.gauss(avg_ret, sd_ret)
        ret_index = my_date.year - start_date.year - 1
        act_ret = ret_list[ret_index] [mc_cnt]
        act_cpi = cpi_list[ret_index] [mc_cnt]

        delta_time = my_date - start_date
        ss_income =soc_sec*cum_cpi
        cum_cpi = cum_cpi*(1 + act_cpi)
        taxes = calc_taxes((timeline[row_cnt-1][2] * act_ret + ss_income*0.85))
        timeline[row_cnt][0] = my_date
        timeline[row_cnt][1] = timeline[row_cnt-1][1]*(1+act_ret) + 0 + 0
        timeline[row_cnt][2] = timeline[row_cnt-1][2]*(1+act_ret) + 0 + 0 - expenses - taxes - health_care + ss_income
        timeline[row_cnt][3] = ss_income      #SS income
        timeline[row_cnt][4] = expenses      #Expenses
        timeline[row_cnt][5] = timeline[row_cnt-1][2] * act_ret + ss_income*0.85       #NQ Taxable Income
        timeline[row_cnt][6] = 0      #Q Taxable Income
        timeline[row_cnt][7] = taxes      #Taxes
        timeline[row_cnt][8] = health_care      #Healthcare
        age = timeline[row_cnt][0] - jon_bd
        timeline[row_cnt][9] = age.days/365.25
        timeline[row_cnt][10] = timeline[row_cnt][4] + timeline[row_cnt][7] + timeline[row_cnt][8]
        timeline[row_cnt][11] = 0       #RMD

        if timeline[row_cnt][2] < 0:
##            back_add_taxes = timeline[row_cnt][1] + timeline[row_cnt][2] + taxes
            taxes = calc_taxes(expenses + anu_pmt + timeline[row_cnt - 1][7] + health_care + liabilities- ss_income + ss_income*0.85)
            timeline[row_cnt][1] = timeline[row_cnt][1] - expenses - taxes - health_care + ss_income
            timeline[row_cnt][1] = timeline[row_cnt][1] + timeline[row_cnt-1][2]
            timeline[row_cnt][2] = 0
            timeline[row_cnt][5] = 0      #NQ Taxable Income
##            timeline[row_cnt][6] = expenses - ss_income*0.15      #Q Taxable Income
            timeline[row_cnt][6] = expenses + anu_pmt + timeline[row_cnt - 1][7] + health_care + liabilities- ss_income + ss_income*0.85
            timeline[row_cnt][7] = taxes      #Taxes
            timeline[row_cnt][8] = health_care      #Healthcare
            timeline[row_cnt][10] = timeline[row_cnt][4] + timeline[row_cnt][7] + timeline[row_cnt][8]
            timeline[row_cnt][11] = 0       #RMD
        expenses = expenses*(1+act_cpi)
        health_care = health_care*(1.04+act_cpi)
        row_cnt = row_cnt + 1
        my_date = my_date + datetime.timedelta(days = 365.25)
##        if timeline[row_cnt][1] + timeline[row_cnt][2] < 0:
##            my_date = my_date + datetime.timedelta(days = 100*365.25)
##            return(row_cnt + 1)

    ret_index = my_date.year - start_date.year - 1
    act_ret = ret_list[ret_index] [mc_cnt]
    act_cpi = cpi_list[ret_index] [mc_cnt]

    taxes = calc_taxes(timeline[row_cnt-1][2] * act_ret)

    timeline[row_cnt][0] = state3_end
    age = timeline[row_cnt][0] - jon_bd
##    act_ret = random.gauss(avg_ret, sd_ret)

    frac_time = state3_end - (my_date - datetime.timedelta(days = 365.25))
    timeline[row_cnt][1] = timeline[row_cnt-1][1]*((1+act_ret)**(frac_time.days/365.25)) + (0 + 0)*frac_time.days/365.25
    if timeline[row_cnt-1][2] > 0:
        timeline[row_cnt][2] = timeline[row_cnt-1][2]*((1+act_ret)**(frac_time.days/365.25)) + (0 + 0 - expenses - taxes - health_care + ss_income)*frac_time.days/365.25
    else:
        timeline[row_cnt][2] = 0
        taxes = calc_taxes(expenses + anu_pmt + timeline[row_cnt - 1][7] + health_care + liabilities- ss_income + ss_income*0.85)
        timeline[row_cnt][1] = timeline[row_cnt-1][1]*((1+act_ret)**(frac_time.days/365.25)) + (0 + 0 - expenses - taxes - health_care + ss_income)*frac_time.days/365.25

    timeline[row_cnt][3] = ss_income*frac_time.days/365.25      #SS income
    timeline[row_cnt][4] = expenses*frac_time.days/365.25      #Expenses
    timeline[row_cnt][5] = (timeline[row_cnt-1][2] * act_ret)*frac_time.days/365.25       #NQ Taxable Income
    timeline[row_cnt][6] = 0      #Q Taxable Income
    timeline[row_cnt][7] = taxes*frac_time.days/365.25      #Taxes
    timeline[row_cnt][8] = health_care*frac_time.days/365.25      #Healthcare
    timeline[row_cnt][9] = age.days/365.25
    timeline[row_cnt][10] = timeline[row_cnt][4] + timeline[row_cnt][7] + timeline[row_cnt][8]
    timeline[row_cnt][11] = 0       #RMD




#    row_cnt = row_cnt + 1
#    timeline[row_cnt][0] = state3_end
#    age = timeline[row_cnt][0] - jon_bd
#    timeline[row_cnt][9] = age.days/365.25
#    timeline[row_cnt][1] = 0
#    timeline[row_cnt][10] = timeline[row_cnt][4] + timeline[row_cnt][7] + timeline[row_cnt][8]

    return(row_cnt + 1)
#-------------------------------------------------------------------------------
# state 4 is where RMDs start...
# Both of us retired, no more contributions.
# Now we're gertting SS
# Projected expenses adjusted for inflation
# This is the state where non-qulified funds run out, and we drawing from the qualified accounts
#-------------------------------------------------------------------------------
def state4(row_cnt):
    global timeline

    state4_end = jon_bd + datetime.timedelta(days = 95*365.25)

    my_date = timeline[row_cnt-1][0] + datetime.timedelta(days = 365.25)
    ret_index = my_date.year - start_date.year - 1
    cum_cpi = 1
    cum_hc_cpi = 1
    for i in range(ret_index + 1):
        cum_cpi = cum_cpi * (1 + cpi_list[i] [mc_cnt])
        cum_hc_cpi = cum_hc_cpi*(1.04 + cpi_list[i] [mc_cnt])
    expenses = proj_exp*cum_cpi - anu_pmt   # initial expenses
    health_care = hc*cum_hc_cpi

    while my_date <= state4_end:
        ret_index = my_date.year - start_date.year - 1
        act_ret = ret_list[ret_index] [mc_cnt]
        act_cpi = cpi_list[ret_index] [mc_cnt]

        delta_time = my_date - start_date
        ss_income =soc_sec*cum_cpi
        cum_cpi = cum_cpi*(1 + act_cpi)

        timeline[row_cnt][0] = my_date
        age = timeline[row_cnt][0] - jon_bd
        timeline[row_cnt][9] = age.days/365.25

        rmd = timeline[row_cnt-1][1]/rmd_table[int(timeline[row_cnt][9] - rmd_start)]
        timeline[row_cnt][1] = timeline[row_cnt-1][1]*(1+act_ret) + 0 + 0 - rmd
        taxes = calc_taxes(timeline[row_cnt-1][2] * act_ret + ss_income*0.85 + rmd)
        timeline[row_cnt][2] = timeline[row_cnt-1][2]*(1+act_ret) + 0 + 0 - expenses - taxes - health_care + ss_income + rmd
        timeline[row_cnt][7] = taxes      #Taxes

        timeline[row_cnt][3] = ss_income      #SS income
        timeline[row_cnt][4] = expenses      #Expenses
        timeline[row_cnt][5] = timeline[row_cnt-1][2] * act_ret + ss_income*0.85       #NQ Taxable Income
        timeline[row_cnt][6] = 0      #Q Taxable Income
        timeline[row_cnt][7] = taxes      #Taxes
        timeline[row_cnt][8] = health_care      #Healthcare
        timeline[row_cnt][10] = timeline[row_cnt][4] + timeline[row_cnt][7] + timeline[row_cnt][8]
        timeline[row_cnt][11] = rmd

        if timeline[row_cnt][2] < 0:
##            back_add_taxes = timeline[row_cnt][1] + timeline[row_cnt][2] + taxes
            if expenses > rmd:
                taxes = calc_taxes(expenses + anu_pmt + timeline[row_cnt - 1][7] + health_care + liabilities- ss_income + ss_income*0.85)
                timeline[row_cnt][1] = timeline[row_cnt][1] - expenses + rmd - taxes - health_care + ss_income
            else:
                taxes = calc_taxes(rmd + timeline[row_cnt - 1][7] + health_care + liabilities- ss_income + ss_income*0.85)
                timeline[row_cnt][1] = timeline[row_cnt][1] - taxes - health_care + ss_income
            timeline[row_cnt][1] = timeline[row_cnt][1] + timeline[row_cnt-1][2]
            timeline[row_cnt][2] = 0
            timeline[row_cnt][5] = 0      #NQ Taxable Income
##            timeline[row_cnt][6] = expenses - ss_income*0.15      #Q Taxable Income
            timeline[row_cnt][6] = expenses + anu_pmt + timeline[row_cnt - 1][7] + health_care + liabilities- ss_income + ss_income*0.85
            timeline[row_cnt][7] = taxes      #Taxes
            timeline[row_cnt][8] = health_care      #Healthcare
            timeline[row_cnt][10] = timeline[row_cnt][4] + timeline[row_cnt][7] + timeline[row_cnt][8]
            timeline[row_cnt][11] = rmd
        expenses = expenses*(1+act_cpi)
        health_care = health_care*(1.04+act_cpi)
        row_cnt = row_cnt + 1
        my_date = my_date + datetime.timedelta(days = 365.25)
##        if timeline[row_cnt][1] + timeline[row_cnt][2] < 0:
##            my_date = my_date + datetime.timedelta(days = 100*365.25)
##            return(row_cnt + 1)

    ret_index = my_date.year - start_date.year - 1
    act_ret = ret_list[ret_index] [mc_cnt]
    act_cpi = cpi_list[ret_index] [mc_cnt]

    taxes = calc_taxes(timeline[row_cnt-1][2] * act_ret)

    timeline[row_cnt][0] = state4_end
    age = timeline[row_cnt][0] - jon_bd
##    act_ret = random.gauss(avg_ret, sd_ret)

    frac_time = state4_end - (my_date - datetime.timedelta(days = 365.25))
    timeline[row_cnt][1] = timeline[row_cnt-1][1]*((1+act_ret)**(frac_time.days/365.25)) + (0 + 0)*frac_time.days/365.25
    if timeline[row_cnt-1][2] > 0:
        timeline[row_cnt][2] = timeline[row_cnt-1][2]*((1+act_ret)**(frac_time.days/365.25)) + (0 + 0 - expenses - taxes - health_care + ss_income)*frac_time.days/365.25
    else:
        timeline[row_cnt][2] = 0
        taxes = calc_taxes(expenses + anu_pmt + timeline[row_cnt - 1][7] + health_care + liabilities- ss_income + ss_income*0.85)
        timeline[row_cnt][1] = timeline[row_cnt-1][1]*((1+act_ret)**(frac_time.days/365.25)) + (0 + 0 - expenses - taxes - health_care + ss_income)*frac_time.days/365.25

    timeline[row_cnt][3] = ss_income*frac_time.days/365.25      #SS income
    timeline[row_cnt][4] = expenses*frac_time.days/365.25      #Expenses
    timeline[row_cnt][5] = (timeline[row_cnt-1][2] * act_ret)*frac_time.days/365.25       #NQ Taxable Income
    timeline[row_cnt][6] = 0      #Q Taxable Income
    timeline[row_cnt][7] = taxes*frac_time.days/365.25      #Taxes
    timeline[row_cnt][8] = health_care*frac_time.days/365.25      #Healthcare
    timeline[row_cnt][9] = age.days/365.25
    timeline[row_cnt][10] = timeline[row_cnt][4] + timeline[row_cnt][7] + timeline[row_cnt][8]
    timeline[row_cnt][11] = rmd

    row_cnt = row_cnt + 1
    timeline[row_cnt][0] = state4_end
    age = timeline[row_cnt][0] - jon_bd
    timeline[row_cnt][9] = age.days/365.25
    timeline[row_cnt][1] = 0
    timeline[row_cnt][10] = timeline[row_cnt][4] + timeline[row_cnt][7] + timeline[row_cnt][8]
    timeline[row_cnt][11] = rmd

    return(row_cnt + 1)

if __name__ == '__main__':

    global timeline
    global new_tax

    new_tax = 0

    timeline = [[0 for j in range(12)] for i in range(50)]
    header = [[0 for j in range(12)] for i in range(1)]
    ret_list = [[0 for j in range(1000)] for i in range(55)]
    cpi_list = [[0 for j in range(1000)] for i in range(55)]
    hist_list = []
    infl_list = []
    year_list = []
    plt.ion()
    plt_type = "B"
    mc_cnt = 0
    rmd_start = 70
    rmd_table = [27.4,26.5,25.6,24.7,23.8,22.9,22.0,21.2,20.3,19.5,18.7,17.9,17.1,16.3,15.5,14.8,14.1,13.4,12.7,12.0,11.4,10.8,10.2,9.6,9.1,8.6,8.1]

    while 1:
        xit = raw_input("\n"
        "Financial Simulator\n"
        "\n"
        "<cr> = exit\n"
        "Enter the name of the output file:\n")

        if xit == "": break

        else:

            histfile = open('hist.csv', 'r')
            readhist = csv.reader(histfile, delimiter=',')
            onheader = 1
            for row in readhist:
                if onheader == 0:
                    hist_list.append(float(row[4]))
                    infl_list.append(float(row[5]))
                    year_list.append(row[0])
                onheader = 0

            plt_type = raw_input("Plot Type: (M = Monte Carlo, H = Historical, B = Baseline) :")
            plt_type = plt_type.upper()

            currentDay = date.today()
            onheader = 1
            old_avg_ret = 0
            csvfile = open('RetireTrials.csv', 'r')
            readCSV = csv.reader(csvfile, delimiter=',')
            res_f = open(xit, "wb")
            writer = csv.writer(res_f)
            fig_count = 0
            for row in readCSV:
                print ', '.join(row)
##                res_f.write(row)
                print "On Header ", onheader

                if onheader == 0:
                    fig_count += 1
                    res_f.write(row[0])
                    res_f.write('\n')
                    param_lst = []
                    trial = row[0]
                    start_date = parse(row[1])
                    avg_ret = float(row[2].strip('%'))/100
                    sd_ret = float(row[3].strip('%'))/100
                    cpi = float(row[4].strip('%'))/100
                    mar_th = float(row[5].replace("$","").replace(",",""))
                    cont_403b = float(row[6].replace("$","").replace(",",""))
                    jon_th = float(row[7].replace("$","").replace(",",""))
                    cont_401k = float(row[8].replace("$","").replace(",",""))
                    cont_espp = float(row[9].replace("$","").replace(",",""))
                    cont_rsu = float(row[10].replace("$","").replace(",",""))
                    mar_bd = parse(row[11])
                    jon_bd = parse(row[12])
                    proj_exp = float(row[13].replace("$","").replace(",",""))
                    soc_sec = float(row[14].replace("$","").replace(",",""))
                    file_ss = parse(row[15])
                    hc = float(row[16].replace("$","").replace(",",""))
                    hc_cpi = float(row[17].strip('%'))/100
                    mar_ret = float(row[18])
                    jon_ret = float(row[19])
                    qual_tot = float(row[20].replace("$","").replace(",",""))
                    nonq_tot = float(row[21].replace("$","").replace(",",""))
                    liabilities = float(row[22].replace("$","").replace(",",""))
                    anu_pmt = float(row[23].replace("$","").replace(",",""))
                    anu_date = parse(row[24])

                    sav_sd_ret = sd_ret
                    sd_ret = 0

                    for i in range(50):
                        ret_list[i] [mc_cnt]= avg_ret
                        cpi_list[i] [mc_cnt] = cpi

                    next_row = state0()
                    next_row = state1(next_row)
                    next_row = state2(next_row)
                    next_row = state3(next_row)
                    next_row = state4(next_row)

                    nom_tl = deepcopy(timeline)
                    nom_last_row = next_row - 1
                    worst_tl = deepcopy(timeline)
                    worst_lst = [i[1] for i in nom_tl]
                    worst_val = next((index for index,value in enumerate(worst_lst) if value < 0), 42)
                    worst_end = nom_tl[worst_val][1]
                    worst_date = nom_tl[worst_val][0]
                    worst_mc = -1
                    worst_year = '0'
                    fails = 0
                    passes = 0

                    if plt_type in ['H', 'M']:
                        sd_ret = sav_sd_ret

                        if avg_ret != old_avg_ret:
                            old_avg_ret = avg_ret
                            print 'Recalculating returns'
                            if plt_type == 'H':
                                max_mc_cnt = 43
                                for i in range(53):
                                    for j in range(37):
                                        ret_list[i] [j]= hist_list[i+j-2]
                                        cpi_list[i][j] = infl_list[i+j-2]
                            else:
                                max_mc_cnt = 1000
                                ret_list = [[random.gauss(avg_ret, sd_ret) for j in range(1000)] for i in range(50)]
                                cpi_list = [[random.gauss(cpi, sd_ret) for j in range(1000)] for i in range(50)]

                        for mc_cnt in range(max_mc_cnt):
##                            act_ret = random.gauss(avg_ret, sd_ret)
                            timeline = [[0 for j in range(12)] for i in range(50)]
                            next_row = state0()
                            next_row = state1(next_row)
                            next_row = state2(next_row)
                            next_row = state3(next_row)
                            next_row = state4(next_row)

                            if timeline[32][1] < 0:
                                fails += 1
                            else:
                                passes += 1

                            worst_lst = [i[1] for i in timeline]
                            val = next((index for index,value in enumerate(worst_lst) if value < 0), 2000)
                            if val < worst_val:
                                worst_tl = deepcopy(timeline)
                                worst_end = nom_tl[val][1]
                                worst_date = nom_tl[val][0]
                                worst_val = val
                                worst_mc = mc_cnt
                                if plt_type == 'H':
                                    worst_year = year_list[mc_cnt]

                            if mc_cnt == 30:
                                mc_tl = deepcopy(timeline)

                            plt_dates = []
                            plt_total = []
                            for my_row in range(0,next_row):
                                plt_dates.append((date2num(timeline[my_row][0]) - date2num(jon_bd))/365.25)
                                plt_total.append(timeline[my_row][1] + timeline[my_row][2])
                            plt.figure(0)
                            plt.plot(plt_dates,plt_total, '-', color=(0.5, 0.5, 0.5), linewidth=1)

                        print 'Total passes is ', passes
                        print 'Total failes is ', fails

                        plt_total = []
                        plt_dates = []
                        for my_row in range(0,next_row):
                            plt_total.append(worst_tl[my_row][1] + worst_tl[my_row][2])
                            plt_dates.append((date2num(worst_tl[my_row][0]) - date2num(jon_bd))/365.25)
                        plt.figure(0)
                        plt.plot(plt_dates,plt_total, '.r-', linewidth=2)

                        plt_total = []
                        plt_dates = []
                        for my_row in range(0,next_row):
                            plt_total.append(nom_tl[my_row][1] + nom_tl[my_row][2])
                            plt_dates.append((date2num(nom_tl[my_row][0]) - date2num(jon_bd))/365.25)
                        plt.figure(0)
                        plt.plot(plt_dates,plt_total, '.b-', linewidth=2)
                        title_str = trial + ' \nConfidence to not be broke @ 90 is ' + str(100*round(float(passes)/float(passes + fails),3)) +'%'
                        if plt_type == 'H':
                            title_str = title_str + ', Hist starts in ' + worst_year

                    else:
                        plt_total = []
                        plt_dates = []
                        plt_total.append(0)
                        plt_dates.append(58)
                        for my_row in range(0,next_row):
                            plt_total.append(nom_tl[my_row][1] + nom_tl[my_row][2])
                            plt_dates.append((date2num(nom_tl[my_row][0]) - date2num(jon_bd))/365.25)
                        plt_total.append(0)
                        plt_dates.append(86)
                        plt.figure(0)
                        plt.fill(plt_dates,plt_total, '.r-')

                        plt_total = []
                        plt_dates = []
                        plt_total.append(0)
                        plt_dates.append(58)
                        for my_row in range(0,next_row):
                            plt_total.append(nom_tl[my_row][1])
                            plt_dates.append((date2num(nom_tl[my_row][0]) - date2num(jon_bd))/365.25)
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
                    if plt_type == 'B':
                       axes.set_ylim([0,2000000])
                    else:
                       axes.set_ylim([0,10000000])
                    plt.gcf().set_size_inches(12, 5.3)
                    plt.title(title_str)
                    plt.legend()
                    plt.draw()

                    plt.ioff()
                    fig_name = 'figure '+str(fig_count)+'-b.png'
                    if plt_type == "H":
                        fig_name = 'figure '+str(fig_count)+'-h.png'
                    if plt_type == "M":
                        fig_name = 'figure '+str(fig_count)+'-mc.png'

                    plt.savefig(fig_name)
                    plt.show()      # blocking!

                    header[0][0] = "Date"
                    header[0][1] = "Qual Total"
                    header[0][2] = "Non-Q Total"
                    header[0][3] = "SS Income"
                    header[0][4] = "Expenses"
                    header[0][5] = "NQ Taxable Income"
                    header[0][6] = "Q Taxable Income"
                    header[0][7] = "Taxes"
                    header[0][8] = "Healthcare"
                    header[0][9] = "Age"
                    header[0][10] = "Total Expenses"
                    header[0][11] = "RMD"

##                    writer = csv.writer(res_f)
                    writer.writerows(header)
                    if plt_type != "B":
                        writer.writerows(worst_tl)
                    else:
                        writer.writerows(timeline)

                onheader = 0
                print currentDay.year
                print currentDay.month
                print currentDay.day

            plt.show()      # blocking!
            res_f.close()
