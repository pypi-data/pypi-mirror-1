# The client code below is based off code from Vaibhav Bhatia's 
# 'xmlrpc server/client which does cookie handling and supports basic
# authentication' The original document can be found here:
# http://code.activestate.com/recipes/501148/
import os
import base64
import urllib
from xmlrpclib import ProtocolError, SafeTransport, Transport, _Method, dumps

from httplib2 import Http

class ServerProxy(object):
    """ Straight copy of xmlrpclib.ServerProxy. """
    def __init__(self, uri, transport=None, encoding=None, verbose=0, allow_none=0):
        # get the url
        import urllib
        type, uri = urllib.splittype(uri)
        if type not in ("http", "https"):
            raise IOError, "unsupported XML-RPC protocol"
        self.__host, self.__handler = urllib.splithost(uri)
        if not self.__handler:
            # THIS LINE HAS BEEN CHANGED
            # We do not want "/RPC2" as the implicit default!
            self.__handler = "/"

        if transport is None:
            if type == "https":
                transport = SafeTransport()
            else:
                transport = Transport()
        self.__transport = transport

        self.__encoding = encoding
        self.__verbose = verbose
        self.__allow_none = allow_none

    def __request(self, methodname, params):
        # call a method on the remote server

        request = dumps(params, methodname, encoding=self.__encoding,
                        allow_none=self.__allow_none)

        response = self.__transport.request(
            self.__host,
            self.__handler,
            request,
            verbose=self.__verbose
            )

        if len(response) == 1:
            response = response[0]

        return response

    def __repr__(self):
        return (
            "<ServerProxy for %s%s>" %
            (self.__host, self.__handler)
            )

    __str__ = __repr__

    def __getattr__(self, name):
        # magic method dispatcher
        return _Method(self.__request, name)


class CookieAuthXMLRPCTransport(Transport):
    """ xmlrpclib.Transport that sends basic HTTP Authentication"""

    user_agent = '*py*'
    credentials = ()
    cookie = ''

    def __init__(self, uri, creds=()):
        type_, uri = urllib.splittype(uri)
        host, handler = urllib.splithost(uri)
        self.type = type_
        self.host = host
        self.handler = handler
        if type(creds) != tuple:
            raise TypeError
        else:
            self.credentials = creds

    # def send_basic_auth(self, connection):
    #     """Include HTTP Basic Authentication data in a header"""
    #     
    #     auth = base64.encodestring("%s:%s"%self.credentials).strip()
    #     auth = 'Basic %s' %(auth,)
    #     connection.putheader('Authorization',auth)

    def plone_login(self, host):
        location = self.type + '://' + self.host + self.handler
        url = location + '/login_form'
        headers =  {"User-agent" : "Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)",
                    "Content-type": "application/x-www-form-urlencoded",
                    "Accept": "text/plain"}
        params = {'came_from': location,
                  'form.submitted': '1',
                  'js_enabled': '0',
                  'cookies_enabled': '',
                  'login_name': '',
                  'pwd_empty': '0',
                  '__ac_name': self.credentials[0],
                  '__ac_password': self.credentials[1],
                  'submit': 'Log in'}
        http = Http()
        resp, content = http.request(url, "POST", body=urllib.urlencode(params), headers=headers)
        self.cookie = resp['set-cookie']
        # print "CRUNCH!!!  NOM NOM, sweet goodness, NOM NOM =D.."

    def send_cookie_auth(self, connection):
        """Include Cookie Authentication data in a header"""
        connection.putheader('Cookie', self.cookie)

    ## override the send_host hook to also send authentication info
    def send_host(self, connection, host):
        Transport.send_host(self, connection, host)
        if self.credentials and self.cookie:
            self.send_cookie_auth(connection)

    def request(self, host, handler, request_body, verbose=0):
        # get the plone cookie credentials
        if self.credentials and not self.cookie:
            self.plone_login(host)

        # issue XML-RPC request
        h = self.make_connection(host)
        if verbose:
            h.set_debuglevel(1)

        self.send_request(h, handler, request_body)
        self.send_host(h, host)
        self.send_user_agent(h)

        self.send_content(h, request_body)

        errcode, errmsg, headers = h.getreply()

        if errcode != 200:
            raise ProtocolError(
                host + handler,
                errcode, errmsg,
                headers
                )

        self.verbose = verbose

        try:
            sock = h._conn.sock
        except AttributeError:
            sock = None
                
        return self._parse_response(h.getfile(), sock)


# To be phased out...
def getXmlrpcClient(uri, site=None, auth=(), **kwargs):
    """ this will return an xmlrpc client which supports
    basic authentication/authentication through cookies 
    """
    return getClient(uri, auth, **kwargs)

# Use this...
def getClient(uri, creds=(), **kwargs):
    """This will return an xmlrpc client which supports Plone's cookie
    based authentication.
    """
    trans = CookieAuthXMLRPCTransport(uri, creds)
    if creds != ():
        trans.credentials = creds
    client = ServerProxy(uri, transport=trans, **kwargs)
    return client
