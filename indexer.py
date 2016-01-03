import re
from UEAlite import stem_doc # added Oct 2015 DJS
import json


# global declarations for doclist, postings, vocabulary
docids = []
postings = {}
vocab = []
vocabsize = 0	# current size of vocabulary
corpustot = 0	# Lab2 4.2
capscount = 0	# lab2 4.3
numofwordsindoc = [] # Store word counts for each document in array (will be indexed with same values as docid)

def main():
    print("Run crawler, will use methods from this file")
	
def write_index():
    #declare refs to global variables
    global docids
    global postings
    global vocab
    global numofwordsindoc
    
    # writing index files to json for easier retrieval
    with open('docids.json', 'w') as file1:
        json.dump(docids, file1)
    with open('vocab.json', 'w') as file2:
        json.dump(vocab, file2)
    with open('postings.json', 'w') as file3:
        json.dump(postings, file3)
    with open('docwordcount.json', 'w') as file4:
        json.dump(numofwordsindoc, file4)
        '''
    #outlist1 = open('docids.txt', 'w')
    outlist2 = open('vocab.txt', 'w')
    outlist3 = open('postings.txt', 'w')
    outlist4 = open('docwordcount.txt', 'w')
    
    #print (docids, file=outlist1)
    print (vocab, file=outlist2)
    print (postings, file=outlist3)
    print (numofwordsindoc, file=outlist4)

    #outlist1.close()
    outlist2.close()
    outlist3.close()
    outlist4.close()
    '''
    return
	
	
def make_index(url, page_contents):
    # declare refs to global variables
    global docids
    global doclist
    global postings
    global vocab
    global corpustot
    global numofwordsindoc
    
    #extract the words from the page contents
    
    if (isinstance(page_contents, bytes)): # convert bytes to string if necessary
        page_contents = page_contents.decode('utf-8')
    else:
        c = page_contents
    ## the raw regex route
    # can easily be refined to be more selective
    c = re.sub('\\\\n|\\\\r|\\\\t', ' ', page_contents)
    c = re.sub('<script.*?script>', ' ', c) # get rid of scripts
    c = re.sub('<style.*?style>', ' ', c)	# get rid of styles
    c = re.sub('<link.*?link>|<link.*?>', ' ', c) # get rid of links
    c = re.sub('<.*?>', ' ', c)		# get rid of HTML tags
    c = re.sub('{.*?}', ' ', c)		# get rid of stray JS
    c = re.sub('<--|-->', ' ', c)	# get rid of comments
    c = re.sub('<|>', ' ', c)		# get rid of stray angle brackets
    c = re.sub('&n.*?;', ' ', c)	# get rid of HTML entities
    c = re.sub('\\\\x..', ' ', c)	# get rid of hex values
    c = re.sub('\\\\\'', '\'', c)	# replace \' => '
    c = re.sub(r'[^\x00-\x7F]',' ', c) # remove arbitrary unicode characters 
    page_text = re.sub('\s+', ' ', c)		# replace multiple spaces with a single space
    
    print ('===============================================')
    print ('make_index: url = ', url)
    print ('===============================================')
    
    ### add the url to the doclist (DJS Nov 2015) ###
    # need to worry about duplicates that only differ in the protocol and www.
    # as these are not picked up by the crawler

    if (re.search('https:..', url)):	# match and remove https://
        domain_url = re.sub('https://', '', url)
    elif (re.search('http:..', url)):	# match and remove http://
        domain_url = re.sub('http://', '', url)
    else:
        print ("make_index no match for protocol url=", url)
    if (re.search('www.', domain_url)):	# match and remove www.
        domain_url = re.sub('www.', '', domain_url)
    ### append the url to the list of documents
    if (domain_url in docids): # return if we've seen this before
        return
    else:
        docids.append(domain_url)				# add url to docids table
        docid = str(docids.index(domain_url))	# get a string version of the docid
    
    ##### stemming and other processing goes here #####
    # page_text is the initial content, transformed to words
    page_text = stem_doc(page_text) # Stemming each document
    words = page_text
    
    # initialise docfreq for this document
    # list contains counts for each term in the document
    docfreq = {}
    docwordscount = 0
    
    # add the vocab counts and postings
    for word in words.split():
        docwordscount += 1 # word count for document
        # is the word in the vocabulary
        if (word in vocab):
            wordid = str(vocab.index(word))
        else:
            vocab.append(word)
            wordid = str(vocab.index(word))
            # keep the counts of words in docfreq
        if (wordid in docfreq):
            docfreq[wordid] += 1
        else:
            docfreq[wordid] = 1

    corpustot += docwordscount # add the document total to the corpus total	

    numofwordsindoc.append(docwordscount) # keep track of individual doc word counts
    
    # postings now stored in nested dictionary as json serialization can preserve data structure
    for wordid in docfreq:
        if (not wordid in postings):
            postings[wordid] = {} # initialising inner dictionary to stop KeyError (key not found)
            postings[wordid][docid] = docfreq[wordid]
        else:
            postings[wordid][docid] = docfreq[wordid]
    
    return
    
# Standard boilerplate to call the main() function to begin
# the program.
if __name__ == '__main__':
    main()