"""
CAPTCHA middleware
"""

import os
import random
import sys
from lxml import etree
from lxmlmiddleware import LXMLMiddleware
from skimpyGimpy import skimpyAPI
from urllib2 import urlopen
from webob import Request, exc


class CAPTCHAmiddleware(LXMLMiddleware):
    """
    put CAPTCHAs on forms for unauthorized users
    """

    ### class level variables
    defaults = { 
                 'dictionary': '/usr/share/dict/words',
                 'error': '<span class="error">Please type the CAPTCHA</span>',
                 'minimum_length': 5, 
                 'path': "/input[@type='submit']",
                 }

    def __init__(self, app, **kw):
        self.app = app

        # set instance parameters from kw and defaults
        for key in self.defaults:
            setattr(self, key, kw.get(key, self.defaults[key]))
        self.minimum_length = int(self.minimum_length)
        assert os.path.exists(self.dictionary)
        
        # get dictionary
        if self.dictionary.startswith('http://') or self.dictionary.startswith('https://'):
            f = urlopen(self.dictionary)
        else:
            f = file(self.dictionary)
        
        # characters skimpygimpy doesnt know about
        forbidden_characters = set(["'"])

        self.words = [ i.strip().lower() for i in f.readlines()
                       if (len(i.strip()) > self.minimum_length)
                       and not forbidden_characters.intersection(i) ]
        random.shuffle(self.words)

    def check_captcha(self, request):
        captcha = request.POST.get('captcha', '').lower()
        key = request.POST.get('key')
        if not key: return False
        try:
            key = int(key)
        except ValueError:
            return False
        try:
            value = self.words[key]
        except IndexError:
            raise # TODO: better error handling
        return value == captcha

    def __call__(self, environ, start_response):
        request = Request(environ)
        if request.method == 'POST' and not request.remote_user:
            if not self.check_captcha(request):
                location = request.referrer
                return exc.HTTPSeeOther(location=location)(environ, start_response)
            # TODO: set a cookie to record an error
            # stage 2: record form values from request.POST,
            # and reinsert them into the form so that users
            # don't hate me ;)

        return LXMLMiddleware.__call__(self, environ, start_response)

    def manipulate(self, environ, tree):
        """manipulate the DOM; should return an etree._Element"""

        request = Request(environ)

        # don't use CAPTCHAs for authorized users
        if request.remote_user:
            return tree 

        for element in tree.findall(".//form[@method='post']"):
            key = random.Random().randint(0, len(self.words))
            word = self.words[key]
            captcha = skimpyAPI.Pre(word).data()
            string = '<div class="captcha">%s<input type="hidden" name="key" value="%s"/><input type="text" name="captcha"/></div>' % (captcha, key)
            addition = etree.fromstring(string)
            insertion_point = element.find('.' + self.path)
            insertion_point.addprevious(addition)

        return tree

