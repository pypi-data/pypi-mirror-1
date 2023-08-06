import unittest
from urllib import urlencode

from samson import Samson

class SamsonTestCase(unittest.TestCase):
    """
    TODO: Test PUT, test automating a form (scraping, parsing, POSTing)
    """

    def setUp(self):
        self.sam = Samson()

    def test_get(self):
        self.sam.url = "http://hroch486.icpf.cas.cz/formpost.html"
        self.sam.get()
        headers = self.sam.response_headers.split('\r\n')
        assert "HTTP/1.1 200 OK" == headers[0]

    def test_post(self):
        self.sam.url = "http://hroch486.icpf.cas.cz/cgi-bin/echo.pl"
        args = urlencode({
            'fruit': 'Apricot',
            'your_name': 'Samson'
        })

        self.sam.post(args)
        headers = self.sam.response_headers.split('\r\n')
        assert "HTTP/1.1 200 OK" == headers[0]
