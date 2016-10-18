# Made in Python 3.4
# Search engines 2016
# created on 11-10-2016
# Michiel van der Meer  -  michielmeer@live.nl        -  10749810
# Jonathan Gerbscheid   -  jonathan-gerb@hotmail.com  -  10787852
# Thomas Groot          -  thomas--g@hotmail.com      -  10658017
import pickle
import math
import os
import nltk
from bs4 import BeautifulSoup as BS
from collections import Counter
import sys
import time

TRAINEDDATA = 'trained_data'
DIRECTORY = '../KVR_TEST'
CLASSES = ["Ministerie van Algemene Zaken",
            "Ministerie van Binnenlandse Zaken en Konkrijksrelaties",
            "Ministerie van Buitenlandse Zaken",
            "Ministerie van Defensie",
            "Ministerie van Economische Zaken",
            "Ministerie van Financien",
            "Ministerie van Infrastructuur en Milieu",
            "Ministerie van Onderwijs, Cultuur en Wetenschap",
            "Ministerie van Sociale Zaken en Werkgelegenheid",
            "Ministerie van Veiligheid en Justitie",
            "Ministerie van Volksgezondheid, Welzijn en Sport",
            "Ministerie van Economische Zaken, Landbouw en Innovatie",
            "Ministerie van Verkeer en Waterstaat",
            "Ministerie van Volkshuisvesting, Ruimtelijke Ordening en Milieubeheer",
            "Ministerie voor Vreemdelingenzaken en Integratie",
            "Ministerie van Landbouw, Natuur en Voedselkwaliteit",
         ]


def main():
    totalClassified = 0
    correctClassified = 0
    voc, priorProbs, condProbs, wordAppearsIn, filesInClass, parsedFiles = readData(TRAINEDDATA)
    filenames = os.listdir(DIRECTORY)
    for file in filenames:
        # print("======================")
        sys.stdout.flush()
        sys.stdout.write("\r{0}".format("files classified: " + str(totalClassified)))
        documentTokens, correctMinistry = readDocument(file)
        if documentTokens == "not readable":
            continue
        for word in documentTokens:
            if not word in voc:
                documentTokens.remove(word)
        # print(documentTokens)
        classScores = scoreDocument(documentTokens, priorProbs, condProbs)
        # print("geclassificeerd als: " + str(CLASSES[classScores.index(max(classScores))]))
        if correctMinistry == CLASSES[classScores.index(max(classScores))]:
            correctClassified += 1
        totalClassified += 1
    # =======================
    # The following part is commented because it is excruciatingly slow and mostely untested.
    # =======================

    # mutualProbs = {}
    # county = 0
    # print(len(voc))
    # for word in voc:
    #     sys.stdout.write("\r{0}".format("Words done: " + str(county)))
    #     sys.stdout.flush()
    #     county += 1
    #     mutualProbs[word] = [0] * 16
    #     for i in range(16):
    #         mutualProbs[word][i] = getMutualInformation(word, wordAppearsIn, filesInClass, parsedFiles, i)


    print("Finished with classification!")
    print("=============================")
    # print()
    list1 = []
    print("meest informatieve woorden voor: " + CLASSES[0] + ": ")
    county = 0
    for key, value in mutualProbs.keys():
        print("keys done: "+ str(county))
        county += 1
        list1.append((key, value[0]))
    sortedlist = sorted(list1, key=lambda tup:tup[1])
    print(sortedlist[:10])
    print("=============================")
    # print("accuracy: " + str(correctClassified/totalClassified))
    print("True positives: " + str(correctClassified))
    print("")

def getMutualInformation(term, wordAppearsIn, filesInClass, parsedFiles,classy):
    """
    classy is a number from 0 o 15
    """
    if term in wordAppearsIn:
        filesPos = wordAppearsIn[term]
    else:
        return 0
    classFiles = filesInClass[CLASSES[classy]]
    N = len(parsedFiles)
    N11 = len([x for x in filesPos if x in classFiles and x in filesPos])
    N10 = len([x for x in filesPos if x not in classFiles])
    N01 = len([x for x in classFiles if x not in filesPos])
    N00 = N - N11 - N10 - N01
    # print("N11: " + str(N11))
    # print("N10: " + str(N10))
    # print("N01: " + str(N01))
    # print("N00: " + str(N00))
    # print("N: " + str(N))
    IUC = 0
    try:
        if N11 == 0:
            A = 0
        else:
            A = N11/N * math.log2((N * N11)/((N11 + N10) * (N11 + N01)))
        if N01 == 0:
            B = 0
        else:
            B = N01/N * math.log2((N * N01)/((N01 + N00) * (N11 + N01)))
        if N10 == 0:
            C = 0
        else:
            C = N10/N * math.log2((N * N10)/((N11 + N10) * (N10 + N00)))
        if N00 == 0:
            D = 0
        else:
            D = N00/N * math.log2((N * N00)/((N01 + N00) * (N10 + N00)))
        IUC = A + B + C + D
    except:
        return 0
    return IUC


def readDocument(filename):
    """
    Reads and tokenizes a files structured as a kamervraag, returns both the tokens
    retrieved from the file and the correct class.
    """
    try:
        soup = BS(open(DIRECTORY + '/' + filename), "lxml")
    except UnicodeDecodeError:
        print("File: " + str(filename) + " could not be read, continuing")
        return "not readable"
    ministry = ""
    ministryTagList = soup.findAll("item", {"attribuut" : "Afkomstig_van"})
    if len(ministryTagList) > 0:
        ministry = ministryTagList[0].get_text()
        ministry = ministry[6:-5]
        # print("correcte ministerie: " + ministry)
    # else:
        # print("geen ministerie gevonden")
    bib = ""
    inhoud = ""
    trefwoorden = ""
    vragen = ""
    antwoorden = ""
    rubriek = ""
    try:
        bib = soup.findAll("item", {"attribuut" : "Bibliografische_omschrijving"})[0].get_text()
    except IndexError:
        print("skipped biblio")
        pass
    try:
        inhoud = soup.findAll("item", {"attribuut" : "Inhoud"})[0].get_text()
    except IndexError:
        # print("skipped inhoud")
        pass
    try:
        trefwoorden = soup.findAll("item", {"attribuut" : "Trefwoorden"})[0].get_text()
    except IndexError:
        print("skipped trefwoorden")
        pass
    try:
        vragen = soup.vragen.get_text()
    except IndexError:
        print("skipped vragen")
        pass
    try:
        antwoorden = soup.antwoorden.get_text()
    except IndexError:
        print("skipped antwoorden")
        pass
    try:
        rubriek = soup.findAll("item", {"attribuut" : "Rubriek"})[0].get_text()
    except IndexError:
        print("skipped rubriek")
        pass
    filestring = ''.join([ministry, bib, inhoud, trefwoorden, vragen, antwoorden, rubriek])
    return nltk.word_tokenize(filestring), ministry

def readData(TRAINEDDATA):
    with open('trained_data.pik', 'rb') as f:
        voc, priorProbs, condProbs, wordAppearsIn, filesInClass, parsedFiles = pickle.load(f)
    return voc, priorProbs, condProbs, wordAppearsIn, filesInClass, parsedFiles


def scoreDocument(tokens, priorProbs, condProbs):
    scores = [0] * len(priorProbs)
    for i, priorProb in enumerate(priorProbs):
        # print(priorProb)
        scores[i] = math.log10(priorProb)
        for token in tokens:
            if token in condProbs:
                scores[i] += math.log10(condProbs[token][i])
    return scores


if __name__ == '__main__':
    """
    classifies all documents as one of 11 ministries
    """
    main()
    print("DONE!")