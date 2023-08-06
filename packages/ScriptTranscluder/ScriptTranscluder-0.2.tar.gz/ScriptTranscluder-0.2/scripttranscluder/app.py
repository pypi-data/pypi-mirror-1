from webob import Request, Response
from webob import exc
from fnmatch import translate
from urlparse import urlsplit
from lxml.html import fromstring, tostring
import lxml.etree
import re
import httplib2
import cgi
import socket

# This loading function is from http://www.kryogenix.org/days/2007/09/26/shortloaded
dest_js = '''\
(function(i) {var u =navigator.userAgent;var e=/*@cc_on!@*/false; var st =
setTimeout;if(/webkit/i.test(u)){st(function(){var dr=document.readyState;
if(dr=="loaded"||dr=="complete"){i()}else{st(arguments.callee,10);}},10);}
else if((/mozilla/i.test(u)&&!/(compati)/.test(u)) || (/opera/i.test(u))){
document.addEventListener("DOMContentLoaded",i,false); } else if(e){     (
function(){var t=document.createElement('doc:rdy');try{t.doScroll('left');
i();t=null;}catch(e){st(arguments.callee,0);}})();}else{window.onload=i;}})(function () {
var _script_el = document.getElementById(%(dest)s);if (_script_el) {_script_el.innerHTML = %(body)s;}});
'''

here_js = '''\
document.write(%(body)s);
'''

no_slash_re = re.compile(r'^https?://[^/]+$', re.I)

CHARSET_RE = re.compile(r'charset=([^ "]+)', re.I)

class FetchingError(Exception):
    pass

class ScriptTranscluder(object):

    def __init__(self, same_host, allowed_urls, cache_dir=None):
        if isinstance(allowed_urls, basestring):
            raise TypeError('allowed_urls must be a sequence')
        self.same_host = same_host
        self.allowed_urls = []
        for host in allowed_urls or ():
            self.allowed_urls.append(re.compile(translate(host)))
        self.http = httplib2.Http(cache_dir)

    def __call__(self, environ, start_response):
        req = Request(environ)
        url = req.GET['url']
        if no_slash_re.search(url):
            url += '/'
        if not self.check_url(url, req.host):
            return exc.HTTPForbidden(
                "You may not access the URL %s through this service" % url)(
                environ, start_response)
        res = Response(content_type='text/javascript; charset=utf8', conditional_response=True)
        if '#' in url:
            url, fragment = url.split('#', 1)
        else:
            fragment = None
        try:
            headers, body = self.get_body(url, fragment)
        except FetchingError, e:
            body = self.format_error(e)
            headers = {}
        res.unicode_body = self.js_body(req, body)
        for name in 'etag last_modified'.split():
            if headers.get(name):
                res.headers[name] = name
        return res(environ, start_response)

    ok_content_types = ['text/html', 'text/xhtml', 'application/xhtml', 'application/xhtml+xml', 'text/plain']

    def get_body(self, url, fragment):
        try:
            headers, body = self.http.request(url)
            ## Surprised there aren't more errors to watch for here:
        except socket.error, e:
            raise FetchingError('Could not fetch url %s: %s' % (url, e))
        if headers['status'] not in ('304', '200'):
            ## FIXME: improve the error message here:
            raise FetchingError('Could not fetch url %s; server responded with error %s'
                                % (url, headers['status']))
        content_type = headers['content-type']
        match = CHARSET_RE.search(content_type)
        content_type = content_type.split(';', 1)[0].lower()
        if content_type not in self.ok_content_types:
            raise FetchingError('Bad content type in url %s: %s' % (url, content_type))
        if match:
            encoding = match.group(1)
        else:
            encoding = 'iso-8859-1'
        body = body.decode(encoding, 'ignore')
        ## FIXME: this should check content type before parsing:
        try:
            body = fromstring(body)
        except lxml.etree.ParseError, e:
            raise FetchingError('Cannot parse url %s' % url)
        body.make_links_absolute(url)
        if fragment:
            try:
                body = body.get_element_by_id(fragment)
            except KeyError:
                return exc.HTTPNotFound(
                    "No element with the id %r in %s"
                    % (fragment, url))(environ, start_response)
            body = tostring(body)
            body = strip_outer(body)
        else:
            body = body.xpath('//body')[0]
            # if there was no body tag in the snippet, then lxml sometimes adds
            # it in for us
            # we never want to have a wrapping body tag however
            if body.tag == 'body':
                body = ''.join([tostring(el) for el in body])
            else:
                body = tostring(body)

        return headers, body

    def format_error(self, exc):
        message = 'Error fetching resource: %s' % exc
        text = '<a href="#" onclick="alert(%s); return false;" style="color: red; text-decoration: none">error</a>' % (cgi.escape(js_repr(message), 1))
        return text
        
    def check_url(self, url, host):
        netloc = urlsplit(url)[1]
        if (self.same_host
            and host.split(':')[0].lower() == netloc.split(':')[0]):
            return True
        for regex in self.allowed_urls:
            if regex.search(url):
                return True
        return False
    
    def js_body(self, req, body):
        if req.GET.get('dest'):
            js = dest_js % dict(dest=js_repr(req.GET.get('dest')), body=js_repr(body))
        else:
            js = here_js % dict(body=js_repr(body))
        return js


def strip_outer(el):
    pos = el.find('>')
    el = el[pos+1:]
    pos = el.rfind('<')
    el = el[:pos]
    return el

lower_re = re.compile(r'[\x00-\x19]')

def js_repr(s):
    if not isinstance(s, unicode):
        s = unicode(s)
    s = s.replace('\\', '\\\\')
    s = s.replace('\n', '\\n')
    s = s.replace('\r', '\\r')
    s = s.replace('"', '\\"')
    s = s.replace("'", "\\'")
    s = lower_re.sub(lambda m: '\\'+oct(ord(m.group(0))), s)
    return '"%s"' % s

    
