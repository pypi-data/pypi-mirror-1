indicngramlib
=============
This script is for to generate n-gram(unigram, bigram, trigram) from Indic Unicode text.
To read more about N-Gram please visit http://en.wikipedia.org/wiki/N-gram.

This script is released under GNU GPL licence.
No commercial use is allowed. 
If you are using the script for your research purpose please refer it.
Also send a mail to jaganadhg@gamil.com (because I am happy to know that some body is using this)

The software is provided as such. No warranty.

Installation
===========

To install it run python setup.py install

Usage
=======
This library provides the following functions.
unigram()
bigram()
trigram()
printUnifreq()
printBigram()
printTrigram()

The library is designed such a way that one can use it for
1) To view the output data (in command line)
2) To store the data in to a file
3) To use the output of this library in a program where it is utilised.

The unigram() and printUnifreq() function
=========================================

The unigram() function is used to generate unigram from a given text.
The text which is giving as input should be in UTF8 format.

The printUnifreq() function can print the unigram with frequency info.
It can be use in two ways.
	1) To print the unigram and frequency info to the command line
	2) To store unigram and frequency info to a file.

A sample code snippet is given below.

	#!/usr/bin/env python
	from indicngramlib import *
	ngram = indicNgram()
	ngram.unigram("my_lang.txt")
	ngram.printUnifreq() # It will print the output to command line

If you would like to store the content to a file, then replace the last line with the following line.

	ngram.printUnifreq("your_output.txt")

The bigram() and printBigram() function
======================================

The bigram function is used to generate bigram from a text.
The text which is given as input should be in UTF8 format.

The printBigram() function can print the bigram with frequency info.
It can be used in two ways.
	1) To print the bigram and frequency info to the command line.
	2) To store bigram and frequency info to a file.

A sample code snippet is given below.

	#!/usr/bin/env python
	from indicngramlib import *
	ngram = indicNgram()
	ngram.bigram("your_text.txt")
	ngram.printBigram() # It will print the output to command line

If you would lke to store the bigram and frequency infro to file, then replace the last line with the following line.

	ngram.printBigram("your_out.txt")

The trigram() and printTrigram() function
=========================================

The trigram() function is used to generate trigram from a given text.
The text whixh s given as input should be in UTF8 format.

The printTrigram() function can print the trigram with frequency info.
It can be used in two ways.
	1) To print the trigram and frequency info to command line.
	2) To store trigram and frequency info to a file.

A sample code snippet is given below.

	#!/usr/bin/env python
	from indicngramlib import *
	ngram = indicNgram()
	ngram.trigram("your_text.txt")
	ngram.printTrigram() # It will print the output to command line

If you would like o store the output to file replace last line with 

	ngram.printTrigram("your_out.txt")

How to use the output of this library in my Python Program?
===========================================================

It is very easy!!
Import the indicngramlib in your Python script.
If you plan to generate unigram from a text and to use that in your program, follow the steps mentioned below.

	from indicngramlib import *

	ngram = indicNgram()
	myunigram = ngram.unigram("your_text.txt")

So now the 'myunigram', which is a dictioney will contain unigram with frequency infor. 
If you want only unigram just get the keys from 'myunigram'

Like wise you can use bigram() and trigram()

There is a __textReader() function in your lib. May I can use it?
=================================================================

No!!
It is a private function. You cant use that function.


