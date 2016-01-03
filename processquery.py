# -*- coding: utf-8 -*-
"""
Module to return list of URLs that are relevant to a given query

Author: aau14dku / 100091995
"""
import json
import math

docids = []
postings = {}
vocab = []
numofwordsindoc = [] # global variables
tfidf = {}

def square_root(x):
    return round(math.sqrt(sum([a*a for a in x])),3)
 
def get_cosine_similarity(x,y):
    numerator = sum(a*b for a,b in zip(x,y))
    denominator = square_root(x)*square_root(y)
    return round(numerator/float(denominator),10)     

'''
Method that takes a list of strings (user given query) and returns the tfidf
weighting of the list as a dictionary in the format tfidf{word : tfidf}
'''
def get_query_tfidf(query):
    query_length = len(query)
    tf = {}
    idf = {}
    tfidf = {}
    tfidf_vector = []
    query_vocab = {}
    for word in query:
        if word not in vocab:
            print('Sorry, one or more words from your query is not in any document')
            return
        wordid = str(vocab.index(word))
        if word in query_vocab: # counting terms
            query_vocab[word] += 1
        else:
            query_vocab[word] = 1
        idf[word] = math.log(len(docids) / len(postings[wordid])) # get idf for each word
    for word in query_vocab:
        tf[word] = query_vocab[word] / query_length # get tf for each word
        tfidf[str(vocab.index(word))] = tf[word] * idf[word] # compute tfidf for each word in query
        
    if len(query) > 1: # Don't need to sort unless there is more than one word in the query
        key_list = tfidf.keys()
        for key in key_list:
            tfidf_vector.append(tfidf[key])
    else:
        key_list = tfidf.keys()
        tfidf_vector.append[key_list[0]]
    return tfidf_vector

'''
Method which takes a list of strings (user given query) and returns a list of
documents that contain all strings in the query
'''
def get_doclist(query):
    doclist = []
    for word in query:
        wordid = str(vocab.index(word)) # postings indexed with ID numbers, word itself will cause KeyError
        for key in postings[wordid].keys():
            if key not in doclist:
                doclist.append(key)
    return doclist

'''
Method that takes a document list, and returns a dictionary containing tfidf
vectors for each document in the list
'''
def get_doc_vectors(doclist):
    global tfidf
    for word in vocab:
        wordid = vocab.index(word)
        for docid in doclist:
            if wordid not in tfidf[docid]:
                tfidf[docid][wordid] = 0 # add zero counts to dictionary
                
    vectors = {}    
    for docid in tfidf:
        key_list = tfidf[docid].keys()# Create list of keys for tfidf[docid] dict
        key_list = map(int, key_list) # Convert list data to integer values for correct sorting 
        key_list = sorted(key_list)   # Sort list
        key_list = map(str, key_list) # Convert list data back to str to use as dictionary keys  
        vectors[docid] = []
        for key in key_list:
            if key in tfidf[docid]:
                vectors[docid].append(tfidf[docid][key]) # Store vector as list inside of 
    return vectors

def main():
    global postings    
    global vocab
    global docids # refs to globals
    global tfidf    
    
    with open('postings.json', 'r') as postings_input: # opening json files for index and tfidf data
        postings = json.load(postings_input)
    with open('vocab.json', 'r') as postings_input:
        vocab = json.load(postings_input)
    with open('docids.json', 'r') as docids_input:
        docids = json.load(docids_input)
    with open('tfidf.json', 'r') as tfidf_input:
        tfidf = json.load(tfidf_input)
        
    print('Enter search query:')
    query = input().split() # user input
    
    query_tfidf = get_query_tfidf(query) # Get a tfidf vector for the user's query
    query_doclist = get_doclist(query)
    vectors = get_doc_vectors(query_doclist)    
    
    with open('vectors.json', 'w') as vector_output:
        json.dump(vectors, vector_output)
    
    document_cosine_similarity = {}
    for docid in vectors: # calculate cosine similarity to query for each document
        document_cosine_similarity[docid] = get_cosine_similarity(query_tfidf, vectors[docid])
    
    results_list = []
    i = 0
    for docid in sorted(document_cosine_similarity, key=document_cosine_similarity.get): # Sorting 
        results_list.append(docids[int(docid)])
        print(document_cosine_similarity[docid])
        i+=1        
        if(i >= 11):
            break
        
    with open('results.json', 'w') as results:
        json.dump(results_list, results)
    
if __name__ == '__main__':
    main()