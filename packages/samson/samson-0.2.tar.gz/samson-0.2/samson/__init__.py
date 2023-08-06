# samson - curl helpers.
#
#       http://github.com/davidreynolds/samson
#
# Copyright 2009 David Reynolds
#
# Use and distribution licensed under the MIT license. See
# the LICENSE file for full text.

import pycurl
try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

from samson.exceptions import SamsonError

def curl_init(**kwargs):
    """
    Available keyword arguments:
        'useragent': string value
        'httpheader': list value
        'followlocation': boolean int (0 or 1)
        'maxredirs': int, max number of redirects
        'cookiefile': string, filename
        'cookiejar': string, filename
        'verifypeer': 0 or 1, SSL stuff
        'verifyhost': 0 or 1, SSL stuff
    """

    # default user agent
    _ua = "Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.18)"
    _ua+= " Gecko/2010021501 Ubuntu/9.04 (jaunty) Firefox/3.0.18"

    # default headers
    _accept_lang = "en-us,en;q=0.5"
    _accept_charset = "ISO-8859-1,utf-8;q=0.7,*;q=0.7"
    _accept = "text/xml,application/xml,application/xhtml+xml,"
    _accept+= "text/html;q=0.9,text/plain;q=0.8,image/png,*/*;q=0.5"

    _headers = [_accept_lang, _accept_charset, _accept]

    # some default attributes
    _follow = 1
    _redirects = 10
    _cookiefile = ''
    _cookiejar = ''
    _verifypeer = 0
    _verifyhost = 0

    curl = pycurl.Curl()
    curl.setopt(pycurl.USERAGENT, kwargs.get('useragent', _ua))

    curl.setopt(pycurl.HTTPHEADER, kwargs.get('httpheader', _headers))

    curl.setopt(pycurl.FOLLOWLOCATION, kwargs.get('followlocation', _follow))
    curl.setopt(pycurl.MAXREDIRS, kwargs.get('maxredirs', _redirects))

    curl.setopt(pycurl.COOKIEFILE, kwargs.get('cookiefile', _cookiefile))
    curl.setopt(pycurl.COOKIEJAR, kwargs.get('cookiejar', _cookiejar))

    curl.setopt(pycurl.SSL_VERIFYPEER, kwargs.get('verifypeer', _verifypeer))
    curl.setopt(pycurl.SSL_VERIFYHOST, kwargs.get('verifyhost', _verifyhost))

    return curl

class Samson:
    """
    Samson is a light wrapper around basic pycurl operations.
    A common usage would be to test an API.

    TODO: Implement DELETE request.
    """

    def __init__(self, url=None):
        self.postfields = []
        self._response = StringIO()
        self._response_headers = StringIO()
        self.url = url

        self.curl = curl_init()

    def _response_html(self):
        return self._response.getvalue()
    response = property(_response_html)

    def _response_headers(self):
        return self._response_headers.getvalue()
    response_headers = property(_response_headers)

    def set_cookie_file(self, filename):
        """
        Change the default cookie storage location from your application
        without having to call setopt on samson.curl itself.
        """
        self.curl.setopt(pycurl.COOKIEFILE, str(filename))
        self.curl.setopt(pycurl.COOKIEJAR, str(filename))

    def add_postfield(self, k, v):
        self.postfields.append((k, v))

    def _prepare_request(self, url=None):
        # sometimes self.url will already be set
        # - this check will just override self.url
        if url:
            self.url = url

        if self.url is None:
            raise SamsonError('self.url is None')

        self._response.truncate(0)
        self._response_headers.truncate(0)
        self.curl.setopt(pycurl.WRITEFUNCTION, self._response.write)
        self.curl.setopt(pycurl.HEADERFUNCTION, self._response_headers.write)

        # not sure why I need to cast this to a str, but sometimes
        # pycurl complains about setting an invalid value.
        # I should dig into it sometime.
        self.curl.setopt(pycurl.URL, str(self.url))

    def get(self, url=None):
        # reset POST-only stuff because I reuse self.curl across multiple requests
        self.postfields = []
        self.curl.setopt(pycurl.POST, 0)

        self._prepare_request(url)
        self.curl.perform()

    def httppost(self, url=None):
        """
        Generally you won't use this method. Stick with `post`.
        """
        self._prepare_request(url)
        self.curl.setopt(pycurl.HTTPPOST, self.postfields)
        self.curl.perform()
        self.postfields = []

    def _setup_post(self, query_string):
        self._prepare_request()
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
        """
        I'm going to be deprecating this method soon so don't rely on it.
        """
        if self.url is None:
            raise SamsonError('self.url is None')

        if len(self.postfields) == 0:
            self.get()
        else:
            self.httppost()
