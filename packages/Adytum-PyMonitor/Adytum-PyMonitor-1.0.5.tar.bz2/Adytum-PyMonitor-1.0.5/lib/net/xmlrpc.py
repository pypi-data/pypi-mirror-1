import string, xmlrpclib, httplib
from base64 import encodestring

class BasicAuthTransport(xmlrpclib.Transport):
    """ taken from http://www.zope.org/Members/Amos/XML-RPC """
    def __init__(self, username=None, password=None, verbose=0):
        self.username=username
        self.password=password
        self.verbose=verbose

    def request(self, host, handler, request_body, verbose=0):
        h = httplib.HTTP(host)
        h.putrequest("POST", handler)
        h.putheader("Host", host)
        h.putheader("User-Agent", self.user_agent)
        h.putheader("Content-Type", "text/xml")
        h.putheader("Content-Length", str(len(request_body)))

        # basic auth
        if self.username is not None and self.password is not None:
            h.putheader("AUTHORIZATION", "Basic %s" % string.replace(
                    encodestring("%s:%s" % (self.username, self.password)),
                    "\012", ""))
        h.endheaders()

        if request_body:
            h.send(request_body)
        errcode, errmsg, headers = h.getreply()

        if errcode != 200:
            raise xmlrpclib.ProtocolError(
                host + handler,
                errcode, errmsg,
                headers
                )

        return self.parse_response(h.getfile())
