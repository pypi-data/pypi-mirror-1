# Copyright Michael Foord 2005 & 2006
# Copyright L.C. Rees 2006
#
# WSGI interface to the Akismet API
# http://akismet.com
#
# Released subject to the BSD License
# Please see http://www.voidspace.org.uk/python/license.shtml

'''WSGI middleware implementing the Akismet Application Programmers Interface.
This is a web service for blocking SPAM comments to blogs - or other online
services. Based on akismet 0.1.3.

You will need a Wordpress API key, from http://wordpress.com/.

You should pass in the keyword argument 'agent' to the name of your program,
when you create an Akismet instance. This sets the ``user-agent`` to a useful
value. The default is:

    Python Interface by Fuzzyman | wsgiakismet.py/0.1

Whatever you pass in, will replace the *Python Interface by Fuzzyman* part.
'''

import cgi
import urllib2
import socket
from urllib import urlencode
from StringIO import StringIO

__all__ = ['__version__', 'WsgiAkismet', 'akismet']
__version__ = '0.1'
__author__ = 'L.C. Rees <lcrees@gmail.com?'
user_agent = '%s | wsgiakismet.py/%s'
DEFAULTAGENT = 'Python Interface by Fuzzyman/%s'

if hasattr(socket, 'setdefaulttimeout'):
    # Set the default timeout on sockets to 5 seconds
    socket.setdefaulttimeout(5)

def formparse(env):
    '''Extracts data from form submissions.

    @param environ Environment dictionary
    @param strict Stops on errors (default: False)
    '''
    winput = env['wsgi.input']
    # Non-destructively retrieve string
    if hasattr(winput, 'getvalue'):
        tinput = winput.getvalue()
    # Recreate wsgi.input as fallback
    else:
        tinput = winput.read()
        env['wsgi.input'] = StringIO(tinput)
    # Parse form submission
    qdict = cgi.parse(fp=StringIO(tinput), environ=env)
    # Remove invididual entries from list and store as naked string
    for key, value in qdict.iteritems():
        if len(value) == 1: qdict[key] = value[0]
    return qdict

def _handler(environ, start_response):
    '''Replace this default handler.'''
    start_response('200 OK', [('Content-type', 'text/plain')])
    return ['Comment was spam.']

def akismet(key, blog_url, **kw):
    '''Decorator for Akismet.'''
    def decorator(application):
        return WsgiAkismet(application, key, blog_url, **kw)
    return decorator


class WsgiAkismet(object):
    
    '''WSGI middleware for working with the akismet API'''

    # Central Akismet server
    baseurl = 'rest.akismet.com/1.1/'
    # Needed form values
    vals = set(['comment_type', 'comment_author', 'comment_author_email',
            'comment_author_url', 'permalink'])

    def __init__(self, application, key, blog_url, **kw):
        self.application = application
        self.key, self.blog_url = key, blog_url           
        agent = kw.get('agent', DEFAULTAGENT % __version__)
        self.user_agent = user_agent % (agent, __version__)
        # Verify key if assertions enabled     
        self.verify = kw.get('verify', False)
        # Form key for comment 
        self.comment_key = kw.get('comment', 'comment')
        # Stub handler -- change
        self.handler = kw.get('handler', _handler)        

    def __call__(self, environ, start_response):
        formdata = formparse(environ)
        # Get comment
        comment = formdata[self.comment_key]
        # Fetch any corresponding values from the form submission
        data = self._getvalues(formdata)
        # Return handler if comment is spam
        if self.iscomment(environ, comment, data):
            return self.handler(environ, start_response)
        return self.application(environ, start_response)        

    def _getvalues(self, data):
        '''Gets any form values corresponding to Akismet request.'''
        return dict((k, data[k]) for k in data if k in self.vals)

    def _build_data(self, environ, comment, data):
        '''This function builds the data structure required by ``iscomment``.
        
        It modifies the ``data`` dictionary you give it in place. (and so
        doesn't return anything)
        '''
        # Add comment
        data['comment_content'] = comment
        data['user_ip'] = environ.get('REMOTE_ADDR', '')
        data['user_agent'] = environ.get('HTTP_USER_AGENT', '')
        # Note the spelling 'referrer'. This is a required value by the
        # akismet api - however, referrer information is not always
        # supplied by the browser or server. In fact the HTTP protocol
        # forbids relying on referrer information for functionality in 
        # programs.
        data['referrer'] = environ.get('HTTP_REFERER', 'unknown')
        data.setdefault('permalink', '')
        # The `API docs <http://akismet.com/development/api/>`_ state that this
        # value can be '*blank, comment, trackback, pingback, or a made up value*
        # *like 'registration'* '.
        data.setdefault('comment_type', 'comment')
        data.setdefault('comment_author', '')
        data.setdefault('comment_author_email', '')
        data.setdefault('comment_author_url', '')
        data['SERVER_ADDR'] = environ.get('SERVER_ADDR', '')
        data['SERVER_ADMIN'] = environ.get('SERVER_ADMIN', '')
        data['SERVER_NAME'] = environ.get('SERVER_NAME', '')
        data['SERVER_PORT'] = environ.get('SERVER_PORT', '')
        data['SERVER_SIGNATURE'] = environ.get('SERVER_SIGNATURE', '')
        data['SERVER_SOFTWARE'] = environ.get('SERVER_SOFTWARE', '')
        data['HTTP_ACCEPT'] = environ.get('HTTP_ACCEPT', '')
        data['blog'] = self.blog_url

    def isvalidkey(self):
        '''This equates to the ``verify-key`` call against the akismet API.
        
        It returns ``True`` if the key is valid.
        
        The docs state that you *ought* to call this at the start of the
        transaction.'''        
        data = {'key':self.key, 'blog':self.blog_url}
        # this function *doesn't* use the key as part of the URL
        url = 'http://%sverify-key' % self.baseurl
        headers = {'User-Agent':self.user_agent}        
        req = urllib2.Request(url, urlencode(data), headers)
        try:
            if urllib2.urlopen(req).read().lower() == 'valid': return True
            return False
        # Errors pass silently
        except:
            return False        

    def iscomment(self, environ, comment, data):
        '''This is the function that checks comments.
        
        It returns ``True`` for spam and ``False`` for ham.
        
        As a minimum it requires the environ and the body of the comment.
        This is the ``comment`` argument.
        
        Akismet requires some other arguments, and allows some optional ones.
        The more information you give it, the more likely it is to be able to
        make an accurate diagnosise. You supply these values using a mapping
        object (dictionary) as the ``data`` argument.
        '''
        # Verify API key if required
        if self.verify and not self.isvalidkey(): return False
        self._build_data(environ, comment, data)
        url = '%scomment-check' % ('http://%s.%s' % (self.key, self.baseurl))
        headers = {'User-Agent':self.user_agent}
        req = urllib2.Request(url, urlencode(data), headers)
        try:
            if urllib2.urlopen(req).read().lower() == 'true': return True
            return False
        # Errors pass silently
        except:
            return True