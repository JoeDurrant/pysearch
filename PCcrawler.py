#! /usr/bin/python

"""
 PCcrawler.py is the producer/consumer version of PF crawler.  This will
 be last the version before transforming into the pure-thread version.

 PCcrawler.py is set up to start a crawl form a given list of frontiers,
 pages already visted, and hash_codes already encountered:

 webcrawl( file_to_dump_to, url_matching_pattern, max_num_page_visited,   \
             links_to_visit, links_already_dispatched, \
             hash_codes_already_visited) :

 ----

 A modular version of webcrawler.py that uses two separate function files
 
 [canonical_URL, page_contents, timestamp] = get_webpage(URL)
 links = scoop_hrefs(page_contents)

 to replace the old get_webinfo() function, which did too many things. 
 The advantage of breaking this up into two parts is that we can see which
 pages causes the program to break.  (Also, retrieving a web page from the
 net is very different than parsing a local html string for href links.)

 So before we would write

 [canonical_URL, sha1_hash, links] = get_webinfo(URL, Permission, RegExp)

 we write

  [canonical_URL, page_contents, timestamp] = get_webpage(ULR)
  print canonical_URL
  links = scoop_hrefs(page_contents)
  for href in links
     print href
     etc.

 
 The function get_webpage() also deals with the proper 'robots.txt'
 permission issues (basically, it politely follows any restrictions)
 so we don't need to worry about it here.
""" 


from datetime import datetime
import sys
import os.path
from urllib.parse import urlparse


#########################
#<<<<< get_webpage module 
#########################

from urllib.robotparser import RobotFileParser
from urllib.parse import urlparse
from urllib.parse import urljoin
import urllib.request, urllib.parse, urllib.error
import urllib.request, urllib.error, urllib.parse
import url_errors
from readwg import process_wg_file

Permissions = {}

#  True, if url is allowed by robots.txt permission.  False, otherwise
#
def can_read(url):

  domain = domain_name(url)
  if domain not in Permissions :
         rp = RobotFileParser()
         rp.set_url(urljoin('http://' + domain, 'robots.txt'))
         try :
            rp.read()
         except:
            return False
         
         Permissions[domain] = rp

  res = False
  try:
    res  = Permissions[domain].can_fetch("*", url)
  except:
    return False

  return res


#  This is the function to put into the producer pool
#
# [timestamp, canonical_url, page_contents] = get_webpage(url)
#
def get_webpage(url):

  timestamp = datetime.now().strftime("%Y-%m-%d:%H:%M:%S") 
  #print "get_webpage(" + url + ")"
  if not can_read(url)  :
      return timestamp, url, url_errors.protected_URL

  #  try to open url, if unsuccessful, return default info and exit
  #

  req = urllib.request.Request(url)
  try :
    #print "Opening: " + url
    f = urllib.request.urlopen(req) 
    #print "Opened: " + url
  #
  # changed IOError to "anything" , since urlopen sometimes throws
  # httplib.BadStatusLine() exception, which apparently is not
  # covered under IOError.
  #
  except IOError as e :
     #print "IOError, e: "
     if hasattr(e, 'code'):
        if e.code == 401 :
          #print "Error 401: " 
          return timestamp, url, url_errors.password_URL
        else :
          return timestamp, url, url_errors.invalid_URL

     else:
          #print "No e-code"
          return timestamp, url, url_errors.invalid_URL
  except: 
        return timestamp, url,  url_errors.invalid_URL
  else:
   
     if (f.info().get_content_type() == "text/html"): #altered 03Oct15 DJS
         #print "Sucess: " + url
         try: 
           page_contents = f.read()
         except:
           page_contents = url_errors.error_reading_URL

         return timestamp, f.geturl(), page_contents
     elif (f.info().get_content_type() == "application/pdf"): #added 22Oct15 DJS
         print ('get_webpage: Found a PDF', url)
         return timestamp, f.geturl(), url_errors.not_text_URL
     else:
         #print "not text/html: " + url
         return timestamp, f.geturl(), url_errors.not_text_URL
       

################################
#>>>> end of get_webpage module
################################


################################
#<<<<  scoop_hrefs module
################################

#from BeautifulSoup import BeautifulSoup
from bs4 import BeautifulSoup # added 03Oct2015 DJS
import re

def scoop_hrefs_beautiful_soup(html_page_contents):
  links = []
  try :
     b = BeautifulSoup(html_page_contents, 'html.parser')
  #except (UnicodeEncodeError, UnicodeDecodeError):
  except :
     pass
  else: 
     for tag in b.findAll('a', href=True):
       links.append(tag['href'])


  return links


#Alternate method using (precompiled) regular expressions:


href_regexp = re.compile(b'<a\s+href\s*?="\s*?(.*?)"', re.IGNORECASE | re.MULTILINE) #altered 03Oct15 DJS

def scoop_hrefs_regexp(html_page_contents):
  return href_regexp.findall(html_page_contents)


# use both methods and combine the results
#
def scoop_hrefs(html_page_contents):
    
    return set.union(set(scoop_hrefs_beautiful_soup(html_page_contents)), \
      set(scoop_hrefs_regexp(html_page_contents)))



################################
#>>>>>>  scoop_hrefs module
################################



################################
#<<<<<<  url_tools module
################################

from urllib.parse import urlparse
from urllib.parse import urljoin
from urllib.parse import urlunsplit

def domain_name(url):
    return urlparse(url)[1]


#  Takes "http://foo.com/page1" and "../page2" to
#  create "http://foo.com/page2"
# 
def href2url(originating_page, href):

    # strip out leading and trailing white space
    # and convert, but do *not* convert to lower-case

    href = href.strip()   
    # href = href.replace("%7","~")
    # href = urllib.unquote(href)

    # Parse out the query and anchor section of url
    # and make relative urls (e.g. "../foo.html") into
    # absolute (complete with "http:")

    try: 
      pieces = urlparse( urljoin(originating_page, href))
    except:
      return ''

    url_scheme = pieces[0]
    url_location = pieces[1]
    url_path = pieces[2]
    return  urlunsplit((url_scheme, url_location, url_path, '',''))



################################
#>>>>>  url_tools module
################################






# returns True if this url is not to be followed
# i.e. is a jpg, gif, pdf, zip, or other document
#

def file_extension(filename) :
    (base, ext) = os.path.splitext(filename)
    if (ext == '.' or ext == ''):
      return ''
    else :
      return ext[1:] 



# Global constants
#


# terminal URL extensions (all lower case) not added to the frontier 
#  (links-to-visit)
#

terminal_extensions = set([ \
  #
  # text file extensions
  #
  'doc', 'docx', 'log', 'msg', 'pages', 'rtf', 'tt', 'wpd', 'wps' , \
  #
  # data file extensions
  #
  'accdb', 'blg', 'dat', 'db', 'efx', 'mdb', 'pdb', 'pps', 'ppt', \
  'pptx', 'sdb', 'sdf', 'sql', 'vcf', 'wks', 'xls', 'xlsx', \
  #
  # image  file extensions
  #
  'bmp', 'gif', 'jpg', 'png', 'psd', 'psp', 'thm', 'tif', 'tiff' ,\
  'ai', 'drw', 'eps', 'ps', 'svg', \
  '3dm', 'dwg', 'dxf', 'pln', \
  'indd', 'pct', 'qxd', 'qxp', 'rels',  \
  #'indd', 'pct', 'pdf', 'qxd', 'qxp', 'rels',  \
  #
  # audio file extensions
  #
  'aac', 'aif', 'iff', 'm3u', 'mid', 'mp3', 'mpa', 'ra', 'wav', 'wma' , \
  #
  # video file extensions
  #
  '3g2', '3gp', 'asf', 'asx', 'avi', 'flv', 'mov', 'mp4', 'mpg', \
  'rm', 'swf', 'vob', 'wmv', \
  #
  # executable file extensions
  #
  'sys', 'dmp', 'app', 'bat', 'cgi', 'exe', 'pif', 'vb', 'ws', \
  #
  # compressed file extensions
  #
  'deb', 'gz', 'pkg', 'rar', 'sit', 'sitx', 'tar', 'gz', 'zip', 'zipx', '7z', \
  #
  # programming file extensions
  #
  'c', 'cc', 'cpp', 'h', 'hpp', 'java', 'pl', 'f', 'for', 'js', \
  #
  # misc file extensions
  #
  'dbx', 'msi', 'part', 'torrent', 'yps', 'dmg', 'iso', 'vcd' , \
  #
  #
  ])




# more_audio_file_extensions = set([\
#    '4mp', 'aa3', 'aac', 'abc', 'adg', 'aif', 'aifc', 'aiiff', \
#    'awb', 'cda', 'cdib', 'dcm', 'dct', 'dfc', 'efa', 'f64', 'flac, \
#    'flp', ,'g726', 'gnt', 'imy', 'kfn', 'm3u', m4a', 'm4p', 'm4r', \
#    'mid', 'midi', 'mio', 'mmf', 'mp3', 'mpa', 'mpu', 'msv', 'mt2', \
#    'mte', 'mtp', 'mzp', 'oga', 'ogg', 'omg', 'pvc', 'ra', 'ram', \
#    'rif', 'ul', 'usm', 'vox', 'wav', 'wma' ])
# 
# data_backup_file_extensions = set([ \
#    'abbu', 'alub', 'asd', 'bac, 'bak', 'bbb', 'bks', 'bup', dkb', \
#    'dov', 'bk', 'nbf', 'qbb', qbk', 'tmp', 'xlf'])
# 
# video_file_extensions = set([\
#   'aaf', 'asf, 'avi', 'cvc', 'ddat', 'divx', 'dmb', 'dv',  \
#   'evo', 'f4v', 'flc', 'fli', 'flv', 'giv', 'm1pg', 'm21' \
#   'mj2', 'mjp', 'mp4', 'mp4v', 'mpeg', 'mpeg4', 'mpg2', \
#   'mts', 'svi', 'tivo', 'vob','wmv', 'wmmp' ])
#
#terminal_extensions  =  set([ \
#                          '.jpg', '.pdf', '.gif', '.pdf',   \
#                          '.ps',  '.gz',  '.tar', '.tgz',   \
#                          '.zip', '.ppt', '.txt', '.doc',   \
#                          '.mp3', '.wav', '.mpg', '.mov',   \
#                          '.avi', '.exe', '.qt',  '.jar',   \
#                          '.Z',   '.mat', '.wrl', '.patch', \
#                          '.jpeg','.mpeg'                   \
#                         ])
# 


#
#   return the set of unqiue page links (in universal format --ie. no relative
#          links) on this url
#
#    set of links = extract_all_href_links(url)
#
def extract_all_href_links(page_contents, page_url):
#
    links_on_page = scoop_hrefs(page_contents)
    universal_links = set([])
    for link in links_on_page :
        u = href2url(page_url, link) 
        if (u.startswith('http')) :
           universal_links.add(u)
    return universal_links



def has_http_in_path(url):
  c = urlparse(url)
  if (c[2].find('http') >= 0) or (c[3].find('http') >= 0):
    return True
  else:
    return False


#
# decide which links to follow (i.e. put on frontier) based on domain
# criteria
#
#   set of links = decide_which_links_to_follow(canonical_url, url, page_links)
#
def decide_which_links_to_follow(url_matching_pattern, terminal_extensions, \
		canonical_url, url, page_links ):
	links_to_follow = set([])
    
    # only follow outgoing links if this originates within domain
    #
	for link in page_links:
		#if ( domain_name(link).endswith(url_matching_pattern) and \
		if ( (link.find(url_matching_pattern) >= 0 ) and \
			(file_extension(link).lower() not in terminal_extensions) and
			(not has_http_in_path(link)) ) :
				links_to_follow.add(link)
	return links_to_follow


#
#
def add_links_to_frontier( page_links, links_to_vist ):
	global links_to_visit_lock

	links_to_vist_lock.acquire()
	for links in page_links:
		links_to_vist.add(link)
	links_to_vist_lock.release()



'''
 prints

*  2:2009-10-28:22:07:55 http://math.nist.gov/javanumerics/jama
#  http://math.nist.gov/javanumerics/jama/

'''
def print_header_record(filestream, num_page, page_size, timestamp, url,canonical_url):
    
	print("* ", str(num_page)+ ':' + str(page_size) + ':' + timestamp, end=' ', file=filestream) 
	try: 
		print(url, file=filestream)
	except UnicodeEncodeError:
		print("$" +  url.encode('ascii', 'xmlcharrefreplace'), file=filestream)

	if (url != canonical_url) :
		print("# ", canonical_url, file=filestream)

	filestream.flush()  #make sure this prints, if program breaks

def print_error_record(filestream,num_page,timestamp,url,canonical_url,error):
    #
    print_header_record(filestream, num_page, 0, timestamp, url, canonical_url)
    print(error, file=filestream)
    print("", file=filestream)

def safe_print_url(filestream, url):
    try: 
        print(url, file=filestream)
    except UnicodeEncodeError:
        print("$" + url.encode('ascii', 'xmlcharrefreplace'), file=filestream)


def print_links(filestream, page_links):
    for link in page_links:
       try: 
         print(link, file=filestream)
       except UnicodeEncodeError:
         print("$" + link.encode('ascii', 'xmlcharrefreplace'), file=filestream)
    filestream.flush()  

def print_record(filestream, num_page, page_size, timestamp, \
              url, canonical_url,\
              hash_or_error_code, page_links, hash_codes_already_visited):

    print_header_record(filestream, num_page, page_size, timestamp, url, \
            canonical_url)

    if (hash_or_error_code in url_errors.URL_errors):
       error_code = hash_or_error_code
       print(error_code, file=filestream)
       print("", file=filestream)
       filestream.flush()
       return

    sha1_hash =   hash_or_error_code

    #  if this is an old hash-code, we already know the links
    #  so just stamp a #! to denote this has page been alread processed
    #  and continue to the next page.
    # 
    if (sha1_hash in hash_codes_already_visited) :
        print("!" + sha1_hash, file=filestream)
        print("", file=filestream)
        filestream.flush()
        return
    
    print(sha1_hash, file=filestream)
  
    # print links on page
    #
    for link in page_links:
       try: 
         print(link, file=filestream)
       except UnicodeEncodeError:
         print("$" + link.encode('ascii', 'xmlcharrefreplace'), file=filestream)

    filestream.flush()  

    print("", file=filestream)
      


def  print_frontier(filestream, links_to_visit):
#
	print(" ", file=filestream)
	print("[-- Frontier --]", file=filestream) 
	for edge in links_to_visit:
		print("", edge, file=filestream)
	print("[-- Frontier end --]", file=filestream) 
    

#  producers automatically put url on links_already_dispatched
#
#  [timestamp, canonical_url, url, page_contents] = producer(...)
#
def producer( url, links_already_dispatched):
	links_already_dispatched.add(url)
	return get_webpage(url)
    


############################################################
#
#  for Python v. 2.5 or later
import hashlib

hash_codes_already_visited = set([])
filestream = sys.stdout
url_matching_pattern = ""

def init_process_webpage(url_matching_pattern_, \
      hash_codes_already_visited_, filestream_):

    global hash_codes_already_visted, filestream, url_matching_pattern

    url_matching_pattern = url_matching_pattern_
    hash_codes_already_visited = hash_codes_already_visited_
    filestream = filestream_

    #print "url_matching_pattern: ", url_matching_pattern
   


##################################################
#
#  new_links_to_follow = modular_process_webpage(...)
#
##################################################
def modular_process_webpage( num_page, \
	url, canonical_url,  page_contents, links_already_dispatched, \
	hash_codes_already_visted, url_matching_pattern, filestream):


	if (file_extension(canonical_url) in terminal_extensions):
		return []

	seq_timestamp = datetime.now().strftime("%Y-%m-%d/%H:%M:%S") 

	# if retrival was not succesful (due to permission, password protection)
	# then print the url and its error code, and continue with next page
	#
	if (page_contents in url_errors.URL_errors):
		print_error_record(filestream, num_page, seq_timestamp, url, canonical_url, page_contents)

		# if we see that a particular file-type is not a text (html) file,
		# add its extensions to the terminal file types so we don't keep
		# chasing these types of files.
		#
		# NOTE: this is a heuristic to aid in processing web sites that 
		# contain a lot of user data files (particularly universities and
		# public sites) which often use non-standard file extensions for
		# user-generated data.
		#
		if (page_contents == url_errors.not_text_URL):
			ext = file_extension(canonical_url)
			if (ext != ''):
				terminal_extensions.add( ext )

		return []

	#otherwise, we have a valid page page
	#

	hash_code = hashlib.sha1(page_contents).hexdigest()
	#hash_code = sha.new(page_contents).hexdigest()
  

	print_header_record(filestream, num_page, len(page_contents), \
		seq_timestamp, url, canonical_url)

	 # did we see this hash_code already (under a different url)?
	# if so, then prefix with '!' and skip printing the links
	#
	if (hash_code in hash_codes_already_visited):
		print("!" + hash_code, file=filestream)
		print("", file=filestream)
		return []
	else:
		print(hash_code, file=filestream)

	page_links = extract_all_href_links(page_contents, canonical_url)
	follow_links = decide_which_links_to_follow(url_matching_pattern, \
		terminal_extensions, canonical_url, url, page_links )

	#for url in follow_links:
	for url in page_links:
		safe_print_url(filestream, url)
	print(" ", file=filestream)
	filestream.flush()  

	hash_codes_already_visited.add(hash_code)
   
	return  follow_links 



##################################################
#
#  new_links_to_follow = process_webpage(...)
#
##################################################
def process_webpage( num_page, timestamp, url, canonical_url, page_contents, links_already_dispatched):

	global hash_codes_already_visted, filestream, url_matching_pattern

	# if retrival was not succesful (due to permission, password protection)
	# then print the url and its error code, and continue with next page
	#
	if (page_contents in url_errors.URL_errors):
		print_error_record(filestream, num_page, timestamp, url, canonical_url, page_contents)
		return []

	#otherwise, we have a valid page page
	#
	hash_code = hashlib.sha1(page_contents).hexdigest() #uncommented  DJS 30/9/15
	#hash_code = sha.new(page_contents).hexdigest()	#commented out DJS 30/9/15
	
	seq_timestamp = datetime.now().strftime("%Y-%m-%d:%H:%M:%S") 
        
	#print_header_record(filestream, num_page, len(page_contents), timestamp, url, canonical_url ) #commented out DJS 30/9/15

	# did we see this hash_code already (under a different url)?
	# if so, then prefix with '!' and skip printing the links
	#
	if (hash_code in hash_codes_already_visited):
		print("!" + hash_code, file=filestream)
		print("", file=filestream)
		return []
	else:
		#print >> filestream, hash_code #commented out DJS 30/9/15
		
		#print line to show what's being retrieved - for demonstration only
		#print(num_page, len(page_contents), url, page_contents) #added DJS 30/9/15
		#print(num_page, len(page_contents), url) #added DJS 30/9/15
	
##################### add code here DJS 30/9/15 ################## 

		make_index(url, page_contents) #added DJS Oct 2015

##################################################################
    
	page_links = extract_all_href_links(page_contents, canonical_url)
	follow_links = decide_which_links_to_follow(url_matching_pattern, terminal_extensions, canonical_url, url, page_links )

	#print_links(filestream, follow_links) # commented out DJS Oct 15
	#print('') # commented out DJS Oct 15

	hash_codes_already_visited.add(hash_code)
	
	return  follow_links 
   
############################################################

#
# [num_page, num_edges] = consumer(...)
#
def consumer( filestream, url_matching_pattern, max_num_page_visited,   \
             links_to_visit, links_already_dispatched, \
             hash_codes_already_visited) :

	num_edges = 0
	num_page = 0

  
	while (len(links_to_visit) > 0) and \
		((max_num_page_visited < 1) or (num_page < max_num_page_visited)):


		# here is where we wait for the producer()
		#
		url = links_to_visit.pop()
		timestamp,canonical_url,page_contents = producer(url, links_already_dispatched)
		# mark canonical links also as "seen" 
		#
		if (url != canonical_url) :
			links_already_dispatched.add(canonical_url)
    
		num_page += 1

		links_to_follow = process_webpage(num_page, timestamp, url, canonical_url, page_contents, links_already_dispatched)
  
		num_edges += len(links_to_follow)
		#print ("consumer: url_matching_pattern =", url_matching_pattern)
		
		for link in links_to_follow:
			if (link.find(url_matching_pattern) == -1): 
				continue
			if (re.search('ears/ears', link)): 	# kludge to stop problem in uea.ac.uk/computing DJS Nov2015
				#print ("consumer: matched /ears/ears/ url=", link)
				continue
			if (link not in links_already_dispatched):
				#print ("consumer:link =", link)
				links_to_visit.add(link)
		### end of added block ###
		
		# original commented out DJS Oct 2015
		#for link in links_to_follow:
        #   if link not in links_already_dispatched:
        #         links_to_visit.add(link)


	return num_page, num_edges
    



################################
#>>>>>  main module 
################################

from indexer import write_index # added Oct 2015 DJS
from indexer import make_index # added Oct 2015 DJS


def main():

	NUM_THREADS = 4
	if (len(sys.argv) <= 2)  :
		print("usage is domain-pattern seed-url  [max-num-pages-visited] ")
		print("     -w  domain-pattern")
		print("              | ")
		print("              ^ ")
		print(" Ex:  nist.gov http://math.nist.gov 100 ")
		print("    -w means to continue from a webcrawl dump  (fed into stdin)")
		print(" ")
		sys.exit(2)

	links_to_visit = set([])
	links_already_dispatched = set([])
	max_num_page_visited = 0     #if 0, then there is no limit


	if (sys.argv[1] == "-w"):    #sart from a previous crawl
		process_wg_file(sys.stdin, links_already_dispatched, \
			hash_codes_already_visited, links_to_visit )
		url_matching_pattern = sys.argv[2]
		###### if resuming index creation, need to add call here ######
	else:
		url_matching_pattern = sys.argv[1]
		starting_url = sys.argv[2]
		links_to_visit.add(starting_url)
	if (len(sys.argv) > 3):
		max_num_page_visited = int(sys.argv[3])
 
	print("#!#  domain pattern: ", url_matching_pattern)
	print(" ")


	# go crawl the web...
	#
	num_page, num_edges = \
	consumer( sys.stdout, url_matching_pattern, max_num_page_visited, \
		links_to_visit,  links_already_dispatched, hash_codes_already_visited)

############################################
#	add call here to write results of index creation to file DJS Oct 2015
	write_index()

############################################
  
	print("\n[-- DONE --]\n", file=sys.stdout)
	print("read ", num_page,  " pages.", file=sys.stdout)
	print("number of edges : ", num_edges, file=sys.stdout)
	#print_frontier(sys.stdout, links_to_visit)



if __name__ == "__main__":
	main()


