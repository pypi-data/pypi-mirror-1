# -*- coding: utf-8 -*-

import pickle

from django.shortcuts import render_to_response 
from django.http import HttpResponse

from tmpfile import pickledDataPath


def display(request):
    "Display a table."

    data = pickle.load(open(pickledDataPath))
    header, table, footer = data
    return render_to_response('table.html', {'header': header, 'table':table, 'footer':footer}) 


def sortAsc(request, colIndex):
    "Sort table by a given column index in ascending order."

    colIndex = int(colIndex)
    data = pickle.load(open(pickledDataPath))
    header, table, footer = data
    table = [[row[colIndex]]+row for row in table]
    table.sort()
    table = [row[1:] for row in table]
    return render_to_response('table.html', {'header': header, 'table':table, 'footer':footer}) 


def sortDesc(request, colIndex):
    "Sort table by a given column index in descending order."

    colIndex = int(colIndex)
    data = pickle.load(open(pickledDataPath))
    header, table, footer = data
    table = [[row[colIndex]]+row for row in table]
    table.sort()
    table.reverse()
    table = [row[1:] for row in table]
    return render_to_response('table.html', {'header': header, 'table':table, 'footer':footer}) 
