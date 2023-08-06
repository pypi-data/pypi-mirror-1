import sys
import urllib
import urllib2
from html2text import html2text
import cookielib
import re

# Cookie Handling Setup
urlopen = urllib2.urlopen
Request = urllib2.Request
cj = cookielib.LWPCookieJar()
opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
urllib2.install_opener(opener)

# Email regex
email_pattern = re.compile("[-a-zA-Z0-9._]+@[-a-zA-Z0-9_]+\.[a-zA-Z0-9_.]+")

# file to put email addresses in
file = open('found_emails.txt', 'w')

# the admin URL & password of the Mailman web interface
# ex: http://example.com/mailman/admin/mylist_example.com/
target = ''
password = ''

urls_parsed = {}
all_emails = []

def main():
    try:
        values = {'adminpw' : password}
        post_data = urllib.urlencode(values)
        req = Request(target, post_data)
        response = urlopen(req)
        the_page = response.read()
        
        top_of_page = html2text(the_page)[0:75]
        if "Authorization failed" in top_of_page:
            die("Incorrect Password")
        if "General Options Section" not in top_of_page:
            die('expected general options page, got %s' % top_of_page)
            
        # Get the members list page
        url = target + 'members/list'
        req = Request(url)
        response = urlopen(req)
        the_page = response.read()
        top_of_page = html2text(the_page)[0:85]
        if "Membership Management... Section" not in top_of_page:
            die('expected membership management page, got %s' % top_of_page)
        
        # total member number
        match = re.search(r'(\d+) members total', the_page)
        if match:
            total_members = match.group(1)
            print "Total Members: %s" % total_members
        else:
            die('Could not find member total')
        
        # parse out the URLs
        url_pattern = re.escape(target) + r'members\?letter=(.)'
        list_pages = distinct_list(re.findall(url_pattern, the_page))
        if list_pages:
            print "Member List Pages: %s" % len(list_pages)
            count = 0
            for page_letter in list_pages:
                list_url = target + 'members?letter=' + page_letter
                print "Processing: '%s'" % page_letter
                parse_emails_from_page(list_url)
                count += 1
                #if count == 4:
                #    break
        else:
            # not enough members for multiple pages
            pass
        
        # stats
        unique_emails = set(all_emails)
        print "Emails found: %s" % len(unique_emails)
        # write emails to file
        file.write('\n'.join(unique_emails))
    finally:
        file.close()
    

def parse_emails_from_page(url):
    if urls_parsed.has_key(url):
        return
    urls_parsed[url] = True
    
    req = Request(url)
    response = urlopen(req)
    the_page = response.read()
    top_of_page = html2text(the_page)[0:85]
    if "Membership Management... Section" not in top_of_page:
        die('expected membership management page, got %s' % top_of_page)
    found_emails = re.findall(email_pattern, the_page)
    # total member number
    match = re.search(r'members total, (\d+) shown', the_page)
    print "Expected/Found: %s / %s" % (match.group(1), len(found_emails)-1)
    all_emails.extend(found_emails)
    
    # now look for more "chunk" pages
    url_pattern = re.escape(url) + '&chunk=(\d+)'
    chunks = distinct_list(re.findall(url_pattern, the_page))
    if chunks:
        for chunk in chunks:
            if chunk != '0':
                chunk_url = url + '&chunk=' + chunk
                print "Processing Chunk: '%s'" % chunk
                parse_emails_from_page(chunk_url)

def die(msg):
    print "Error: " + msg
    sys.exit()

def distinct_list(l):
    return list(set(l))