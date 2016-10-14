# Made in Python 3.4
# Search engines 2016
# created on 11-10-2016
# Michiel van der Meer  -  michielmeer@live.nl        -  10749810
# Jonathan Gerbscheid   -  jonathan-gerb@hotmail.com  -  10787852
# Thomas Groot          -  thomas--g@hotmail.com      -  10658017
import jellyfish
import os
from bs4 import BeautifulSoup as BS
import unicodedata
import io
import numpy as np
from collections import Set
import nltk
from collections import Counter
import pickle
import sys
import time

CLASSSMOOTHING = 0

def main():
    data = {}
    directory = '../KVR_TRAIN'
    # list of accepted ministries
    classes =  ["Ministerie van Algemene Zaken",
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

    p = 0
    for file in os.listdir(directory):
        p += 1
        sys.stdout.flush()
        sys.stdout.write("\r{0}".format("files read: " + str(p)))
        # print("files processed: " + str(p))
        try:
            soup = BS(open(directory + '/' + file), "lxml")
        except UnicodeDecodeError:
            print("\nFile: " + str(file) + " could not be parsed, continuing")
        ministryTagList = soup.findAll("item", {"attribuut" : "Afkomstig_van"})
        if len(ministryTagList) > 0:
            ministryTag = ministryTagList[0].get_text()
        else: 
            continue
        bestMinistry = getBestMatch(ministryTag, classes)
        bib = ""
        inhoud = ""
        trefwoorden = ""
        vragen = ""
        antwoorden = ""
        rubriek = ""
        try:
            bib = soup.findAll("item", {"attribuut" : "Bibliografische_omschrijving"})[0].get_text()
        except IndexError:
            # print("skipped biblio")
            pass
        try:
            inhoud = soup.findAll("item", {"attribuut" : "Inhoud"})[0].get_text()
        except IndexError:
            # print("skipped inhoud")
            pass
        try:
            trefwoorden = soup.findAll("item", {"attribuut" : "Trefwoorden"})[0].get_text()
        except IndexError:
            # print("skipped trefwoorden")
            pass
        try:
            vragen = soup.vragen.get_text()
        except IndexError:
            # print("skipped vragen")
            pass
        try:
            antwoorden = soup.antwoorden.get_text()
        except IndexError:
            # print("skipped antwoorden")
            pass
        try:
            rubriek = soup.findAll("item", {"attribuut" : "Rubriek"})[0].get_text()
        except IndexError:
            # print("skipped rubriek")
            pass
        
        data[file] = [bestMinistry, bib, inhoud, trefwoorden, vragen, antwoorden, rubriek]

    classCount = classFreqCounter(data, classes)
    print("Calculated frequencies for all classes.")
    totalFiles = len(os.listdir(directory)) + CLASSSMOOTHING
    priorProbs = np.divide(np.array(classCount), totalFiles)
    print("Calculated prior probabilities for all classes.")
    classStrings = getclassStrings(data, classes)
    print("Concatenated files for all classes.")
    vocabulary = getVocabulary(classStrings)
    print("Processed vocabulary.")
    tokenClassCounts = getTokenClassCounts(vocabulary, classStrings)
    print("Calculated class counts for all tokens.")
    conditionalProbs = getConProb(tokenClassCounts, vocabulary, classes)
    print("Calculated conditional probabilities.")
    with open('trained_data.pik', 'wb') as f:
        pickle.dump([vocabulary, priorProbs, conditionalProbs], f, -1)
        print("wrote data to trained_data.pik.")


def getConProb(tct, vocabulary, classes):
    conditionalProbs = {}
    wordsInClass = [sum(item) for item in zip(*tct.values())]
    # print(wordsInClass)

    for word in vocabulary:
        conditionalProbs[word] = [0] * 16

    for i, classy in enumerate(classes):
        for word in vocabulary:
            conditionalProbs[word][i] = (tct[word][i] + 1) / (wordsInClass[i] + len(tct.keys()))
    return conditionalProbs


def getTokenClassCounts(vocabulary, classStrings):
    tct = {}
    for word in vocabulary:
        tct[word] = [0] * len(classStrings)
    for i, classString in enumerate(classStrings):
        tokenCounter = Counter(nltk.word_tokenize(classString))
        for token in list(tokenCounter):
            tct[token][i] = tokenCounter[token]
    return tct


def getclassStrings(data, classes):
    classStrings = [""] * 16
    for key in data.keys():
        for i, docClass in enumerate(classes):
            if(docClass == data[key][0]):
                filestring = ''.join(data[key])
                classStrings[i] = classStrings[i] + filestring
                break
    return classStrings
    
def classFreqCounter(data, classes):
    classCounts = [0] * 16
    for key in data.keys():
        for i, classy in enumerate(classes):
            if classy == data[key][0]:
                classCounts[i] += 1
    for i, n in enumerate(classCounts):
        if n == 0:
            classCounts[i] = 1
            CLASSSMOOTHING =+ 1
    return classCounts


def getBestMatch(foundMinistry, classes):
    """
    Get most similar to foundMinistry option from classes by checking for occurence of tokens, otherwise uses string similarity 
    """
    maxScore = [0,0] # [score, index]

    for i, ministry in enumerate(classes):
        # first see if there are direct similar words in the titles if there is
        # choose that ministry and stop
        ministry = ministry.lower()
        foundMinistry = foundMinistry.lower()

        ministry = ministry.replace("ë", "e")
        ministry = ministry.replace(" en ", "")
        ministry = ministry.replace("zaken", " ")
        ministry = ministry.replace("ministerie van ", "")
        ministry = ministry.replace("ministerie voor ", "")
        foundMinistry = foundMinistry.replace("ë", "e")
        foundMinistry = foundMinistry.replace(" en ", "")
        foundMinistry = foundMinistry.replace("zaken", "")
        foundMinistry = foundMinistry.replace("ministerie van ", "")
        foundMinistry = foundMinistry.replace("ministerie voor ", "")

        tokens = foundMinistry.split()
        for token in tokens:
            # nasty hack, removing the last 3 solves a problem with reading financien wrongly
            # the ministries will still match correctly even after removing 3 characters :)
            if token[:-3] in ministry:
                return classes[i]

        # if no ministry is found use string similarity score
        score = jellyfish.levenshtein_distance(foundMinistry, classes[i])
        if score > maxScore[0]:
            maxScore[0] = score
            maxScore[1] = i
    return classes[maxScore[1]]


def getVocabulary(classStrings):
    datasetString = ''.join(classStrings)
    vocabulary = set(nltk.word_tokenize(datasetString))
    return vocabulary
            
if __name__ == '__main__':
    """
    classifies all documents as one of 11 ministries
    """
    main()
    print("DONE!")