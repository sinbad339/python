#-------------------------------------------------------------------------------
# Name:        Retirement States
# Purpose:
#
# Author:      jdilorenzo
#
# Created:     20/10/2017
# Copyright:   (c) jdilorenzo 2017
# Licence:     <your licence>
#-------------------------------------------------------------------------------
import datetime
from datetime import date,timedelta
from dateutil.parser import parse
import random

#--------------------------------------------------------
# Calculate Income Taxes
#-------------------------------------------------------
def calc_taxes(income, new_tax):
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
def state0(entries, timeline, sd_ret):

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
##    sd_ret = float(entries[9][1].get().strip('%'))/100
    cpi = float(entries[10][1].get().strip('%'))/100
    proj_exp = float(entries[11][1].get().replace("$","").replace(",",""))
    file_ss = parse(entries[12][1].get())
    soc_sec = float(entries[13][1].get().replace("$","").replace(",",""))
    hc = float(entries[14][1].get().replace("$","").replace(",",""))
    hc_cpi = float(entries[15][1].get().strip('%'))/100
    qual_tot = float(entries[16][1].get().replace("$","").replace(",",""))
    nonq_tot = float(entries[17][1].get().replace("$","").replace(",",""))
    liabilities = float(entries[18][1].get().replace("$","").replace(",",""))

    state0_end = bd2 + datetime.timedelta(days = ret2*365.25)

    timeline[0][0] = start_date
    timeline[0][1] = qual_tot
    timeline[0][2] = nonq_tot
    timeline[0][3] = 0      #SS income
    timeline[0][4] = 0      #Expenses
    timeline[0][5] = 0      #NQ Taxable Income
    timeline[0][6] = 0      #Q Taxable Income
    timeline[0][7] = 0      #Taxes
    timeline[0][8] = 0      #Healthcare
    age = timeline[0][0] - bd1
    timeline[0][9] = age.days/365.25
    timeline[0][10] = timeline[0][4] + timeline[0][7] + timeline[0][8]

    row_cnt = 1
    act_ret = 0

    my_date = start_date + datetime.timedelta(days = 365.25)
    while my_date <= state0_end:
        act_ret = random.gauss(avg_ret, sd_ret)
##        ret_index = my_date.year - start_date.year - 1
##        act_ret = ret_list[ret_index]
        delta_time = my_date - start_date
        timeline[row_cnt][0] = my_date
        timeline[row_cnt][1] = timeline[row_cnt-1][1]*(1+act_ret) + (qual_cont)*((1+cpi)**(delta_time.days/365.25))
        timeline[row_cnt][2] = timeline[row_cnt-1][2]*(1+act_ret) + (nonq_cont)*((1+cpi)**(delta_time.days/365.25))
        timeline[row_cnt][3] = 0      #SS income
        timeline[row_cnt][4] = 0      #Expenses
        timeline[row_cnt][5] = 0      #NQ Taxable Income
        timeline[row_cnt][6] = 0      #Q Taxable Income
        timeline[row_cnt][7] = 0      #Taxes
        timeline[row_cnt][8] = 0      #Healthcare
        age = timeline[row_cnt][0] - bd1
        timeline[row_cnt][9] = age.days/365.25
        timeline[row_cnt][10] = timeline[row_cnt][4] + timeline[row_cnt][7] + timeline[row_cnt][8]
        row_cnt = row_cnt + 1
        my_date = my_date + datetime.timedelta(days = 365.25)

    timeline[row_cnt][0] = state0_end
    age = timeline[row_cnt][0] - bd1
    timeline[row_cnt][9] = age.days/365.25
    timeline[row_cnt][10] = timeline[row_cnt][4] + timeline[row_cnt][7] + timeline[row_cnt][8]
    act_ret = random.gauss(avg_ret, sd_ret)
##    ret_index = my_date.year - start_date.year
##    act_ret = ret_list[ret_index]
    delta_time = state0_end - (my_date - datetime.timedelta(days = 365.25))
##    jjd = delta_time.days/365.25
    timeline[row_cnt][1] = timeline[row_cnt-1][1]*((1+act_ret)**(delta_time.days/365.25)) + (qual_cont)*delta_time.days/365.25
    timeline[row_cnt][2] = timeline[row_cnt-1][2]*((1+act_ret)**(delta_time.days/365.25)) + (nonq_cont)*delta_time.days/365.25

    return(row_cnt + 1)

#-------------------------------------------------------------------------------
# state 1 is Martha retired, me working and contributing tomy accounts
# Expenses are to make up for Martha's take-home pay.
#-------------------------------------------------------------------------------
def state1(row_cnt, entries, timeline, sd_ret):

    name1 = entries[0][1].get()
    name2 = entries[0][2].get()
    qual_cont = float(entries[1][1].get().replace("$","").replace(",",""))
##    qual_cont += float(entries[1][2].get().replace("$","").replace(",",""))
    nonq_cont = float(entries[2][1].get().replace("$","").replace(",",""))
##    nonq_cont += float(entries[2][2].get().replace("$","").replace(",",""))
    bd1 = parse(entries[3][1].get())
    bd2 = parse(entries[3][2].get())
    ret1 = float(entries[4][1].get())
    ret2 = float(entries[4][2].get())
    takehome1 = float(entries[5][1].get().replace("$","").replace(",",""))
    takehome2 = float(entries[5][2].get().replace("$","").replace(",",""))

    trial = entries[6][1].get()
    start_date = parse(entries[7][1].get())
    avg_ret = float(entries[8][1].get().strip('%'))/100
##    sd_ret = float(entries[9][1].get().strip('%'))/100
    cpi = float(entries[10][1].get().strip('%'))/100
    proj_exp = float(entries[11][1].get().replace("$","").replace(",",""))
    file_ss = parse(entries[12][1].get())
    soc_sec = float(entries[13][1].get().replace("$","").replace(",",""))
    hc = float(entries[14][1].get().replace("$","").replace(",",""))
    hc_cpi = float(entries[15][1].get().strip('%'))/100
    qual_tot = float(entries[16][1].get().replace("$","").replace(",",""))
    nonq_tot = float(entries[17][1].get().replace("$","").replace(",",""))
    liabilities = float(entries[18][1].get().replace("$","").replace(",",""))

    state1_end = bd1 + datetime.timedelta(days = ret1*365.25)

    my_date = timeline[row_cnt-1][0] + datetime.timedelta(days = 365.25)
    delta_time = my_date - start_date
    expenses = takehome2*((1+cpi)**(delta_time.days/365.25))

    while my_date <= state1_end:
        act_ret = random.gauss(avg_ret, sd_ret)
##        ret_index = my_date.year - start_date.year
##        act_ret = ret_list[ret_index]
        delta_time = my_date - start_date
        timeline[row_cnt][0] = my_date
        timeline[row_cnt][1] = timeline[row_cnt-1][1]*(1+act_ret) + 0 + qual_cont*((1+cpi)**(delta_time.days/365.25))
        timeline[row_cnt][2] = timeline[row_cnt-1][2]*(1+act_ret) + (nonq_cont - expenses)*((1+cpi)**(delta_time.days/365.25))
        timeline[row_cnt][3] = 0      #SS income
        timeline[row_cnt][4] = expenses      #Expenses
        timeline[row_cnt][5] = 0      #NQ Taxable Income
        timeline[row_cnt][6] = 0      #Q Taxable Income
        timeline[row_cnt][7] = 0      #Taxes
        timeline[row_cnt][8] = 0      #Healthcare
        age = timeline[row_cnt][0] - bd1
        timeline[row_cnt][9] = age.days/365.25
        timeline[row_cnt][10] = timeline[row_cnt][4] + timeline[row_cnt][7] + timeline[row_cnt][8]
        row_cnt = row_cnt + 1
        my_date = my_date + datetime.timedelta(days = 365.25)
        expenses = takehome2*((1+cpi)**(delta_time.days/365.25))

    timeline[row_cnt][0] = state1_end
    age = timeline[row_cnt][0] - bd1
    timeline[row_cnt][9] = age.days/365.25
    timeline[row_cnt][10] = timeline[row_cnt][4] + timeline[row_cnt][7] + timeline[row_cnt][8]
    act_ret = random.gauss(avg_ret, sd_ret)
##    ret_index = my_date.year - start_date.year
##    act_ret = ret_list[ret_index]

    frac_time = state1_end - (my_date - datetime.timedelta(days = 365.25))
    timeline[row_cnt][1] = timeline[row_cnt-1][1]*((1+act_ret)**(frac_time.days/365.25)) + (0 + qual_cont)*frac_time.days/365.25
    timeline[row_cnt][2] = timeline[row_cnt-1][2]*((1+act_ret)**(frac_time.days/365.25)) + (nonq_cont - expenses)*frac_time.days/365.25
    timeline[row_cnt][3] = 0      #SS income
    timeline[row_cnt][4] = expenses*frac_time.days/365.25      #Expenses
    timeline[row_cnt][5] = 0      #NQ Taxable Income
    timeline[row_cnt][6] = 0      #Q Taxable Income
    timeline[row_cnt][7] = 0      #Taxes
    timeline[row_cnt][8] = 0      #Healthcare
    timeline[row_cnt][10] = timeline[row_cnt][4] + timeline[row_cnt][7] + timeline[row_cnt][8]

    return(row_cnt + 1)

#-------------------------------------------------------------------------------
# state 2 is both of us retired, no more contributions.
# SS not filed for yet
# Projected expenses adjusted for inflation PLUS Health Care
# Taxes now included
#-------------------------------------------------------------------------------
def state2(row_cnt, entries, timeline, sd_ret, new_tax):

    name1 = entries[0][1].get()
    name2 = entries[0][2].get()
    qual_cont = float(entries[1][1].get().replace("$","").replace(",",""))
##    qual_cont += float(entries[1][2].get().replace("$","").replace(",",""))
    nonq_cont = float(entries[2][1].get().replace("$","").replace(",",""))
##    nonq_cont += float(entries[2][2].get().replace("$","").replace(",",""))
    bd1 = parse(entries[3][1].get())
    bd2 = parse(entries[3][2].get())
    ret1 = float(entries[4][1].get())
    ret2 = float(entries[4][2].get())
    takehome1 = float(entries[5][1].get().replace("$","").replace(",",""))
    takehome2 = float(entries[5][2].get().replace("$","").replace(",",""))

    trial = entries[6][1].get()
    start_date = parse(entries[7][1].get())
    avg_ret = float(entries[8][1].get().strip('%'))/100
##    sd_ret = float(entries[9][1].get().strip('%'))/100
    cpi = float(entries[10][1].get().strip('%'))/100
    proj_exp = float(entries[11][1].get().replace("$","").replace(",",""))
    file_ss = parse(entries[12][1].get())
    soc_sec = float(entries[13][1].get().replace("$","").replace(",",""))
    hc = float(entries[14][1].get().replace("$","").replace(",",""))
    hc_cpi = float(entries[15][1].get().strip('%'))/100
    qual_tot = float(entries[16][1].get().replace("$","").replace(",",""))
    nonq_tot = float(entries[17][1].get().replace("$","").replace(",",""))
    liabilities = float(entries[18][1].get().replace("$","").replace(",",""))

    state2_end = file_ss

    my_date = timeline[row_cnt-1][0] + datetime.timedelta(days = 365.25)
    delta_time = my_date - start_date
    expenses = proj_exp*((1+cpi)**(delta_time.days/365.25))
    health_care = hc*((1+hc_cpi)**(delta_time.days/365.25))
##    taxes = calc_taxes(timeline[row_cnt-1][2] * act_ret)

    while my_date <= state2_end:
        act_ret = random.gauss(avg_ret, sd_ret)
##        ret_index = my_date.year - start_date.year
##        act_ret = ret_list[ret_index]

        taxes = calc_taxes(timeline[row_cnt-1][2] * act_ret, new_tax)
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
        age = timeline[row_cnt][0] - bd2
        timeline[row_cnt][9] = age.days/365.25
        timeline[row_cnt][10] = timeline[row_cnt][4] + timeline[row_cnt][7] + timeline[row_cnt][8]

        if timeline[row_cnt][2] < 0:
##            back_add_taxes = timeline[row_cnt][1] + timeline[row_cnt][2] + taxes
            taxes = calc_taxes(expenses + timeline[row_cnt - 1][7] + health_care + liabilities, new_tax)
            timeline[row_cnt][1] = timeline[row_cnt][1] - expenses - taxes - health_care - liabilities
            timeline[row_cnt][2] = 0
            timeline[row_cnt][5] = 0      #NQ Taxable Income
            timeline[row_cnt][6] = expenses     #Q Taxable Income
            timeline[row_cnt][7] = taxes      #Taxes
            timeline[row_cnt][8] = health_care      #Healthcare
            timeline[row_cnt][10] = timeline[row_cnt][4] + timeline[row_cnt][7] + timeline[row_cnt][8]

        row_cnt = row_cnt + 1
        my_date = my_date + datetime.timedelta(days = 365.25)
        delta_time = my_date - start_date
        expenses = proj_exp*((1+cpi)**(delta_time.days/365.25))
        health_care = hc*((1+hc_cpi)**(delta_time.days/365.25))
        taxes = calc_taxes(timeline[row_cnt-1][2] * act_ret, new_tax)

    act_ret = random.gauss(avg_ret, sd_ret)
##    ret_index = my_date.year - start_date.year
##    act_ret = ret_list[ret_index]

    taxes = calc_taxes(timeline[row_cnt-1][2] * act_ret, new_tax)
    timeline[row_cnt][0] = state2_end
    age = timeline[row_cnt][0] - bd2
    timeline[row_cnt][9] = age.days/365.25
    timeline[row_cnt][10] = timeline[row_cnt][4] + timeline[row_cnt][7] + timeline[row_cnt][8]
    frac_time = state2_end - (my_date - datetime.timedelta(days = 365.25))
    timeline[row_cnt][1] = timeline[row_cnt-1][1]*((1+act_ret)**(frac_time.days/365.25)) + (0 + 0)*frac_time.days/365.25
    if timeline[row_cnt-1][2] > 0:
        timeline[row_cnt][2] = timeline[row_cnt-1][2]*((1+act_ret)**(frac_time.days/365.25)) + (0 + 0 - expenses - taxes - health_care)*frac_time.days/365.25
    else:
        timeline[row_cnt][2] = 0
        taxes = calc_taxes(expenses + timeline[row_cnt - 1][7] + health_care + liabilities, new_tax)
        timeline[row_cnt][1] = timeline[row_cnt-1][1]*((1+act_ret)**(frac_time.days/365.25)) + (0 + 0 -expenses - taxes)*frac_time.days/365.25
    timeline[row_cnt][3] = 0      #SS income
    timeline[row_cnt][4] = expenses*frac_time.days/365.25      #Expenses
    timeline[row_cnt][5] = (timeline[row_cnt-1][2] * act_ret)*frac_time.days/365.25       #NQ Taxable Income
    timeline[row_cnt][6] = 0      #Q Taxable Income
    timeline[row_cnt][7] = taxes*frac_time.days/365.25      #Taxes
    timeline[row_cnt][8] = health_care*frac_time.days/365.25      #Healthcare
    timeline[row_cnt][10] = timeline[row_cnt][4] + timeline[row_cnt][7] + timeline[row_cnt][8]

    return(row_cnt + 1)

#-------------------------------------------------------------------------------
# state 3 is both of us retired, no more contributions.
# Now we're gertting SS
# Projected expenses adjusted for inflation
# This is the state where non-qulified funds run out, and we drawing from the qualified accounts
#-------------------------------------------------------------------------------
def state3(row_cnt, entries, timeline, sd_ret, new_tax):

    name1 = entries[0][1].get()
    name2 = entries[0][2].get()
    qual_cont = float(entries[1][1].get().replace("$","").replace(",",""))
##    qual_cont += float(entries[1][2].get().replace("$","").replace(",",""))
    nonq_cont = float(entries[2][1].get().replace("$","").replace(",",""))
##    nonq_cont += float(entries[2][2].get().replace("$","").replace(",",""))
    bd1 = parse(entries[3][1].get())
    bd2 = parse(entries[3][2].get())
    ret1 = float(entries[4][1].get())
    ret2 = float(entries[4][2].get())
    takehome1 = float(entries[5][1].get().replace("$","").replace(",",""))
    takehome2 = float(entries[5][2].get().replace("$","").replace(",",""))

    trial = entries[6][1].get()
    start_date = parse(entries[7][1].get())
    avg_ret = float(entries[8][1].get().strip('%'))/100
##    sd_ret = float(entries[9][1].get().strip('%'))/100
    cpi = float(entries[10][1].get().strip('%'))/100
    proj_exp = float(entries[11][1].get().replace("$","").replace(",",""))
    file_ss = parse(entries[12][1].get())
    soc_sec = float(entries[13][1].get().replace("$","").replace(",",""))
    hc = float(entries[14][1].get().replace("$","").replace(",",""))
    hc_cpi = float(entries[15][1].get().strip('%'))/100
    qual_tot = float(entries[16][1].get().replace("$","").replace(",",""))
    nonq_tot = float(entries[17][1].get().replace("$","").replace(",",""))
    liabilities = float(entries[18][1].get().replace("$","").replace(",",""))
    liabilities = 0.0

    state3_end = bd2 + datetime.timedelta(days = 95*365.25)

    my_date = timeline[row_cnt-1][0] + datetime.timedelta(days = 365.25)
    while my_date <= state3_end:
        act_ret = random.gauss(avg_ret, sd_ret)
##        ret_index = my_date.year - start_date.year
##        act_ret = ret_list[ret_index]

        delta_time = my_date - start_date
        expenses = proj_exp*((1+cpi)**(delta_time.days/365.25))
        health_care = hc*((1+hc_cpi)**(delta_time.days/365.25))
        ss_income =soc_sec*((1+cpi)**(delta_time.days/365.25))
        taxes = calc_taxes((timeline[row_cnt-1][2] * act_ret + ss_income*0.85), new_tax)
        timeline[row_cnt][0] = my_date
        timeline[row_cnt][1] = timeline[row_cnt-1][1]*(1+act_ret) + 0 + 0
        timeline[row_cnt][2] = timeline[row_cnt-1][2]*(1+act_ret) + 0 + 0 - expenses - taxes - health_care + ss_income
        timeline[row_cnt][3] = ss_income      #SS income
        timeline[row_cnt][4] = expenses      #Expenses
        timeline[row_cnt][5] = timeline[row_cnt-1][2] * act_ret + ss_income*0.85       #NQ Taxable Income
        timeline[row_cnt][6] = 0      #Q Taxable Income
        timeline[row_cnt][7] = taxes      #Taxes
        timeline[row_cnt][8] = health_care      #Healthcare
        age = timeline[row_cnt][0] - bd2
        timeline[row_cnt][9] = age.days/365.25
        timeline[row_cnt][10] = timeline[row_cnt][4] + timeline[row_cnt][7] + timeline[row_cnt][8]
        if timeline[row_cnt][2] < 0:
##            back_add_taxes = timeline[row_cnt][1] + timeline[row_cnt][2] + taxes
            taxes = calc_taxes(expenses + timeline[row_cnt - 1][7] + health_care + liabilities- ss_income + ss_income*0.85, new_tax)
            timeline[row_cnt][1] = timeline[row_cnt][1] - expenses - taxes - health_care + ss_income
            timeline[row_cnt][2] = 0
            timeline[row_cnt][5] = 0      #NQ Taxable Income
            timeline[row_cnt][6] = expenses - ss_income*0.15      #Q Taxable Income
            timeline[row_cnt][7] = taxes      #Taxes
            timeline[row_cnt][8] = health_care      #Healthcare
            timeline[row_cnt][10] = timeline[row_cnt][4] + timeline[row_cnt][7] + timeline[row_cnt][8]
        row_cnt = row_cnt + 1
        my_date = my_date + datetime.timedelta(days = 365.25)
##        if timeline[row_cnt][1] + timeline[row_cnt][2] < 0:
##            my_date = my_date + datetime.timedelta(days = 100*365.25)
##            return(row_cnt + 1)

    timeline[row_cnt][0] = state3_end
    age = timeline[row_cnt][0] - bd2
    timeline[row_cnt][9] = age.days/365.25
    act_ret = random.gauss(avg_ret, sd_ret)
##    ret_index = my_date.year - start_date.year
##    act_ret = ret_list[ret_index]

    taxes = calc_taxes(timeline[row_cnt-1][2] * act_ret, new_tax)
    delta_time = state3_end - (my_date - datetime.timedelta(days = 365.25))
    timeline[row_cnt][1] = timeline[row_cnt-1][1]*((1+act_ret)**(delta_time.days/365.25)) - (expenses - taxes + ss_income)*delta_time.days/365.25
    row_cnt = row_cnt + 1
    timeline[row_cnt][0] = state3_end
    age = timeline[row_cnt][0] - bd2
    timeline[row_cnt][9] = age.days/365.25
    timeline[row_cnt][1] = 0
    timeline[row_cnt][10] = timeline[row_cnt][4] + timeline[row_cnt][7] + timeline[row_cnt][8]

    return(row_cnt + 1)

