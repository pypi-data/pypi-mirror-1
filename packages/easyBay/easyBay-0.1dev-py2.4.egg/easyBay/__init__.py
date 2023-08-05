# This module is under development.
# For documentation see: http://exogen.case.edu/easyBay/
# Find a sample ebay.ini in the trunk: svn://exogen.case.edu/easyBay/trunk

import httplib, ConfigParser, urlparse
from elementtree.ElementTree import ElementTree, Element, SubElement, fromstring, tostring, parse

_DEBUG = False

class eBay(object):
    _callDefaults = {} # 'DetailLevel': 0, 'ErrorLevel': 1, 'SiteId': 0, 'Version': 433 }
    _sellerLink = "http://feedback.ebay.com/ws/eBayISAPI.dll?ViewFeedBack&amp;userid=%s"
    _itemLink = "http://cgi1.ebay.com/aw-cgi/eBayISAPI.dll?ViewItemWithCategory&item=%s"
    _fixedListings = ('AdType', 'StoresFixedPrice', 'FixedPriceItem')

    class eBayError(Exception):
        def __init__(self, node, response):
            self.Response = response
            self.ErrorCode = node.ErrorCode and int(node.ErrorCode)
            self.SeverityCode = node.SeverityCode
            self.ShortMessage = node.ShortMessage
            self.LongMessage = node.LongMessage
            self.ErrorParameters = node.ErrorParameters
            self.ErrorClassification = node.ErrorClassification
            self.UserDisplayHint = node.UserDisplayHint

        def __str__(self):
            return repr(self)

        def __repr__(self):
            return "(%s) %s: %s" % (str(self.ErrorCode),
                                    str(self.SeverityCode),
                                    str(self.LongMessage))

    class RequestError(eBayError):
        pass

    class SystemError(eBayError):
        pass

    def __init__(self, dev=None, app=None, cert=None, token=None,
                 url="http://api.ebay.com/ws/api.dll", config=None):
        if config:
            self._fromConfig(config)
        else:
            self._init(dev, app, cert, token, url)

    def _init(self, dev, app, cert, token, url):
        self._dev = dev
        self._app = app
        self._cert = cert
        self._url = url
        self._token = token

    def _token():
        doc = "Session token"
        def get(self):
            return self.__token
        def set(self, value):
            self._callDefaults['RequesterCredentials.eBayAuthToken'] = value
            self.__token = value
        return get, set, None, doc
    _token = property(*_token())

    def _url():
        doc = "Remote API address"
        def get(self):
            return self.__url
        def set(self, value):
            self._server, self._command =  urlparse.urlparse(value)[1:3]
            self.__url = value
        return get, set, None, doc
    _url = property(*_url())

    def _fromConfig(self, filename):
        config = ConfigParser.ConfigParser()
        config.read(filename)
        dev = config.get("Developer Keys", "Developer")
        app = config.get("Developer Keys", "Application")
        cert = config.get("Developer Keys", "Certificate")
        token = config.get("Authentication", "Token")
        url = config.get("Server", "URL")
        self._init(dev, app, cert, token, url)

    def __getattr__(self, attr):
        return self._call(attr)

    def __repr__(self):
        return "<API.eBay dev=%r, app=%r, cert=%r, token=%r, server=%r>" % \
               (self._dev, self._app, self._cert,
                str(self._token)[:15] + (str(self._token)[15:] and "..."),
                self._server)

    def _fillDefaults(self, req, explicit):
        for arg, default in self._callDefaults.iteritems():
            if arg not in explicit:
                req.append(self._makeElement(arg, str(default)))

    @staticmethod
    def _makeElement(name, value):
        parts = name.split(".")
        parent = Element(parts[0])
        e = parent
        for part in parts[1:]:
            e = SubElement(e, part)
        e.text = str(value)
        return parent

    def _call(self, verb):
        def _request(*args, **kwargs):
            req = Element(verb + "Request",
                          xmlns="urn:ebay:apis:eBLBaseComponents")

            for k, v in kwargs.iteritems():
                req.append(self._makeElement(k, v))

            self._fillDefaults(req, kwargs)
            reqString = """<?xml version="1.0" encoding="utf-8"?>"""
            reqString += tostring(req)

            if _DEBUG:
                print reqString

            conn = httplib.HTTPSConnection(self._server)
            conn.request("POST", self._command, reqString,
                         self._headers(verb, kwargs))
            response = conn.getresponse()

            node = Node(parse(response).getroot())

            #if _DEBUG:
                #print data

            conn.close()
            #root = fromstring(data)
            #node = Node(root)

            for error in node.Errors:
                try:
                    if error.ErrorClassification == 'RequestError':
                        raise self.RequestError(error, node)
                    elif error.ErrorClassification == 'SystemError':
                        raise self.SystemError(error, node)
                    else:
                        raise self.eBayError(error, node)
                except self.eBayError, e:
                    if e.SeverityCode == 'Warning':
                        print "\n", e, "\n"
                    else:
                        raise

            return node
        return _request

    def _headers(self, verb, kwargs):
        return { "X-EBAY-API-COMPATIBILITY-LEVEL": str(self._default('Version', self._callDefaults, 435)),
                 "X-EBAY-API-SESSION-CERTIFICATE": "%s;%s;%s" % (self._dev, self._app, self._cert),  
                 "X-EBAY-API-DEV-NAME": self._dev,
                 "X-EBAY-API-APP-NAME": self._app,
                 "X-EBAY-API-CERT-NAME": self._cert,
                 "X-EBAY-API-CALL-NAME": verb,
                 "X-EBAY-API-SITEID": str(self._default('SiteId', kwargs, self._callDefaults, 0)),
                 "Content-Type": "text/xml" }

    @staticmethod
    def _default(key, *args):
        for arg in args:
            try:
                value = arg.get(key, None)
            except AttributeError:
                return arg
            if value is None:
                continue
            else:
                return value

    def _newSession(self):
        pass

class TextNode(unicode):
    def __init__(self, value):
        super(TextNode, self).__init__(value)

    def __iter__(self):
        return iter([self])

    def __getitem__(self, item):
        if isinstance(item, int):
            return super(TextNode, self).__getitem__(item)
        return self._attrib.get(item, None)

    def __getattr__(self, attr):
        return Node()

    def _setAttrs(self, attrib):
        self._attrib = attrib

    @classmethod
    def makeNode(cls, elem):
        if elem.text is None:
            text = ""
        else:
            text = elem.text
        t = cls(text)
        t._setAttrs(elem.attrib)
        t._elem = elem
        ns = elem.tag.find("}") + 1
        t._ns, t._tag = elem.tag[:ns], elem.tag[ns:]
        return t

    def _repr(self, pre=""):
        return "%s.%s:%r" % (pre, self._tag, self)

class Node(object):
    """Node allows you to refer to XML elements just like what you see on
    the eBay documentation. Initialize it with an ElementTree Element.

    Example:

    <CallResponse>
      <Item>
        <ItemID>12345</ItemID>
        <Images>
          <Image>pic1.jpg</Image>
          <Image>pic2.jpg</Image>
        </Images>
      </Item>
    </CallResponse>

    After creating an ElementTree using the above XML, use it like this:

    response = Node(elem)
    print response.Item.ItemID
    for image in response.Item.Images.Image:
        print image

    Output:

    12345
    pic1.jpg
    pic2.jpg
    """
    def __init__(self, elem=None):
        self._elem = elem
        if elem:
            ns = elem.tag.find("}") + 1
            self._ns, self._tag = elem.tag[:ns], elem.tag[ns:]
        else:
            self._ns = self._tag = None
        self._iter = None

    @classmethod
    def safeCreate(cls, elem):
        try:
            if elem.getchildren():
                return cls(elem)
        except AttributeError:
            pass
        return TextNode.makeNode(elem)

    def __getattr__(self, attr):
        if self._elem is None:
            return self

        elems = self._elem.findall(self._ns + attr)
        value = None
        for elem in elems:
            if value is not None:
                break
            value = Node(elem)
        else:
            if value is None:
                value = Node(None)
            elif not value._elem.getchildren():
                value = TextNode.makeNode(elem)
            return value
        self._iter = (Node.safeCreate(elem) for elem in self._elem.findall(self._ns + attr))
        value = iter(self)
        return value

    def __len__(self):
        if self._iter:
            return len(list(self._iter))
        return 0

    def __iter__(self):
        #return self
        if self._elem is not None:
            if self._iter:
                return iter(self._iter)
            else: 
                return iter([self])
        return iter([])

    #def next(self):
        #if self._elem is not None:
            #if self._iter:
                #return self._iter.next()
            #return self
        #raise StopIteration

    def __nonzero__(self):
        return self._elem is not None

    def __getitem__(self, key):
        if isinstance(key, basestring):
            if self._elem is not None:
                return self._elem.get(key)
        else:
            return list(self._iter)[key]

    def __contains__(self, key):
        if self._elem is not None:
            return key in self._elem.keys()
        return False

    def __repr__(self):
        return self._repr("")

    def _repr(self, pre=""):
        if pre:
            pre = pre + "."
        if not self:
            return repr(None)
        return "\n".join([Node.safeCreate(e)._repr(pre + self._tag) \
                          for e in self._elem.getchildren()])

    def _get(self, key, default=None):
        if self._elem is not None:
            return self._elem.get(key, default)
        return default
