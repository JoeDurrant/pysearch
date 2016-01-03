#! /usr/bin/python

import sys;
import url_errors

DONE = False
DONE_string = "[-- DONE --]"

'''
Assumes that we are at the current line where that starts with '*'.  The format
is follows the following example:

--------------------------

*  1:2009-09-09:12:56:19 http://physics.nist.gov
e796febb7593fde042a7511a9761da8ce6d84299
http://physics.nist.gov/Divisions/Div842/div842.html
http://physics.nist.gov/MajResProj/Nanotech/nanotech.html

*  2:2009-09-09:12:56:20 http://physics.nist.gov/Divisions/Div842/div842.html
68e24912e780a2076f29b76b64066003a0f05fd0
http://physics.nist.gov/Divisions/Div842/Gp4/group4.html
http://physics.nist.gov/Divisions/Div842/Gp5/index.html
http://www.doc.gov

--------------------------


will process current page to visited_links (along with its hash-code)
and add outgoing links to frontier.

current line:   string
frontier:       set of strings (URLs) to visit
visited_links:  set of strings (URLs) already processed
hash_codes:     set of strings (alphanumeric hash codes) for visited pages

'''


'''
  read a URL (with possible spaces) in the current line
'''
def get_url(line):
  pos = line.find('http')
  if (pos < 0):
     return ''
  else  :
    return line[ line.find('http') : ]


#  The last letter in readline is a '\n', so let's not include it
#
def get_next_line(file):
     line = file.readline()
     if len(line) > 1:
       return line[:-1]
     elif len(line) == 1:
       return ' '
     else:
       return line




def scroll_to_next_webpage(file):
  global DONE
  if not file:
     DONE = True
  current_line = ""
  while (file and (not DONE)) :
    current_line = get_next_line(file)
    if ((current_line == DONE_string) or (current_line == '')):
        DONE = True
        return ''
    #print "scroll: " + current_line
    if (len(current_line)>0 and current_line[0] == '*'):
      #print "   scroll: stop at " + current_line
      return current_line
  return ''





'''
   file              text input file  (the webcrawl dump)
   current_line      string (current line of webcrawl dump)
   frontier          set of strings (URLs to visit)
   visited_links     set of strings (URLs already visited)
   sha_codes         set of strings (hexadecimal hash codes for vistied URLs)
'''
def process_page(file, current_line, frontier, visited_links, sha_codes):

  if DONE :
    return

  home_url = get_url(current_line)

  if (len(home_url) < 1):
      return

  visited_links.add( home_url )

  # remove **
  #print  "home_url = " + home_url
  # ^^^^^^^^^

  frontier.discard(home_url)    # set.remove() assume element is present 
  hash = get_next_line(file)
  if (hash in url_errors.URL_errors):     # one of the special cases 
     return

  if (hash[0] == '#'):
    hash = get_next_line(file)
  elif (hash[0] == '!'):         # already processed URL (via hash contents)
     return


  # remove**
  #print "hash = " + hash
  # ^^^^^^^^^

  sha_codes.add(hash)
  while (True) :
      line = get_next_line(file)
      url = get_url(line)
      if url == "":
         break
      if url not in visited_links:
         # print "   added outlink: " + url
         frontier.add(url)




def process_wg_file(file, visited_links, hash_codes, frontier):
  line = ""
  while (file and not DONE):
    line = scroll_to_next_webpage(file)
    process_page(file, line, frontier, visited_links, hash_codes)


# ***** MAIN *********

def main():

     file = sys.stdin
     frontier = set([])
     visited_links = set([])
     hash_codes = set([])
     process_wg_file(file, visited_links, hash_codes, frontier)


     # now print out the results
  
  
     print(" ")
     print("Visited Links: ")
     print("-------------  ")
     for url in visited_links:
       print(url)
     
     
     print(" ")
     print("Frontier: ")
     print("--------  ")
     for url in frontier:
       print(url)
     
     
     print(" ")
     print("Hash Codes: ")
     print("-----------  ")
     for url in hash_codes:
       print(url)
     
     
     print(" ")
     
  
  
if __name__ == "__main__":
  main()
