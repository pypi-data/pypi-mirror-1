#!/usr/bin/env python
"""
Author: Jaganadh G
Date: 22/07/2009
Version: 1.0
Copyright(C): Jaganadh G
Bug mail to : jaganadhg@gmail.com
Licence: GNU/GPL V.3+ 
Note: If you are using it for any commercial purpose drop a mail to me.
Name: Indic Languages Corpus Processing Module
Functions: 
	1) unigram() generates unigram with frequency
	2) bigram() generate bigram with frequency
	3) trigram() generates trigrams with frequency
	4) __textReader() private function. Just for reading text and split in to words
	5) printUnifreq()  To print unigram with frequency
	6) printBigram() To print bigram with frequency
	7) printTrigram() To print trigram with frequency.
	
"""

import codecs
import sys
import os
from operator import itemgetter
import re
import string


class indicNgram:
	"""
	A Program for Indic language Corpus(Unicode) Processing
	"""

	def __init__(self):
		"""
		Initialization of the class
		"""


	def unigram(self,text):
		"""
		Function for generating unigrams(word) with frequency from a Unicode text
		Finds number of times occoures in the text and stores to a dictionery 'unifreq'
		Sorts the dictionery and prints it.
		"""

		self.text = text
		#self.unifreq = unifreq
		uniwords = self.__textReader(text)
		#print uniwords
		#global unifreq = {}

		global unifreq
		unifreq = {}

		for word in uniwords:
			unifreq[word] = uniwords.count(word)

		"""
		for unigram,frequency in sorted(unifreq.iteritems(), \
			key=lambda (key,value):(value,key),reverse=True):
			print unigram, frequency
		"""

		"""
		for word in uniwords:
			print word,"\t",uniwords.count(word)
			#print word,"\t",count(uniwords(word))
		"""
		return unifreq


	def printUnifreq(self,outf = None):
		"""
		Function to print unigram.
		The same function can be used to print the output to a file.
		It will print or save the output by frequency.
		The output file name should be given as parameter to the function.
		If no argument is passed to the function it will print the 
		unigram to the command line.
		"""

		self.unifreq = unifreq

		if outf != None:
			out = codecs.open(outf,'w','utf8')
			for unigram,frequency in sorted(unifreq.iteritems(), \
				key=lambda (key,value):(value,key),reverse=True):
				out.write(unigram+" "+str(frequency)+"\n")
		else:
			for unigram,frequency in sorted(unifreq.iteritems(), \
				key=lambda (key,value):(value,key),reverse=True):
				print unigram, frequency
		#print unifreq



	def bigram(self,text):
		"""
		Function to generate bigrams from a given text
		
		"""

		self.text = text
		uniwords = self.__textReader(text)
		bigrams = []

		for w in range(len(uniwords)-1):
			bigram = uniwords[w] + "  " + uniwords[w+1]
			bigrams.append(bigram)
			#print bigram
			#print uniwords[w]," ",uniwords[w+1]

		global bigramfreq	
		bigramfreq = {}

		for bigram in bigrams:
			bigramfreq[bigram] = bigrams.count(bigram)


		"""
		for bigram,frequency in sorted(bigramfreq.iteritems(), \
			key = lambda (key,value):(value,key), reverse = True):
			print bigram," ", frequency
		"""
		"""
		for bigram in bigrams:
			print bigram
		"""
		return bigramfreq


	def printBigram(self,outf = None):
		"""
		Function to print bigram frequency to command prompt or to save in a file.
		The file name should be given as a command line parameter.
		If no argument is given for the function 
		it will print the bigrams to the command line.
		It will print/ or save the bigram by frequency
		"""

		self.bigramfreq = bigramfreq

		if outf != None:
			out = codecs.open(outf,'w','utf8')
			for bigram,frequency in sorted(bigramfreq.iteritems(), \
				key = lambda (key,value):(value,key), reverse = True):
				#print bigram," ", frequency
				out.write(bigram + " " + str(frequency) + "\n")
		else:
			for bigram,frequency in sorted(bigramfreq.iteritems(), \
				key = lambda (key,value):(value,key), reverse = True):
				print bigram," ", frequency



	def trigram(self,text):
		"""
		Function to generate trigram from a given text.
		"""

		self.text = text
		uniwords = self.__textReader(text)
		trigrams = []
		
		for w in range(len(uniwords)-2):
			trigram = uniwords[w] + " " + uniwords[w+1] + " " +uniwords[w+2]
			trigrams.append(trigram)
			#print uniwords[w]," ",uniwords[w+1]," ",uniwords[w+2]

		global trigramfreq
		trigramfreq = {}

		for trigram in trigrams:
			trigramfreq[trigram] = trigrams.count(trigram)

		"""
		for trigram,frequency in sorted(trigramfreq.iteritems(), \
			key = lambda (key,value):(value,key), reverse = True):
			print trigram, " " , frequency
		"""
		"""
		for trigram in trigrams:
			print trigram

		"""
		return trigramfreq



	def printTrigram(self,outf = None):
		"""
		Function to print trigrams to command line or file.
		The file name should be given as argument to function.
		If no argument is given to the function it will 
		print the trigram to the command line.
		"""

		self.trigramfreq = trigramfreq

		if outf != None:
			out = codecs.open(outf,'w','utf8')
			for trigram,frequency in sorted(trigramfreq.iteritems(), \
				key = lambda (key,value):(value,key), reverse = True):
				#print trigram, " " , frequency
				out.write(trigram + " " + str(frequency)+"\n")
		else:
			for trigram,frequency in sorted(trigramfreq.iteritems(), \
				key = lambda (key,value):(value,key), reverse = True):
				print trigram, " " , frequency



	def __textReader(self,text):
		"""
		FUnction to read text and return a list of word.
		The function will read the text, removes the punctuation marks 
		if any and splits the text in to words. 
		This word list will be utilized by unigram() , 
		bigram() and trigram() functions.
		"""

		untxtf = codecs.open(text,'r','utf8')
		unicontent = untxtf.read()
		untxtf.close()

		for punct in string.punctuation:
			unicontent = unicontent.replace(punct,"")

		words = unicontent.split()
	
		return words


def demo():
	try:
		inp_file = sys.argv[1]
	except IndexError:
		print "Usage python indicngramlib.py <input>"

	indicNgram().unigram(inp_file)
	indicNgram().printUnifreq()


if __name__ == '__main__':
	demo()
