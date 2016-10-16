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
    voc, priorProbs, condProbs = readData(TRAINEDDATA)
    filenames = os.listdir(DIRECTORY)
    for file in filenames:
        print("======================")
        documentTokens, correctMinistry = readDocument(file)
        if documentTokens == "not readable":
            continue
        for word in documentTokens:
            if not word in voc:
                documentTokens.remove(word)
        # print(documentTokens)
        classScores = scoreDocument(documentTokens, priorProbs, condProbs)
        print("geclassificeerd als: " + str(CLASSES[classScores.index(max(classScores))]))
        if correctMinistry == CLASSES[classScores.index(max(classScores))]:
            correctClassified += 1
        totalClassified += 1
    print("accuracy: " + str(correctClassified/totalClassified))


def readDocument(filename):
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
        print("correcte ministerie: " + ministry)
    else:
        print("geen ministerie gevonden")
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
    # try:
    #     inhoud = soup.findAll("item", {"attribuut" : "Inhoud"})[0].get_text()
    # except IndexError:
    #     # inhoud is regularly absent from data
    #     pass
    # try:
    #     bib = soup.findAll("item", {"attribuut" : "Bibliografische_omschrijving"})[0].get_text()
    #     trefwoorden = soup.findAll("item", {"attribuut" : "Trefwoorden"})[0].get_text()
    #     vragen = soup.vragen.get_text()
    #     antwoorden = soup.antwoorden.get_text()
    #     rubriek = soup.findAll("item", {"attribuut" : "Rubriek"})[0].get_text()
    # except IndexError:
    #     print("something went wrong while parsing File: " + str(filename) + ", continuing")
    #     pass
    
    filestring = ''.join([ministry, bib, inhoud, trefwoorden, vragen, antwoorden, rubriek])
    return nltk.word_tokenize(filestring), ministry

def readData(TRAINEDDATA):
    with open('trained_data.pik', 'rb') as f:
        voc, priorProbs, condProbs = pickle.load(f)
    return voc, priorProbs, condProbs


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