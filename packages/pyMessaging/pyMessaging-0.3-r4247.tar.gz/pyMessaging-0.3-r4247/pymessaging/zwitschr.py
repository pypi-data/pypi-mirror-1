#!/usr/local/bin/python
# -*- coding: utf-8 -*-

"Reads a mail from stdin and deliver it via twitter."

__revision__ = "$Revision: $"

from pkg_resources import require
require("huTools")

import re
import time
import unittest
import urllib
from urllib2 import build_opener, install_opener, urlopen
from urllib2 import Request, HTTPBasicAuthHandler, HTTPPasswordMgrWithDefaultRealm


# next functions are based on http://snipplr.com/view/7604/python-make-url-address-to-tinyurl/


def _tiny_url(url):
    """Does a API call to tinyurl.com to get a shortened URL."""
    
    apiurl = "http://tinyurl.com/api-create.php?url="
    tinyurl = urllib.urlopen(apiurl + url).read()
    return tinyurl
    

def _content_tiny_url(content):
    """Converts all URLS in content to TinyURLs."""
    
    regex_url = r'http:\/\/([\w.]+\/?)\S*'
    for match in re.finditer(regex_url, content):
        url = match.group(0)
        content = content.replace(url, _tiny_url(url))
    return content
    

def shorten(text, maxlen=140):
    """Shortens a text to be less than <maxlen>."""
    
    text = _content_tiny_url(text)
    textsegments = text.split()
    output = []
    while textsegments and (len(' '.join(output + [textsegments[0]])) <= maxlen):
        output.append(textsegments.pop(0))
    if output:
        return (' '.join(output))[:maxlen]
    return text[:maxlen]
    

# the next code is from twitvn
_name = 'zwitscherer'


class _TwitHTTP:
    "This class twitters @ twitter (or zwitschr)"
    __username = None
    __password = None
    
    def __init__(self, username, password):
        self.__username = username
        self.__password = password
    
    def send_twitter(self, message):
        """Actually sends a message to Twitter/zwitschr"""
        req = Request('http://zwitschr.hudora.biz/api/statuses/update.json')
        twit_auth = HTTPPasswordMgrWithDefaultRealm()
        twit_auth.add_password(None, 'zwitschr.hudora.biz', self.__username, self.__password)
        # install the auth handler built from the HTTPPasswordMgrWithDefaultRealm password manager
        install_opener(build_opener(HTTPBasicAuthHandler(twit_auth)))
        data = urllib.urlencode({'status': message, 'source': _name})
        try:
            urlopen(req, data)
        except IOError, msg:
            print 'We got an error'
            print msg.code
    

def zwitscher(text, username='zwitscherer', password=None):
    """Sends a message to our zwitschr server."""
    
    if not password:
        password = username
    _TwitHTTP(username, password).send_twitter(shorten(text))
    

_dupedict = {}


def zwitscher_nodupes(text, username='zwitscherer', password=None):
    """Sends a message to our zwitschr server without sending the same message twice within 3 hours."""

    if not password:
        password = username
    if "%s %s" % (username, text) in _dupedict:
        return
    _TwitHTTP(username, password).send_twitter(shorten(text))
    _dupedict["%s %s" % (username, text)] = int(time.time())
    
    # clean dupedict
    maxtime = int(time.time()) - 60*60*3 # 3h
    for key, timestamp in _dupedict.items():
        if timestamp < maxtime:
            del _dupedict[key]
        

class SomeTests(unittest.TestCase):
    """Some minimal testing functionality."""
    
    def test_shorten(self):
        """Test if String shortening actually works."""
        self.assertEqual('abc def', shorten('abc def ghi jkl mno pq', 10))
        self.assertEqual('abcdefghij', shorten('abcdefghijklmnopq', 10))
        self.assertEqual('a', shorten('abc def ghi jkl', 1))
        self.assertEqual('abc def ghi', shorten('abc def ghi jkl', 12))
        self.assertEqual('abc def ghi', shorten('abc def ghi jkl', 14))
        self.assertEqual('abc def ghi jkl', shorten('abc def ghi jkl', 15))
        self.assertEqual('abc def ghi jkl', shorten('abc def ghi jkl', 16))
        self.assertEqual('http://tinyurl.com/5ft3ph <-',
                         shorten('http://www.example.com/longurlthingohohohohoh/ <- link', 31))
        self.assertEqual('http://tinyurl.com/5ft3ph <-',
                         shorten('http://www.example.com/longurlthingohohohohoh/ <- link', 32))
        self.assertEqual('http://tinyurl.com/5ft3ph <- link',
                         shorten('http://www.example.com/longurlthingohohohohoh/ <- link', 33))
        self.assertEqual('http://tinyurl.com/5ft3ph <- link',
                         shorten('http://www.example.com/longurlthingohohohohoh/ <- link', 34))
        
    
if __name__ == '__main__':
    unittest.main()
