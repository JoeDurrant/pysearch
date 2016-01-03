# -*- coding: utf-8 -*-
import json # used to read in corpus data
import math as math # used for logarithms
import matplotlib
"""
Module to create tf*idf vectors from given index data

Author: aau14dku / 100091995
"""

docids = []
postings = {}
vocab = []
numofwordsindoc = [] # global variables

'''
Method to return inverse document frequency from given postings dictionary 
with the format: postings{wordid : {docid: wordfrequency}}
Returns dictionary in format idf{wordid : idf}
'''
def get_idf(postings_list):
    idf_dict = {}
    for wordid in postings:
        idf_dict[wordid] = math.log(len(docids) / len(postings[wordid]))
    return idf_dict

'''
Method to return the term frequency of a given corpus.
Term frequency returned as dictionary in format tf{docid : {wordid : tf}}
'''
def get_tf(docwordcounts, postings_list):
    tf_dict = {}
    for wordid in postings_list: # for each word in postings file
        for docid in postings_list[wordid]: # for each doc containing that word
            if docid in tf_dict: # 
                tf_dict[docid][wordid] = float(postings_list[wordid][docid] / docwordcounts[int(docid)])
            else:
                tf_dict[docid] = {} # initialising inner dict to avoid KeyError
                tf_dict[docid][wordid] = float(postings_list[wordid][docid] / docwordcounts[int(docid)])
    return tf_dict
    
'''
Method to generate tfidf vectors from pre calculated term frequency and inverse
document frequency values. Returns a dictionary of this format: 
tfidf{docid{wordid : tfidf_value}}
'''
def get_tfidf(tf, idf, postings_list):
    tfidf_dict = {}
    for wordid in postings_list:
        for docid in postings_list[wordid]:
            if docid in tfidf_dict:
                tfidf_dict[docid][wordid] = tf[docid][wordid] * idf[wordid] # computing tfidf vectors
            else:
                tfidf_dict[docid] = {} # initialising inner dict to avoid KeyError
                tfidf_dict[docid][wordid] = tf[docid][wordid] * idf[wordid]
    return tfidf_dict

def main():
    global docids
    global postings
    global vocab    
    global numofwordsindoc # refs to globals
    
    with open('vocab.json', 'r') as vocabInput: # reading in index data from .json files
        vocab = json.load(vocabInput)
    with open('postings.json', 'r') as postingsInput:
        postings = json.load(postingsInput)
    with open('docids.json', 'r') as fp:
        docids = json.load(fp)
    with open('docwordcount.json', 'r') as wordcountsInput:
        numofwordsindoc = json.load(wordcountsInput)

    idf = get_idf(postings)
    tf = get_tf(numofwordsindoc, postings)
    tfidf = get_tfidf(tf, idf, postings)

    
    with open('idf.json', 'w') as idf_output: # dumping tf, idf and tfidf to file (mainly for testing purposes)
        json.dump(idf, idf_output)
    with open('tf.json', 'w') as tf_output:
        json.dump(tf, tf_output)
    with open('tfidf.json', 'w') as tfidf_output:
        json.dump(tfidf, tfidf_output)

    print('success')
if __name__ == '__main__':
    main()