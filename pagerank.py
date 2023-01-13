from numpy import genfromtxt
import numpy as np
import csv
import networkx as nx
import matplotlib.pyplot as plt
import pandas as pd
import pickle

if __name__ == "__main__":
    filename = 'matrix.csv'
    columnNames = []
    rowNames = []
    rowFlag = False
    # get all names from column
    with open(filename, 'r') as csvfile:
        datareader = csv.reader(csvfile)
        for row in datareader:
            if not rowFlag:
                rowNames = row[1:]
                rowFlag = True
                continue
            columnNames.append(row[0])
           
    # generate graph from edge list
    f = open('linkDictionary.pickle', 'rb')
    linkDict = pickle.load(f)

    edges = [(j,k) for j , i in linkDict.items() for k in i]
    G = nx.from_edgelist(edges, create_using=nx.DiGraph)

    outboundDict = dict()
    inboundDict = dict()
    scoreDict = dict()
    # find all inbound and outbound links for each node
    for name in columnNames:
        scoreDict[name] = 1
        outboundDict[name] = []
        for self, outbound, data in G.out_edges(name, data=True):
            outboundDict[name].append(outbound)
        inboundDict[name] = []
        for inbound, self, data in G.in_edges(name, data=True):
            inboundDict[name].append(inbound)
    # calculate page rank scores for each node
    for _ in range(0, 20):
        for key in scoreDict.keys():
            b_u = inboundDict[key]
            rank = 0
            for score in b_u:
                r_v = scoreDict[score]
                n_v = len(outboundDict[score])
                rank += (r_v / n_v)
            scoreDict[key] = 0.75 * rank
    # reformat each key
    newScoreDict = dict()
    for key in scoreDict.keys():
        name = key.replace('/', '').replace(':', '')
        newScoreDict[name] = scoreDict[key]        

    # create pickled version of dictionary
    with open('scoreDict.pickle', 'wb') as handle:
        pickle.dump(newScoreDict, handle, protocol=-1)
