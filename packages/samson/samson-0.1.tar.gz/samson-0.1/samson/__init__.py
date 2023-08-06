# samson - curl helpers.
#
#       http://github.com/davidreynolds/samson
#
# Copyright 2009 David Reynolds
#
# Use and distribution licensed under the MIT license. See
# the LICENSE file for full text.

import pycurl
from StringIO import StringIO

from exceptions import *

def curl_init():
    curl = pycurl.Curl()
    curl.setopt(pycurl.USERAGENT,
                "Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.18) Gecko/2010021501 Ubuntu/9.04 (jaunty) Firefox/3.0.18")

    curl.setopt(pycurl.HTTPHEADER, [
        "Accept-Language: en-us,en;q=0.5",
        "Accept-Charset: ISO-8859-1,utf-8;q=0.7,*;q=0.7",
        "Accept: text/xml,application/xml,application/xhtml+xml,text/html;q=0.9,text/plain;q=0.8,image/png,*/*;q=0.5"
    ])

    curl.setopt(pycurl.FOLLOWLOCATION, 1)
    curl.setopt(pycurl.MAXREDIRS, 10)

    curl.setopt(pycurl.COOKIEFILE, 'cookies.txt')
    curl.setopt(pycurl.COOKIEJAR, 'cookies.txt')

    curl.setopt(pycurl.SSL_VERIFYPEER, 0)
    curl.setopt(pycurl.SSL_VERIFYHOST, 0)

    return curl

class Samson:
    def __init__(self, url=None):
        self.postfields = []
        self.response = None
        self.url = url

        self.curl = curl_init()

    def set_cookie_file(self, filename):
        self.curl.setopt(pycurl.COOKIEFILE, str(filename))
        self.curl.setopt(pycurl.COOKIEJAR, str(filename))

    def add_postfield(self, k, v):
        self.postfields.append((k, v))

    def get(self, url=None):
        if url:
            self.url = url

        if self.url is None:
            raise SamsonError('self.url is None')


        self.curl.setopt(pycurl.URL, self.url)

        # reset POST-only stuff because I reuse self.curl across multiple requests
        self.postfields = []
        self.curl.setopt(pycurl.POST, 0)

        self.response = StringIO()
        self.curl.setopt(pycurl.WRITEFUNCTION, self.response.write)
        self.curl.perform()

    def httppost(self, url=None):
        if url:
            self.url = url

        if self.url is None:
            raise SamsonError('self.url is None')

        self.curl.setopt(pycurl.URL, self.url)

        if len(self.postfields) == 0:
            raise SamsonError('self.postfields is empty')

        self.response = StringIO()
        self.curl.setopt(pycurl.WRITEFUNCTION, self.response.write)
        self.curl.setopt(pycurl.HTTPPOST, self.postfields)
        self.curl.perform()
        self.postfields = []

    def _setup_post(self, query_string):
        if self.url is None:
            raise SamsonError('self.url is None')

        self.curl.setopt(pycurl.URL, str(self.url))
        if query_string == '':
            raise SamsonError('query_string is empty')

        self.response = StringIO()
        self.curl.setopt(pycurl.WRITEFUNCTION, self.response.write)
        self.curl.setopt(pycurl.POSTFIELDS, query_string)

    def post(self, query_string):
        self._setup_post(query_string)
        self.curl.setopt(pycurl.POST, 1)
        self.curl.perform()

    def put(self, query_string):
        self._setup_post(query_string)
        self.curl.setopt(pycurl.CUSTOMREQUEST, 'PUT')
        self.curl.perform()

    def perform(self):
        if self.url is None:
            raise SamsonError('self.url is None')

        if len(self.postfields) == 0:
            self.get()
        else:
            self.httppost()
