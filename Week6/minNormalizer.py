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

def main():
	directory = '../TESTKVR'
	# list of accepted ministries
	ministryList = ["Ministerie van Algemene Zaken",
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
			soup = BS(open(directory + '/' + file), "html.parser")
		except UnicodeDecodeError:
			print("File could not be parsed, continuing")
		ministryTagList = soup.findAll("item", {"attribuut" : "Afkomstig_van"})
		if len(ministryTagList) > 0:
			ministryTag = ministryTagList[0].get_text()
		else: 
			continue

		bestMinistry = getBestMatch(ministryTag, ministryList)
		ministryTagList[0].contents[0].replaceWith(bestMinistry)

		xml = soup.prettify("utf-8")
		with open(directory + "+/" + file, "wb") as f:
			f.write(xml)


def getBestMatch(foundMinistry, ministryList):
	"""
	Get most similar to foundMinistry option from ministryList by checking for occurence of tokens, otherwise uses string similarity 
	"""
	maxScore = [0,0] # [score, index]

	for i, ministry in enumerate(ministryList):
		# first see if there are direct similar words in the titles if there is
		# choose that ministry and stop
		ministry = str(ministry.encode('utf-8').decode('ascii', 'ignore'))
		foundMinistry = str(foundMinistry.encode('utf-8').decode('ascii', 'ignore'))
		ministry = ministry.lower()
		foundMinistry = foundMinistry.lower()

		ministry = ministry.replace(" en ", "")
		ministry = ministry.replace("zaken", " ")
		ministry = ministry.replace("ministerie van ", "")
		ministry = ministry.replace("ministerie voor ", "")
		foundMinistry = foundMinistry.replace(" en ", "")
		foundMinistry = foundMinistry.replace("zaken", "")
		foundMinistry = foundMinistry.replace("ministerie van ", "")
		foundMinistry = foundMinistry.replace("ministerie voor ", "")

		tokens = foundMinistry.split()
		for token in tokens:
			if token in ministry:
				return ministryList[i]

		# if no ministry is found use string similarity score
		score = jellyfish.levenshtein_distance(foundMinistry, ministryList[i])
		if score > maxScore[0]:
			maxScore[0] = score
			maxScore[1] = i
	return ministryList[maxScore[1]]


if __name__ == '__main__':
	"""
	classifies all documents as one of 11 ministries
	"""
	main()
	print("DONE!")