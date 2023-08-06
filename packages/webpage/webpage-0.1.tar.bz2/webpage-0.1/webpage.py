import urllib
import urllib2
import gzip

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

class NotFoundError(Exception):
    pass

class RedirectHandler(urllib2.HTTPRedirectHandler):

    def http_error_301(self, req, fp, code, msg, headers):
        result = urllib2.HTTPRedirectHandler.http_error_301(self, req, fp, code, msg, headers)
        result.status = code
        return result

    def http_error_302(self, req, fp, code, msg, headers):
        result = urllib2.HTTPRedirectHandler.http_error_302(self, req, fp, code, msg, headers)
        result.status = code
        return result

class ErrorHandler(urllib2.HTTPDefaultErrorHandler):

    def http_error_default(self, req, fp, code, msg, headers):
        result = urllib2.HTTPError(req.get_full_url(), code, msg, headers, fp)
        result.status = code
        return result

user_agent = 'Python Webpage/0.1 +http://amikrop.gr/webpage.php'

class Webpage(object):

    def __init__(self, url, agent=user_agent):
        self.url = url
        self.agent = agent
        self.last_modified = None
        self.etag = None
        self._refresh()

    def _refresh(self):
        self.permanent = True
        self.get_data = None
        self.post_data = None

    def _fetch(self, url):
        if self.get_data is not None:
            url = '%s?%s' % (url, urllib.urlencode(self.get_data))
        request = urllib2.Request(url, urllib.urlencode(self.post_data))
        request.add_header('User-Agent', self.agent)
        request.add_header('Accept-Encoding', 'gzip')
        if self.last_modified is not None:
            request.add_header('If-Modified-Since', self.last_modified)
        if self.etag is not None:
            request.add_header('If-None-Match', self.etag)

        opener = urllib2.build_opener(RedirectHandler(), ErrorHandler())
        response = opener.open(request)

        if hasattr(response, 'status'):
            if response.status == 301:
                if self.permanent:
                    self.url = response.url
                return self._fetch(response.url)
            if response.status == 302:
                self.permanent = False
                return self._fetch(response.url)
            if response.status == 304:
                return self.data
            if response.status == 404:
                raise NotFoundError, '404 Not Found: %s' % url

        self.data = response.read()

        if hasattr(response, 'headers'):
            self.last_modified = response.headers.get('Last-Modified')
            self.etag = response.headers.get('ETag')
            if response.headers.get('content-encoding', '') == 'gzip':
                self.data = gzip.GzipFile(fileobj=StringIO(self.data)).read()

        return self.data

    def get(self, **data):
        self.get_data = data

    def post(self, **data):
        self.post_data = data

    def download(self):
        result = self._fetch(self.url)
        self._refresh()
        return result

if __name__ == '__main__':
    import sys

    try:
        url = sys.argv[1]
    except IndexError:
        url = 'http://www.python.org/'

    page = Webpage(url)
    html = page.download()

    local_file = open('page.html', 'w')
    local_file.write(html)
    local_file.close()
