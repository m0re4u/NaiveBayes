# Made in Python 3.4
# Search engines 2016
# created on 11-10-2016
# Michiel van der Meer  -  michielmeer@live.nl        -  10749810
# Jonathan Gerbscheid   -  jonathan-gerb@hotmail.com  -  10787852
# Thomas Groot          -  thomas--g@hotmail.com      -  10658017

import os
import re
import math
import numpy as np
from collections import Counter
from bs4 import BeautifulSoup as BS

def main():
	# directory = '../shaks200'
	directory = '../TESTKVR+'
	# tokenizeFiles(directory)
	# createTokenDict(directory)
	classFreq(directory)


def tokenizeFiles(directory):
	for file in os.listdir(directory):
		text = re.sub('<[^<]+>', "", open(directory + '/' + file).read())
		text = text.replace(' ', '\n')
		if not os.path.exists(directory + "_/"):
			os.makedirs(directory + "_/")
		with open(directory + "_/" + file, "w") as f:
			# lowercase tokens
			text = text.lower()
			# remove trailing non word characters and empty lines
			text = re.sub('(\W+\\n)', '\n', text)
			f.write(text)


def classFreq(directory):
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
	classCount = [0] * 11
	for file in os.listdir(directory):
		soup = BS(open(directory + '/' + file), "html.parser")
		docClass = soup.findAll("item", {"attribuut" : "Afkomstig_van"})[0].get_text()
		# print(docClass)
		for i, classy in enumerate(classes):
			docClass = ''.join(docClass.split())
			classy = ''.join(classy.split())
			if docClass == classy:
				classCount[i] += 1

	print("final count of each class")
	print("=========================")
	for i, classy in enumerate(classes):
		print(classy + ": " + str(classCount[i]))


def createTokenDict(directory):
	token_dict = {}
	# Iterate over files
	for i, file in enumerate(os.listdir(directory + "_")):
			# count individual tokens
			mycounts = Counter(open(directory + "_/" + file).readlines()) 
			# loop over the count dict, assigning tokens as keys in the token dict
			for key, value in mycounts.items():
				# if a key already exists in the token dict, store the count of it in the dict, else also create the key
				key = key.replace('\n','')
				if key in token_dict:
					token_dict[key][i] = value
				else:
					token_dict[key] = {}
					token_dict[key][i] = value

if __name__ == '__main__':
	main()
	print("DONE!")