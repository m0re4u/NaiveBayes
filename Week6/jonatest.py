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
from sets import Set

def main():
	data = {}
	directory = '../TESTKVR'
	# list of accepted ministries
	classes = ["Ministerie van Algemene Zaken",
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

	if not os.path.exists(directory + "+"):
		os.mkdir(directory + "+")

	for file in os.listdir(directory):
		try:
			soup = BS(open(directory + '/' + file), "lxml")
		except UnicodeDecodeError:
			print("File could not be parsed, continuing")
		ministryTagList = soup.findAll("item", {"attribuut" : "Afkomstig_van"})
		if len(ministryTagList) > 0:
			ministryTag = ministryTagList[0].get_text()
		else: 
			continue

		bestMinistry = getBestMatch(ministryTag, classes)
		# ministryTagList[0].contents[0].replaceWith(bestMinistry)
		# print("==========================")
		# print("found tag: " + ministryTag)
		# print("matched with: " + bestMinistry)
		# print(file)
		bib = ""
		inhoud = ""
		trefwoorden = ""
		vragen = ""
		antwoorden = ""
		rubriek = ""
		try:
			bib = soup.findAll("item", {"attribuut" : "Bibliografische_omschrijving"})[0].get_text()
			inhoud = soup.findAll("item", {"attribuut" : "Inhoud"})[0].get_text()
			trefwoorden = soup.findAll("item", {"attribuut" : "Trefwoorden"})[0].get_text()
			vragen = soup.vragen.get_text()
			antwoorden = soup.antwoorden.get_text()
			rubriek = soup.findAll("item", {"attribuut" : "Rubriek"})[0].get_text()
		except IndexError:
			pass
		data[file] = [bestMinistry, bib, inhoud, trefwoorden, vragen, antwoorden, rubriek]
		# xml = soup.prettify("utf-8")
		# with open(directory + "+/" + file, "wb") as f:
		# 	f.write(xml)
	classCount = classFreqCounter(data, classes)
	priorProbs = np.array(classCount)
	totalFiles = len(os.listdir(directory))
	priorProbs = np.divide(priorProbs, totalFiles)
	print(priorProbs)
	# print(data.values())
	for value in data.values():
		set(value)




def classFreqCounter(data, classes):
	classCounts = [0] * 16
	print(data.keys())
	for key in data.keys():
		for i, classy in enumerate(classes):
			if classy == data[key][0]:
				classCounts[i] += 1
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


if __name__ == '__main__':
	"""
	classifies all documents as one of 11 ministries
	"""
	main()
	print("DONE!")