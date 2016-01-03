#!/usr/bin/env python

# This is the Python3 implementation of the UEAlite stemmer
# DJS Oct 2015

# import modules used here 
import sys
import re
import os
import codecs

# Gather our code in a main() function
def main():
	#textin = open('COMMON.TXT', 'rU')
	#outlist = open('stemmed_text.txt', 'w')
	stem_doc(textin)
	#textin.close()
	#outlist.close()
		
def stem_doc(textin):

	if isinstance (textin, str):
		stemmed_word = ['','999']
		#print ('stem_doc: textin is string')
	elif isinstance (textin, bytes):
		stemmed_word = ['','999']
		textin = textin.decode('utf-8') 
		#print ('stem_doc: textin is bytes, conveted len=',len(textin))
	else:
		print ('UEAlist stemmer: Error - input is not string or bytes')
	
	textout = '';
	lines = textin.split('\n')
	for line in lines:   ## iterates over the lines of the input
		words = line.split(' ')
		for word in words:
			word = re.sub('\s+', '', word)
			if (word == ''): continue
			if (not word.find('\w')): continue
			#print('main1: word='+word)
			stemmed_word, rule = stem(word)
			if (rule == '90.2'):					# hyphenated words
				m = re.search('(\w+)-(\w+)', word)	# split into 2, treat separately
				word_a = m.group(0)
				word_b = m.group(1)
				stemmed_word, rule = stem(word_a)
				textout += ' '+stemmed_word.lower()
				stemmed_word, rule = stem(word_b)
				textout += ' '+stemmed_word.lower()
			elif (rule == '91'): 					# word is all caps - assumed acronym
				textout += ' '+stemmed_word
			else:
				textout += ' '+stemmed_word.lower()
				
			#print('stem_doc2: word='+word+' stemmed_word='+stemmed_word+' '+rule)

	#print ('main3: textout = '+textout)
	return textout



def stem(word):
 #DJS 02Mar2004, V0.X MCJ Feb2004 - Perl version
 #DJS Oct 2013 - JavaScript version
 #DJS Oct 2015 - Python version
	stemmed_word = ['','999'] # word, ruleno

	stemmed_word[0] = word
	
	origword = word
	maxWord = 'deoxyribonucleicacid'
	maxWordLength = len(maxWord) # or some other suitable value, e.g antidisestablishmentarianism
	maxAcronym = 'CAVASSOO'
	maxAcronymLength = len(maxAcronym) # or some other suitable value, e.g antidisestablishmentarianism

	## first stage deals with spurious words, NNP, apostrophes, specific problem words ##

	#  preliminaries
	if re.search('^is$|^as$|^this$|^has$|^was$|^during$', word):	# word is a frequent problem word (1.01 added)
		stemmed_word[1] = '90'
		stemmed_word[0] = word
		return stemmed_word	
	
	if len(word) > maxWordLength:			# word is too long to be proper 95
		stemmed_word[1]= '95'
		stemmed_word[0] = word
		return stemmed_word
	

	if re.search("'", word):					# word had apostrophe(s) - remove and continue 94
		word = re.sub("'s$", '', word)					# remove possessive singular
		word = re.sub("'$", '', word)					# remove possessive plural
		word = re.sub("n't",'not', word) 				# expand contraction n't
		word = re.sub("'ve",'have', word) 				# expand contraction 've
		word = re.sub("'re",'are', word) 				# expand contraction 're
		word = re.sub("'m",'am', word) 					# expand contraction I'm
		stemmed_word[1] = '94'

	 											# 90-92 detect NNP, acronym, program variable, ...
	 										
	if re.search('\d+', word) and re.search('[a-zA-Z]', word):		# word is all digits 90.3
		stemmed_word[1]= '90.3'
		stemmed_word[0] = word
		return stemmed_word 
	elif re.search('(\w+)-(\w+)', word):			# word is hyphenated 90.2
		stemmed_word[0] = word
		stemmed_word[1] = '90.2'
		#print ('stem_word90.2: stemmed_word =',stemmed_word[0])
		return stemmed_word 
	elif re.search('-', word):						# word has hyphen 90.1
		stemmed_word[1]= '90.1'
		stemmed_word[0] = word
		return stemmed_word 
	elif re.search('_|\d', word):					# word has underscore, digit 90
		stemmed_word[1]= '90'
		stemmed_word[0] = word
		return stemmed_word 
	elif re.search('^[A-Z]+s$', word):				# word is all uppercase with terminal s 91.1
		re.sub('s$', '', word)
		stemmed_word[1]= '91'
		stemmed_word[0] = word
		return stemmed_word
	elif word.isupper():							# word is all uppercase 91
		stemmed_word[1]= '91'
		stemmed_word[0] = word
		return stemmed_word
	elif re.search('\p{IsUpper}.*\p{IsUpper}', word):	# word has multiple uppercase chars 92
		stemmed_word[1]= '92'
		stemmed_word[0] = word
		return stemmed_word
	elif re.search('^\p{IsUpper}{1}', word):		# word is capitalised 93
		stemmed_word[1]= '93'						# assume capitalised words without punctuation are NNP
		stemmed_word[0] = word
		return stemmed_word	
	
	orig_word = word
	stemmed_word = suffix_remove(word, stemmed_word)
	
	if (stemmed_word[1] == '68' and word != stemmed_word[0]):
		# may be understemmed, so go again
		word = stemmed_word[0]
		stemmed_word = suffix_remove(word, stemmed_word) 
		
	return stemmed_word
 
 

def suffix_remove (word, stemmed_word):
	#print('suffix_remove word='+word)
 	# 139 rule version
	if re.search('[a-zA-Z]', word) == -1:
		#print ('suffix_remove1: word = '+word+' stemmed_word = '+stemmed_word[0])
		return stemmed_word
		
	stemmed_word[1] = '0'
	stemmed_word[0] = word
	a1 =''
	a2 = ''
	origword = word
	
	if re.search('aceous$', word.casefold()): 			# word ends in -aceous 1
		word = re.sub('aceous$', '', word) 
		stemmed_word[1] = '1'
	elif re.search('ces$', word.casefold()): 			# word ends in -ces 2
		word = re.sub('s$', '', word)		# strip -s
		word = re.sub('S$', '', word)		# strip -s
		stemmed_word[1] = '2'
	elif re.search('cs$', word.casefold()):			# word ends in -cs 3
		stemmed_word[1] = '3'
	elif re.search('sis$', word.casefold()): 			# word ends in -sis 4
		stemmed_word[1] = '4'
	elif re.search('tis$', word.casefold()): 			# word ends in -tis 5
		stemmed_word[1] = '5'
	elif re.search('ss$', word.casefold()): 			# word ends in -ss 6
		stemmed_word[1] = '6'
	elif re.search('eed$', word.casefold()): 			# word ends in -eed 7
		stemmed_word[1] = '7'
	elif re.search('ued$', word.casefold()): 			# word ends in -ued 8
		word = re.sub('d$', '', word)					# strip -d
		word = re.sub('D$', '', word)					# strip -d
		stemmed_word[1] = '8'
	elif re.search('ues$', word.casefold()):			# word ends in -ues 9
		word = re.sub('s$', '', word)					# strip -s
		word = re.sub('S$', '', word)					# strip -s
		stemmed_word[1] = '9'
	elif re.search('ees$', word.casefold()):			# word ends in -ees 10
		word = re.sub('s$', '', word)					# strip -s
		word = re.sub('S$', '', word)					# strip -s
		stemmed_word[1] = '10'
	elif re.search('iases$', word.casefold()): 			# word ends in -iases 11.4
		word = re.sub('es$', '', word)					# strip -es
		word = re.sub('ES$', '', word)					# strip -es
		stemmed_word[1] = '11.4'
	elif re.search('uses$', word.casefold()): 			# word ends in -uses 11.3 (change 1.01: more take e than not)
		word = re.sub('s$', '', word)					# strip -s
		word = re.sub('S$', '', word)					# strip -s
		stemmed_word[1] = '11.3'
	elif re.search('sses$', word.casefold()): 			# word ends in -sses 11.2
		word = re.sub('es$', '', word)					# strip -es
		word = re.sub('ES$', '', word)					# strip -es
		stemmed_word[1] = '11.2'
	elif re.search('eses$', word.casefold()): 			# word ends in -eses 11.1
		word = re.sub('es$','is', word)
		word = re.sub('ES$','IS', word)
		stemmed_word[1] = '11.1'
	elif re.search('ses$', word.casefold()): 			# word ends in -ses 11
		word = re.sub('s$', '', word)		# strip -s
		word = re.sub('S$', '', word)		# strip -s
		stemmed_word[1] = '11'
	elif re.search('tled$', word.casefold()): 			# word ends in -tled 12.5
		word = re.sub('d$', '', word)		# strip -d
		word = re.sub('D$', '', word)		# strip -d
		stemmed_word[1] = '12.5'
	elif re.search('pled$', word.casefold()): 			# word ends in -pled 12.4
		word = re.sub('d$', '', word)		# strip -d
		word = re.sub('D$', '', word)		# strip -d
		stemmed_word[1] = '12.4'
	elif re.search('bled$', word.casefold()): 			# word ends in -bled 12.3
		word = re.sub('d$', '', word)		# strip -d
		word = re.sub('D$', '', word)		# strip -d
		stemmed_word[1] = '12.3'
	elif re.search('eled$', word.casefold()): 			# word ends in -eled 12.2
		word = re.sub('ed$', '', word)		# strip -ed
		word = re.sub('ED$', '', word)		# strip -ed
		stemmed_word[1] = '12.2'
	elif re.search('lled$', word.casefold()): 			# word ends in -lled 12.1
		word = re.sub('ed$', '', word)		# strip -ed
		word = re.sub('ED$', '', word)		# strip -ed
		stemmed_word[1] = '12.1'
	elif re.search('led$', word.casefold()): 			# word ends in -led 12
		word = re.sub('ed$', '', word)		# strip -ed
		word = re.sub('ED$', '', word)		# strip -ed
		stemmed_word[1] = '12'
	elif re.search('ened$', word.casefold()): 			# word ends in -ened 13.7
		word = re.sub('ed$', '', word)		# strip -ed
		word = re.sub('ED$', '', word)		# strip -ed
		stemmed_word[1] = '13.7'
	elif re.search('ained$', word.casefold()): 		# word ends in -ained 13.6
		word = re.sub('ed$', '', word)		# strip -ed
		word = re.sub('ED$', '', word)		# strip -ed
		stemmed_word[1] = '13.6'
	elif re.search('erned$', word.casefold()): 		# word ends in -erned 13.5
		word = re.sub('ed$', '', word)		# strip -ed
		word = re.sub('ED$', '', word)		# strip -ed
		stemmed_word[1] = '13.5'
	elif re.search('rned$', word.casefold()): 			# word ends in -rned 13.4
		word = re.sub('ed$', '', word)		# strip -ed
		word = re.sub('ED$', '', word)		# strip -ed
		stemmed_word[1] = '13.4'
	elif re.search('nned$', word.casefold()): 			# word ends in -nned 13.3
		word = re.sub('ned$', '', word)		# strip -ned
		word = re.sub('NED$', '', word)		# strip -ned
		stemmed_word[1] = '13.3'
	elif re.search('oned$', word.casefold()): 			# word ends in -oned 13.2
		word = re.sub('ed$', '', word)		# strip -ed
		word = re.sub('ED$', '', word)		# strip -ed
		stemmed_word[1] = '13.2'
	elif re.search('gned$', word.casefold()): 			# word ends in -gned 13.1
		word = re.sub('ed$', '', word)		# strip -ed
		word = re.sub('ED$', '', word)		# strip -ed
		stemmed_word[1] = '13.1'
	elif re.search('ned$', word.casefold()): 			# word ends in -ned 13
		word = re.sub('d$', '', word)		# strip -d
		word = re.sub('D$', '', word)		# strip -d
		stemmed_word[1] = '13'
	elif re.search('ifted$', word.casefold()): 			# word ends in -ifted 14
		word = re.sub('ed$', '', word)		# strip -ed
		word = re.sub('ED$', '', word)		# strip -ed
		stemmed_word[1] = '14'
	elif re.search('ected$', word.casefold()): 			# word ends in -ected 15
		word = re.sub('ed$', '', word)		# strip -ed
		word = re.sub('ED$', '', word)		# strip -ed
		stemmed_word[1] = '15'
	elif re.search('vided$', word.casefold()): 		# word ends in -vied 16
		word = re.sub('d$', '', word)		# strip -d
		word = re.sub('D$', '', word)		# strip -d
		stemmed_word[1] = '16'
	elif re.search('ved$', word.casefold()): 			# word ends in -ved 17
		word = re.sub('d$', '', word)		# strip -d
		word = re.sub('D$', '', word)		# strip -d
		stemmed_word[1] = '17'
	elif re.search('ced$', word.casefold()): 			# word ends in -ced 18
		word = re.sub('d$', '', word)		# strip -d
		word = re.sub('D$', '', word)		# strip -d
		stemmed_word[1] = '18'
	elif re.search('erred$', word.casefold()): 		# word ends in -erred 19
		word = re.sub('red$', '', word)		# strip -red
		word = re.sub('RED$', '', word)		# strip -red
		stemmed_word[1] = '19'
	elif re.search('urred$', word.casefold()): 		# word ends in -urred 20.5
		word = re.sub('red$', '', word)		# strip -red
		word = re.sub('RED$', '', word)		# strip -red
		stemmed_word[1] = '20.5'
	elif re.search('lored$', word.casefold()): 		# word ends in -lored 20.4
		word = re.sub('ed$', '', word)		# strip -ed
		word = re.sub('ED$', '', word)		# strip -ed
		stemmed_word[1] = '20.4'
	elif re.search('eared$', word.casefold()): 		# word ends in -eared 20.3
		word = re.sub('ed$', '', word)		# strip -ed
		word = re.sub('ED$', '', word)		# strip -ed
		stemmed_word[1] = '20.3'
	elif re.search('tored$', word.casefold()): 		# word ends in -tored 20.2
		word = re.sub('ed$','e', word)
		word = re.sub('ED$','E', word)
		stemmed_word[1] = '20.2'
	elif re.search('ered$', word.casefold()): 			# word ends in -ered 20.1
		word = re.sub('ed$', '', word)		# strip -ed
		word = re.sub('eD$', '', word)		# strip -ed
		stemmed_word[1] = '20.1'
	elif re.search('red$', word.casefold()): 			# word ends in -red 20
		word = re.sub('d$', '', word)		# strip -d
		word = re.sub('D$', '', word)		# strip -d
		stemmed_word[1] = '20'
	elif re.search('tted$', word.casefold()): 			# word ends in -tted 21
		word = re.sub('ted$', '', word)		# strip -ted
		word = re.sub('TED$', '', word)		# strip -ted
		stemmed_word[1] = '21'
	elif re.search('noted$', word.casefold()): 		# word ends in -noted 22.4
		word = re.sub('d$', '', word)		# strip -d
		word = re.sub('D$', '', word)		# strip -d
		stemmed_word[1] = '22.4'
	elif re.search('leted$', word.casefold()): 		# word ends in -leted 22.3
		word = re.sub('d$', '', word)		# strip -d
		word = re.sub('D$', '', word)		# strip -d
		stemmed_word[1] = '22.3'
	elif re.search('uted$', word.casefold()): 			# word ends in -ated 22.2
		word = re.sub('d$', '', word)		# strip -d
		word = re.sub('D$', '', word)		# strip -d
		stemmed_word[1] = '22.2'
	elif re.search('ated$', word.casefold()): 			# word ends in -ated 22.1
		word = re.sub('d$', '', word)		# strip -d
		word = re.sub('D$', '', word)		# strip -d
		stemmed_word[1] = '22.1'
	elif re.search('ted$', word.casefold()): 			# word ends in -ted 22
		word = re.sub('ed$', '', word)		# strip -ed
		word = re.sub('ED$', '', word)		# strip -ed
		stemmed_word[1] = '22'
	elif re.search('anges$', word.casefold()): 		# word ends in -anges 23
		word = re.sub('s$', '', word)		# strip -s
		word = re.sub('S$', '', word)		# strip -s
		stemmed_word[1] = '23'
	elif re.search('aining$', word.casefold()): 		# word ends in -aining 24
		word = re.sub('ing$', '', word)		# strip -ing
		word = re.sub('ING$', '', word)		# strip -ing
		stemmed_word[1] = '24'
	elif re.search('acting$', word.casefold()): 		# word ends in -acting 25
		word = re.sub('ing$', '', word)		# strip -ing
		word = re.sub('ING$', '', word)		# strip -ing
		stemmed_word[1] = '25'
	elif re.search('tting$', word.casefold()): 		# word ends in -tting 26
		word = re.sub('ting$', '', word)		# strip -ting
		word = re.sub('TING$', '', word)		# strip -ting
		stemmed_word[1] = '26'
	elif re.search('viding$', word.casefold()): 		# word ends in -viding 27
		word = re.sub('ing$','e', word)
		word = re.sub('ING$','E', word)
		stemmed_word[1] = '27'
	elif re.search('ssed$', word.casefold()): 			# word ends in -ssed 28
		word = re.sub('ed$', '', word)		# strip -ed
		word = re.sub('ED$', '', word)		# strip -ed
		stemmed_word[1] = '28'
	elif re.search('sed$', word.casefold()): 			# word ends in -sed 29
		word = re.sub('d$', '', word)		# strip -d
		word = re.sub('D$', '', word)		# strip -d
		stemmed_word[1] = '29'
	elif re.search('titudes$', word.casefold()): 		# word ends in -titudes 30
		word = re.sub('s$', '', word)		# strip -s
		word = re.sub('S$', '', word)		# strip -s
		stemmed_word[1] = '30'
	elif re.search('umed$', word.casefold()): 			# word ends in -umed 31
		word = re.sub('d$', '', word)		# strip -d
		word = re.sub('D$', '', word)		# strip -d
		stemmed_word[1] = '31'
	elif re.search('ulted$', word.casefold()): 		# word ends in -ulted 32
		word = re.sub('ed$', '', word)		# strip -ed
		word = re.sub('ED$', '', word)		# strip -ed
		stemmed_word[1] = '32'
	elif re.search('uming$', word.casefold()): 		# word ends in -uming 33
		word = re.sub('ing$','e', word)
		word = re.sub('ING$','E', word)
		stemmed_word[1] = '33'
	elif re.search('fulness$', word.casefold()): 		# word ends in -fulness 34
		word = re.sub('ness$', '', word)	# strip -ness
		word = re.sub('NESS$', '', word)	# strip -ness
		stemmed_word[1] = '34'
	elif re.search('ousness$', word.casefold()): 		# word ends in -ousness 35
		word = re.sub('ness$','e', word)
		word = re.sub('NESS$','E', word)
		stemmed_word[1] = '35'
	elif re.search('r[aeiou]bed$', word.casefold()): 	# word ends in -r*bed 36.1 (1.01 added)
		word = re.sub('d$', '', word)		# strip -d
		word = re.sub('D$', '', word)		# strip -d
		stemmed_word[1] = '36'
	elif re.search('bed$', word.casefold()): 			# word ends in -bed 36 (1.01 changed)
		word = re.sub('ed$', '', word)		# strip -ed
		word = re.sub('ED$', '', word)		# strip -ed
		stemmed_word[1] = '36'
	elif re.search('ssing$', word.casefold()): 		#  word ends in -ding 37
		word = re.sub('ing$', '', word)		# strip -ing
		word = re.sub('ING$', '', word)		# strip -ing
		stemmed_word[1] = '37'
	elif re.search('ulting$', word.casefold()): 		# word ends in -ulting 38
		word = re.sub('ing$', '', word)		# strip -ing
		word = re.sub('ING$', '', word)		# strip -ing
		stemmed_word[1] = '38'
	elif re.search('ving$', word.casefold()): 			# word ends in -ving 39
		word = re.sub('ing$','e', word)
		word = re.sub('ING$','E', word)
		stemmed_word[1] = '39'
	elif re.search('eading$', word.casefold()): 		# word ends in -eading 40.7
		word = re.sub('ing$', '', word)		# strip -ing
		word = re.sub('ING$', '', word)		# strip -ing
		stemmed_word[1] = '40.7'
	elif re.search('oading$', word.casefold()): 		# word ends in -oading 40.6
		word = re.sub('ing$', '', word)		# strip -ing
		word = re.sub('ING$', '', word)		# strip -ing
		stemmed_word[1] = '40.6'
	elif re.search('eding$', word.casefold()): 		# word ends in -eding 40.5
		word = re.sub('ing$', '', word)		# strip -ing
		word = re.sub('ING$', '', word)		# strip -ing
		stemmed_word[1] = '40.5'
	elif re.search('dding$', word.casefold()): 		# word ends in -dding 40.4
		word = re.sub('ding$', '', word)		# strip -ding
		word = re.sub('DING$', '', word)		# strip -ding
		stemmed_word[1] = '40.4'
	elif re.search('lding$', word.casefold()): 		# word ends in -lding 40.3
		word = re.sub('ing$', '', word)		# strip -ing
		word = re.sub('ING$', '', word)		# strip -ing
		stemmed_word[1] = '40.3'
	elif re.search('rding$', word.casefold()): 		# word ends in -rding 40.2
		word = re.sub('ing$', '', word)		# strip -ing
		word = re.sub('ING$', '', word)		# strip -ing
		stemmed_word[1] = '40.2'
	elif re.search('nding$', word.casefold()): 		# word ends in -nding 40.1
		word = re.sub('ing$', '', word)		# strip -ing
		word = re.sub('ING$', '', word)		# strip -ing
		stemmed_word[1] = '40.1'
	elif re.search('ding$', word.casefold()): 			# word ends in -ding 40
		word = re.sub('ing$','e', word)
		word = re.sub('ING$','E', word)
		stemmed_word[1] = '40'
	elif re.search('lling$', word.casefold()): 		# word ends in -lling 41
		word = re.sub('ling$', '', word)		# strip -ling
		word = re.sub('LING$', '', word)		# strip -ling
		stemmed_word[1] = '41'
	elif re.search('ealing$', word.casefold()): 		# word ends in -ealing 42.4
		word = re.sub('ing$', '', word)		# strip -ing
		word = re.sub('ING$', '', word)		# strip -ing
		stemmed_word[1] = '42.4'
	elif re.search('oling$', word.casefold()): 		# word ends in -oling 42.3
		word = re.sub('ing$', '', word)		# strip -ing
		word = re.sub('ING$', '', word)		# strip -ing
		stemmed_word[1] = '42.3'
	elif re.search('ailing$', word.casefold()): 		# word ends in -ailing 42.2
		word = re.sub('ing$', '', word)		# strip -ing
		word = re.sub('ING$', '', word)		# strip -ing
		stemmed_word[1] = '42.2'
	elif re.search('eling$', word.casefold()): 		# word ends in -ling 42.1
		word = re.sub('ing$', '', word)		# strip -ing
		word = re.sub('ING$', '', word)		# strip -ing
		stemmed_word[1] = '42.1'
	elif re.search('ling$', word.casefold()): 			# word ends in -ling 42
		word = re.sub('ing$','e', word)
		word = re.sub('ING$','E', word)
		stemmed_word[1] = '42'
	elif re.search('nged$', word.casefold()): 			# word ends in -nged  43.2
		word = re.sub('d$', '', word)		# strip -d
		word = re.sub('D$', '', word)		# strip -d
		stemmed_word[1] = '43.2'
	elif re.search('gged$', word.casefold()): 			# word ends in -gged  43.1
		word = re.sub('ged$', '', word)		# strip -ged
		word = re.sub('GED$', '', word)		# strip -ged
		stemmed_word[1] = '43.1'
	elif re.search('ged$', word.casefold()): 			# word ends in -ged  43
		word = re.sub('d$', '', word)		# strip -d
		word = re.sub('D$', '', word)		# strip -d
		stemmed_word[1] = '43'
	elif re.search('mming$', word.casefold()): 		# word ends in -mming  44.3
		word = re.sub('ming$', '', word)		# strip -ming
		word = re.sub('MING$', '', word)		# strip -ming
		stemmed_word[1] = '44.3'
	elif re.search('rming$', word.casefold()): 		# word ends in -rming  44.2
		word = re.sub('ing$', '', word)		# strip -ing
		word = re.sub('ING$', '', word)		# strip -ing
		stemmed_word[1] = '44.2'
	elif re.search('lming$', word.casefold()): 		# word ends in -lming  44.1
		word = re.sub('ing$', '', word)		# strip -ing
		word = re.sub('ING$', '', word)		# strip -ing
		stemmed_word[1] = '44.1'
	elif re.search('ming$', word.casefold()): 			# word ends in -ming  44
		word = re.sub('ing$','e', word)
		word = re.sub('ING$','E', word)
		stemmed_word[1] = '44'
	elif re.search('nging$', word.casefold()): 		# word ends in -ging 45.2
		word = re.sub('ing$', '', word)		# strip -ing
		word = re.sub('ING$', '', word)		# strip -ing
		stemmed_word[1] = '45.2'
	elif re.search('gging$', word.casefold()): 		# word ends in -ging 45.1
		word = re.sub('ging$', '', word)		# strip -ging
		word = re.sub('GING$', '', word)		# strip -ging
		stemmed_word[1] = '45.1'
	elif re.search('ging$', word.casefold()): 			# word ends in -ging 45
		word = re.sub('ing$','e', word)
		word = re.sub('ING$','E', word)
		stemmed_word[1] = '45'
	elif re.search('aning$', word.casefold()): 		# word ends in -aning 46.6
		word = re.sub('ing$', '', word)		# strip -ing
		word = re.sub('ING$', '', word)		# strip -ing
		stemmed_word[1] = '46.6'
	elif re.search('ening$', word.casefold()): 		# word ends in -ening 46.5
		word = re.sub('ing$', '', word)		# strip -ing
		word = re.sub('ING$', '', word)		# strip -ing
		stemmed_word[1] = '46.5'
	elif re.search('gning$', word.casefold()): 		# word ends in -gning 46.4
		word = re.sub('ing$', '', word)		# strip -ing
		word = re.sub('ING$', '', word)		# strip -ing
		stemmed_word[1] = '46.4'
	elif re.search('nning$', word.casefold()): 		# word ends in -nning 46.3
		word = re.sub('ning$', '', word)		# strip -ning
		word = re.sub('NING$', '', word)		# strip -ning
		stemmed_word[1] = '46.3'
	elif re.search('oning$', word.casefold()): 		# word ends in -oning 46.2
		word = re.sub('ing$', '', word)		# strip -ing
		word = re.sub('ING$', '', word)		# strip -ing
		stemmed_word[1] = '46.2'
	elif re.search('rning$', word.casefold()): 		# word ends in -rning 46.1
		word = re.sub('ing$', '', word)		# strip -ing
		word = re.sub('ING$', '', word)		# strip -ing
		stemmed_word[1] = '46.1'
	elif re.search('ning$', word.casefold()): 			# word ends in -ning 46
		word = re.sub('ing$','e', word)
		word = re.sub('ING$','E', word)
		stemmed_word[1] = '46'
	elif re.search('sting$', word.casefold()): 		# word ends in -sting 47
		word = re.sub('ing$', '', word)		# strip -ing
		word = re.sub('ING$', '', word)		# strip -ing
		stemmed_word[1] = '47'
	elif re.search('eting$', word.casefold()): 		# word ends in -pting 48.4
		word = re.sub('ing$', '', word)		# strip -ing
		word = re.sub('ING$', '', word)		# strip -ing
		stemmed_word[1] = '48.4'
	elif re.search('pting$', word.casefold()): 		# word ends in -pting 48.3
		word = re.sub('ing$', '', word)		# strip -ing
		word = re.sub('ING$', '', word)		# strip -ing
		stemmed_word[1] = '48.3'
	elif re.search('nting$', word.casefold()): 		# word ends in -nting 48.2
		word = re.sub('ing$', '', word)		# strip -ing
		word = re.sub('ING$', '', word)		# strip -ing
		stemmed_word[1] = '48.2'
	elif re.search('cting$', word.casefold()): 		# word ends in -cting 48.1
		word = re.sub('ing$', '', word)		# strip -ing
		word = re.sub('ING$', '', word)		# strip -ing
		stemmed_word[1] = '48.1'
	elif re.search('ting$', word.casefold()): 			# word ends in -ting 48
		word = re.sub('ing$','e', word)
		word = re.sub('ING$','E', word)
		stemmed_word[1] = '48'
	elif re.search('ssed$', word.casefold()): 			# word ends in -ssed 49
		word = re.sub('ed$', '', word)		# strip -ed
		word = re.sub('ED$', '', word)		# strip -ed
		stemmed_word[1] = '49'
	elif re.search('les$', word.casefold()): 			# word ends in -les 50
		word = re.sub('s$', '', word)		# strip -s
		word = re.sub('S$', '', word)		# strip -s
		stemmed_word[1] = '50'
	elif re.search('tes$', word.casefold()): 			# word ends in -tes 51
		word = re.sub('s$', '', word)		# strip -s
		word = re.sub('S$', '', word)		# strip -s
		stemmed_word[1] = '51'
	elif re.search('zed$', word.casefold()): 			# word ends in -zed 52
		word = re.sub('d$', '', word)		# strip -d
		word = re.sub('D$', '', word)		# strip -d
		stemmed_word[1] = '52'
	elif re.search('lled$', word.casefold()): 			# word ends in -lled 53
		word = re.sub('ed$', '', word)		# strip -ed
		word = re.sub('ED$', '', word)		# strip -ed
		stemmed_word[1] = '53'
	elif re.search('iring$', word.casefold()): 		# word ends in -iring 54.4
		word = re.sub('ing$','e', word)
		word = re.sub('ING$','E', word)
		stemmed_word[1] = '54.4'
	elif re.search('uring$', word.casefold()): 		# word ends in -uring 54.3
		word = re.sub('ing$','e', word)
		word = re.sub('ING$','E', word)
		stemmed_word[1] = '54.3'
	elif re.search('ncing$', word.casefold()): 		# word ends in -ncing 54.2
		word = re.sub('ing$','e', word)
		word = re.sub('ING$','E', word)
		stemmed_word[1] = '54.2'
	elif re.search('zing$', word.casefold()): 			# word ends in -zing 54.1
		word = re.sub('ing$','e', word)
		word = re.sub('ING$','E', word)
		stemmed_word[1] = '54.1'
	elif re.search('sing$', word.casefold()): 			# word ends in -sing 54
		word = re.sub('ing$','e', word)
		word = re.sub('ING$','E', word)
		stemmed_word[1] = '54'
	elif re.search('lling$', word.casefold()): 		# word ends in -lling 55
		word = re.sub('ing$', '', word)		# strip -ing
		word = re.sub('ING$', '', word)		# strip -ing
		stemmed_word[1] = '55'
	elif re.search('ied$', word.casefold()): 			# word ends in -ied 56
		word = re.sub('ied$','y', word)
		word = re.sub('IED$','Y', word)
		stemmed_word[1] = '56'
	elif re.search('ating$', word.casefold()): 		# word ends in -ating 57
		word = re.sub('ing$', '', word)		# strip -ing
		word = re.sub('ING$', '', word)		# strip -ing
		stemmed_word[1] = '57'
	elif re.search('thing$', word.casefold()): 		# word ends in -thing 58.1 (1.01 added)
		stemmed_word[1] = '58.1'
	elif re.search('(\w)(\w)ing$', word.casefold()): 	# word ends in -ing 58 xxxxxx
#		a1 = $1
#		a2 = $2
		word = re.sub('ing$', '', word)		# strip -ing
		word = re.sub('ING$', '', word)		# strip -ing
		if (a1 == a2):
			word = word+a1
		stemmed_word[1] = '58'
	elif re.search('ies$', word.casefold()): 			# word ends in -ies 59
		word = re.sub('ies$', 'y', word)		#strip -es
		stemmed_word[1] = '59'
	elif re.search('lves$', word.casefold()): 			# word ends in -lves 60.1
		word = re.sub('ves$','f', word)
		stemmed_word[1] = '60.1'
	elif re.search('ves$', word.casefold()): 			# word ends in -ves 60
		word = re.sub('s$', '', word) 	#changed from s/ves$/f/
		word = re.sub('S$', '', word) 	#changed from s/ves$/f/
		stemmed_word[1] = '60'
	elif re.search('aped$', word.casefold()): 			# word ends in -uded 61.3
		word = re.sub('d$', '', word) 	#strip -d
		word = re.sub('D$', '', word) 	#strip -d
		stemmed_word[1] = '61.3'
	elif re.search('uded$', word.casefold()): 			# word ends in -uded 61.2
		word = re.sub('d$', '', word) 	#strip -d
		word = re.sub('D$', '', word) 	#strip -d
		stemmed_word[1] = '61.2'
	elif re.search('oded$', word.casefold()): 			# word ends in -oded 61.1
		word = re.sub('d$', '', word) 	#strip -d
		word = re.sub('D$', '', word) 	#strip -d
		stemmed_word[1] = '61.1'
	elif re.search('ated$', word.casefold()): 			# word ends in -ated 61
		word = re.sub('d$', '', word) 	#strip -d
		word = re.sub('D$', '', word) 	#strip -d
		stemmed_word[1] = '61'
	elif re.search('(\w)(\w)ed$', word.casefold()): 	# word ends in -ed 62 xxxx
		m = re.search('(\w)(\w)ed$', word.casefold())
		a1 = m.group(0)
		a2 = m.group(1)
		word = re.sub('ed$', '', word)	#strip -ed
		word = re.sub('ED$', '', word)	#strip -ed
		#print ('stem_word62: a1='+a1+' a2='+a2+'word='+word)
		if a1 == a2:
			word = word+a1
		stemmed_word[0] = word
		stemmed_word[1] = '62'
	elif re.search('pes$', word.casefold()): 			# word ends in -pes 63.8 (1.01 added)
		word = re.sub('s$', '', word) 	#strip -s
		word = re.sub('S$', '', word) 	#strip -s
		stemmed_word[1] = '63.8'
	elif re.search('mes$', word.casefold()): 			# word ends in -mes 63.7 (1.01 added)
		word = re.sub('s$', '', word) 	#strip -s
		word = re.sub('S$', '', word) 	#strip -s
		stemmed_word[1] = '63.7'
	elif re.search('ones$', word.casefold()): 			# word ends in -ones 63.6
		word = re.sub('s$', '', word) 	#strip -s
		word = re.sub('S$', '', word) 	#strip -s
		stemmed_word[1] = '63.6'
	elif re.search('izes$', word.casefold()): 			# word ends in -izes 63.5
		word = re.sub('s$', '', word) 	#strip -s
		word = re.sub('S$', '', word) 	#strip -s
		stemmed_word[1] = '63.5'
	elif re.search('ures$', word.casefold()): 			# word ends in -ures 63.4
		word = re.sub('s$', '', word) 	#strip -s
		word = re.sub('S$', '', word) 	#strip -s
		stemmed_word[1] = '63.4'
	elif re.search('ines$', word.casefold()): 			# word ends in -ines 63.3
		word = re.sub('s$', '', word) 	#strip -s
		word = re.sub('S$', '', word) 	#strip -s
		stemmed_word[1] = '63.3'
	elif re.search('ides$', word.casefold()): 			# word ends in -ides 63.2
		word = re.sub('s$', '', word) 	#strip -s
		word = re.sub('S$', '', word) 	#strip -s
		stemmed_word[1] = '63.2'
	elif re.search('ges$', word.casefold()): 			# word ends in -ges 63.1
		word = re.sub('s$', '', word) 	#strip -s
		word = re.sub('S$', '', word) 	#strip -s
		stemmed_word[1] = '63.1'
	elif re.search('es$', word.casefold()): 				# word ends in -es 63
		word = re.sub('es$', '', word) 	#strip -es
		word = re.sub('ES$', '', word) 	#strip -es
		stemmed_word[1] = '63'
	elif re.search('is$', word.casefold()): 				# word ends in -is 64
		word = re.sub('is$','e', word) 			# replace -is
		word = re.sub('IS$','E', word) 			# replace -is
		stemmed_word[1] = '64'
	elif re.search('ous$', word.casefold()): 				# word ends in -ous 65
		stemmed_word[1] = '65'	
	elif re.search('ums$', word.casefold()): 				# word ends in -ums 66
		stemmed_word[1] = '66'
	elif re.search('us$', word.casefold()): 				# word ends in -us 67
		stemmed_word[1] = '67'
	elif re.search('s$', word.casefold()): 					# word ends in -s 68
		word = re.sub('s$', '', word) 					# strip -s
		word = re.sub('S$', '', word) 					# strip -s
		a1 = word
		stemmed_word[0] = word
		if stemmed_word[1] == '0':
			stemmed_word[1] = '68'
			
	stemmed_word[0] = word
	#if word != origword:
	#	print ('suffix_remove1: '+origword+' to '+stemmed_word[0]+' ('+stemmed_word[1]+')')
	
	return stemmed_word

  
  
  
  
# Standard boilerplate to call the main() function to begin
# the program.
if __name__ == '__main__':
    main()
