# pysearch
An information retrieval system to work over a single domain. Uses the NIST web crawler.

# Searching the current corpus files
Running processquery.py will prompt you for a query: If you enter one and hit return, the documents that the system think are
the most relevant will be saved to results.json (can be opened with a text editor, current corpus is of the University of East
Anglia computing subdomain, as this IR system was originally a piece of coursework) 

# Creating your own corpus
If you wish to rebuild the index and tfidf weights, enter this at the command line whilst in this directory:

python PCcrawler.py --domain to start from-- --only follow links to this subdomain--

This will crawl and index the specified pages. To then compute the tfidf vectors for each document/term, run tfidf.py
from the command line.

Once this is done, processquery.py can be run on the updated index.

# Why are there so many json files?
When I created this system I was saving each step of the TF*IDF calculations as a separate file, to see if I was getting any errors. 
Also, each part of the process is done in a separate python file, meaning I had to save various data structures to ensure they could be used by others - I may update the project to incorporate all code into one terminal command.
