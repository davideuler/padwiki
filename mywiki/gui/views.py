from django.http import *
# use subprocess.Popen instead of os.popen, since the former allows unicode characters in commandline string
# import everything from subprocess, in particular, PIPE
import subprocess
from subprocess import *
import os, re, urllib

def index(request):
    return article(request, "Wikipedia")

# due to a werid behavior instroduced by subprocess.Popen, the two function calls subprocess.Popen and os.popen do not always return the same thing. Try "wikipedia" as the search keyword. ASCII version returns 3 results, whereas unicode version returns 1 only.
# therefore, to maintain compatibility, we have two versions of article functions. If the search keyword contains ASCII only, we use the function that ships with the original views.py; otherwise we use the unicode version.
def article(request, article):
    try:
        article.decode('utf8');
        return article_a(request, article);
    except UnicodeEncodeError:
        return article_w(request, article);

# the unicode version of article function
def article_w(request, article):
    if article.endswith("/"):
	article = article[:-1]
    result = "Not found"
    print "Getting for exact article:", article
#    print article
    #print "./quickstartsearch ../db/ \"%s\"" % article.lower().replace('_', ' ')
# use subprocess.Popen, directing the PIPE to stdin
# the output is a unicode stream, so we obtain the stream as a string, spliting it with the newline character. I don't know why it is '\n' instead of u'\n'. I am totally ignorant of Python...
#    for line in os.popen(u"./quickstartsearch ../db/ \"%s\"" % article.lower().replace('_', ' ')):
    for line in subprocess.Popen(args="./quickstartsearch ../db/ \"%s\"" % article.lower().replace('_', ' '), shell=True, stdout=PIPE).communicate()[0].split('\n'):
        line = line + '\n'; # append a newline character
	res = re.match(u'^([\d%]+)\s\[(rec[^:]+):(.+?)\]$', line) # this gives a res object
        # res.group(3)'s type is str (byte array), so there will be some problem in comparing res.group(3) with article.replace('_', ' ') (the latter is unicode). Encode article... as utf8 before comparing
	if res != None:
	    print res.group(3)
	else:
            print "article_w for line in...",line
	    print "none"
	if res != None and res.group(3) == article.replace('_', ' ').encode('utf8'):
	    cmd = "./show.pl \"../wiki-splits/%s\" \"%s\"  | php ../mediawiki_sa/wikiparser.php - | ./addSearchbox.pl \"%s\"" % (res.group(2), res.group(3), res.group(3))
	    text=""
            for aline in subprocess.Popen(args=cmd, shell=True, stdout=PIPE).communicate()[0].split('\n'):
	        text = text + aline
	    result = text 
	    break
        else:
            return search(request, article)
    return HttpResponse(result)

# the ASCII version of article function
def article_a(request, article):
    if article.endswith("/"):
	article = article[:-1]
    result = "Not found"
    print "Getting for exact article:", article
    #print "./quickstartsearch ../db/ \"%s\"" % article.lower().replace('_', ' ')
    for line in os.popen("./quickstartsearch ../db/ \"%s\"" % article.lower().replace('_', ' ')):
	print line,
	res = re.match(r'^([\d%]+)\s\[(rec[^:]+):(.+?)\]$', line)
	if res != None and res.group(3) == article.replace('_', ' '):
	    cmd = "./show.pl \"../wiki-splits/%s\" \"%s\"  | php ../mediawiki_sa/wikiparser.php - | ./addSearchbox.pl \"%s\"" % (res.group(2), res.group(3), res.group(3))
	    text=""
            for aline in subprocess.Popen(args=cmd, shell=True, stdout=PIPE).communicate()[0].split('\n'):
	        text = text + aline
	    result = text 
	    break
    else:
	return search(request, article)
    return HttpResponse(result)

def search(request, article):
    print "Searching for article:", article
    lines = []
    #print u"./quickstartsearch ../db/ \"%s\"" % article.lower().replace('_', ' ')
    # same treat
    for line in subprocess.Popen(args="./quickstartsearch ../db/ \"%s\"" % article.lower().replace('_', ' '), shell=True, stdout=PIPE).communicate()[0].split('\n'):
#    for line in os.popen("./quickstartsearch ../db/ \"%s\"" % article.lower().replace('_', ' ').encode('utf8')):
        line = line+'\n';
	print line,
	lines.append(line[:])
    #if len(lines) == 0:
    if ( len(lines) == 0 or lines[0].strip('\r\n ') == '' ) :
	result = '<html><head><title>Wikipedia has nothing about this.</title>'
	result += '</head><body>Wikipedia has nothing about: %s . You can try other keywords. <br/>' % article
	#result += 'You can keyword search about it  <a href="/keyword/%s">here</a>' % article
	result += searchbox()
	result += '</body></html>'
    else:
	result = "<html><head><title>Choose one</title></head><body><h1>Choose one of the options below</h1>\n" + lines[0]
	for line in lines:
	    res = re.match(r'^([\d%]+)\s\[(rec[^:]+):(.+?)\]$', line)
	    if res != None:
		result += "(%s) <A HREF=\"/article/%s\">%s</A><br/>\n" % (res.group(1), res.group(3), res.group(3))
	result += "</body></html>"
    return HttpResponse(result)

def searchbox():
    searchbox="""
    <script type="text/javascript">
    function DoSearch(form)
    {
    top.location='/searchbar/?data='+form.data.value;
    }
    </script>
    <form name="SearchForm" onSubmit="DoSearch(this.form)" method="get" action="/searchbar">
    Search for
    <input type="text" name="data" size="50">
    <input type="button" value="Submit" onclick="DoSearch(this.form)">
    <br>
    <hr>
    </form>
    """
    return searchbox

def keyword(request, article):
    print "Searching for keywords of article:", article
    lines = []
    cmd = "./quickstartsearch ../db/ "
    for i in article.lower().replace('_', ' ').split():
	cmd += u'"%s" ' % i
    #print cmd
#    for line in os.popen(cmd.encode('utf-8')):
    # same treat
    for line in subprocess.Popen(args=cmd, shell=True, stdout=PIPE).communicate()[0].split('\n'):
        line = line+'\n';    
	print line,
	lines.append(line[:])
    if ( len(lines) == 0 or lines[0].startswith('usage:') or lines[0].strip('\r\n ') == '' )  :
	result = '<html><head><title>No exact match for this article name found in Wikipedia (try a keyword search).</title>'
	result += '<body>' + searchbox()
	result += 'no content for:' + article + ' </body></html>'
    else:
	result = "<html><head><title>Choose one</title></head><body><h1>Choose one of the options below</h1>\n"
	for line in lines:
	    res = re.match(r'^([\d%]+)\s\[(rec[^:]+):(.+?)\]$', line)
	    if res != None:
		result += "(%s) <A HREF=\"/article/%s/\">%s</A><br/>\n" % (res.group(1), urllib.quote(res.group(3)), res.group(3))
	result += "</body></html>"
    return HttpResponse(result)

def searchbar(request):
    searchData = request.GET['data']
    return keyword(request, searchData)
