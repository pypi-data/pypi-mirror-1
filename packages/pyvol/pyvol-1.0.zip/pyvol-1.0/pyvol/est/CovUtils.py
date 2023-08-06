"""Module providing some simple utilities for covariance estimators.
"""

import datetime

def GetYear(date):
    "Return year for date"
    return date.year

def GetQuarter(date):
    "Return quarter for date"
    return int((date - datetime.date(date.year,1,1)).days/91.25)

def GetMonth(date):
    "Return month for date"
    return date.month

def GetWeek(date):
    "Return week for date"
    return int((date - datetime.date(date.year,1,1)).days/7)

def GetDay(date):
    "Return day for date"
    return date.weekday()

def Mean(data):
    "Compute mean of input data list."
    return sum(data)/float(len(data))

def Var(data):
    "Compute (biased) variance of input data list."
    avg = Mean(data)
    var = Mean([(d - avg)**2 for d in data])
    return var
