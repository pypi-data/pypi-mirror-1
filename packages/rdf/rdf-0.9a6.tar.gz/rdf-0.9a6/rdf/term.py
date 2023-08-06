"""
This module defines the different types of terms...

"""

from urlparse import urlparse, urljoin, urldefrag
from threading import RLock
import re
import base64
import time
import datetime
import unicodedata
import logging

_logger = logging.getLogger(__name__)

# From: http://www.w3.org/TR/REC-xml/#NT-CombiningChar
#
# The character classes defined here can be derived from the Unicode
# 2.0 character database as follows:
#
# * Name start characters must have one of the categories Ll, Lu, Lo,
#   Lt, Nl.
#
# * Name characters other than Name-start characters must have one of
#   the categories Mc, Me, Mn, Lm, or Nd.
#
# * Characters in the compatibility area (i.e. with character code
#   greater than #xF900 and less than #xFFFE) are not allowed in XML
#   names.
#
# * Characters which have a font or compatibility decomposition
#   (i.e. those with a "compatibility formatting tag" in field 5 of the
#   database -- marked by field 5 beginning with a "<") are not allowed.
#
# * The following characters are treated as name-start characters rather
#   than name characters, because the property file classifies them as
#   Alphabetic: [#x02BB-#x02C1], #x0559, #x06E5, #x06E6.
#
# * Characters #x20DD-#x20E0 are excluded (in accordance with Unicode
#   2.0, section 5.14).
#
# * Character #x00B7 is classified as an extender, because the property
#   list so identifies it.
#
# * Character #x0387 is added as a name character, because #x00B7 is its
#   canonical equivalent.
#
# * Characters ':' and '_' are allowed as name-start characters.
#
# * Characters '-' and '.' are allowed as name characters.
#
_NAME_START_CATEGORIES = ["Ll", "Lu", "Lo", "Lt", "Nl"]
_NAME_CATEGORIES = _NAME_START_CATEGORIES + ["Mc", "Me", "Mn", "Lm", "Nd"]
_ALLOWED_NAME_CHARS = [u"\u00B7", u"\u0387", u"-", u".", u"_"]

def is_ncname(name):
    """
    http://www.w3.org/TR/REC-xml-names/#NT-NCName

    [4] NCName ::= (Letter | '_') (NCNameChar)* /* An XML Name, minus
        the ":" */
    [5] NCNameChar ::= Letter | Digit | '.' | '-' | '_' | CombiningChar
        | Extender
    """
    if name is None or name=='':
        return False
    first = name[0]
    if first=="_" or unicodedata.category(first) in _NAME_START_CATEGORIES:
        for i in xrange(1, len(name)):
            c = name[i]
            if not unicodedata.category(c) in _NAME_CATEGORIES:
                if c in _ALLOWED_NAME_CHARS:
                    continue
                return False
            #if in compatibility area
            #if unicodedata.decomposition(c)!='':
            #    return False

        return True
    else:
        return False

def _strToTime(v):
    return time.strptime(v, "%H:%M:%S")

def _strToDate(v):
    tstr = time.strptime(v, "%Y-%m-%d")
    return datetime.date(tstr.tm_year, tstr.tm_mon, tstr.tm_mday)

## Note: _date_parser adapeted from http://www.mnot.net/python/isodate.py
## modified to handle fractional seconds beyond tenths and to allow
## pseudo iso i.e. "2001-12-15 22:43:46" vs "2001-12-15T22:43:46"

_date_parser = re.compile(r"""^
    (?P<year>\d{4,4})
    (?:
        -
        (?P<month>\d{1,2})
        (?:
            -
            (?P<day>\d{1,2})
            (?:
                [T ]
                (?P<hour>\d{1,2})
                :
                (?P<minute>\d{1,2})
                (?:
                    :
                    (?P<second>\d{1,2})
                    (?:
                        (?P<dec_second>\.\d+)?
                    )?
                )?                   
                (?:
                    Z
                    |
                    (?:
                        (?P<tz_sign>[+-])
                        (?P<tz_hour>\d{1,2})
                        :
                        (?P<tz_min>\d{2,2})
                    )
                )?
            )?
        )?
    )?
$""", re.VERBOSE)

def _strToDateTime(s):
        """ parse a string and return a datetime object. """
        assert isinstance(s, basestring)
        r = _date_parser.search(s)
        try:
            a = r.groupdict('0')
        except:
            raise ValueError, 'invalid date string format'

        dt = datetime.datetime(int(a['year']),
                               int(a['month']) or 1,
                               int(a['day']) or 1,
                               # If not given these will default to 00:00:00.0
                               int(a['hour']),
                               int(a['minute']),
                               int(a['second']),
                               # Convert into microseconds
                               int(float(a['dec_second'])*1000000),
                               )
        tz_hours_offset = int(a['tz_hour'])
        tz_mins_offset = int(a['tz_min'])
        if a.get('tz_sign', '+') == "-":
            return dt + datetime.timedelta(hours = tz_hours_offset,
                                           minutes = tz_mins_offset)
        else:
            return dt - datetime.timedelta(hours = tz_hours_offset,
                                           minutes = tz_mins_offset)


class Term(object):
    """
    A Term...
    """
    __slots__ = ()


class Identifier(Term, unicode): 
    """
    See http://www.w3.org/2002/07/rdf-identifer-terminology/
    regarding choice of terminology.
    """

    __slots__ = ()

    def __new__(cls, value, encoding='utf-8', errors='strict'):
        """
        TODO:
        """
        if isinstance(value, str):
            return unicode.__new__(cls, value, encoding, errors)
        else:
            return unicode.__new__(cls, value)


class URIRef(Identifier):
    """
    RDF URI Reference: http://www.w3.org/TR/rdf-concepts/#section-Graph-URIref

    >>> uri = URIRef("http://example.org/foo#bar")
    >>> uri
    rdf.URIRef('http://example.org/foo#bar')

    >>> uri = URIRef("baz", base="http://example.org/")
    >>> uri.n3()
    u'<http://example.org/baz>'

    """

    __slots__ = ()

    def __new__(cls, value, base=None, encoding='utf-8', errors='strict'):
        """
        TODO:
        """
        if base is not None:
            ends_in_hash = value.endswith("#")
            value = urljoin(base, value, allow_fragments=1)
            if ends_in_hash:
                if not value.endswith("#"):
                    value += "#"
        #if normalize and value and value != normalize("NFC", value):
        #    raise Error("value must be in NFC normalized form.")
        return Identifier.__new__(cls, value, encoding, errors)

    def n3(self):
        """
        Return the URIRef in n3 notation.
        """
        return "<%s>" % self

    def concrete(self):
        """
        Return the related concrete URIRef if this is a abstract
        URIRef. Else return the already concrete URIRef.

        NOTE: This is just one pattern for mapping between related
        concrete and abstract URIRefs.
        """
        if "#" in self:
            return URIRef("/".join(self.rsplit("#", 1)))
        else:
            return self

    def abstract(self):
        """
        Return the related abstract URIRef if this is a concrete
        URIRef. Else return the already abstract URIRef.

        NOTE: This is just one pattern for mapping between related
        concrete and abstract URIRefs.
        """
        if "#" not in self:
            scheme, netloc, path, params, query, fragment = urlparse(self)
            if path:
                return URIRef("#".join(self.rsplit("/", 1)))
            else:
                if not self.endswith("#"):
                    return URIRef("%s#" % self)
                else:
                    return self
        else:
            return self


    def defrag(self):
        """
        Defragment the URIRef and return the resulting URIRef.
        """
        if "#" in self:
            url, frag = urldefrag(self)
            return URIRef(url)
        else:
            return self

    def __reduce__(self):
        """
        TODO:
        """
        return (URIRef, (unicode(self),))

    def __getnewargs__(self):
        """
        TODO:
        """
        return (unicode(self), )


    def __ne__(self, other):
        """
        TODO:
        """
        return not self.__eq__(other)

    def __eq__(self, other):
        """
        TODO:
        """
        if isinstance(other, URIRef):
            return unicode.__eq__(self, other)
        else:
            return False

    def __hash__(self):
        return unicode.__hash__(self)

    def __str__(self):
        """
        TODO:
        """
        return self.encode("unicode-escape")

    def __repr__(self):
        """
        TODO:
        """
        return """rdf.URIRef('%s')""" % str(self)

    def namespace_ncname(self):
        """
        Split URI into a namespace, ncname pair if possible.
        """
        XMLNS = "http://www.w3.org/XML/1998/namespace"
        if self.startswith(XMLNS):
            return (XMLNS, self.split(XMLNS)[1])
        length = len(self)
        for i in xrange(0, length):
            c = self[-i-1]
            if not unicodedata.category(c) in _NAME_CATEGORIES:
                if c in _ALLOWED_NAME_CHARS:
                    continue
                for j in xrange(-1-i, length):
                    if unicodedata.category(self[j]) in _NAME_START_CATEGORIES or self[j]=="_":
                        ns = self[:j]
                        if not ns:
                            break
                        ln = self[j:]
                        return (URIRef(ns), ln)
                break
        raise Exception("Can't split '%s'" % self)

    def __add__(self, val):
        return URIRef(unicode.__add__(self, val))


class BNode(Identifier):
    """
    Blank Node: http://www.w3.org/TR/rdf-concepts/#section-blank-nodes

    Applications should typically create a BNode instance without
    specifying a specific value. Support for specifying a specific value
    is primarily for store implementations to be able to create BNodes
    with a specific value (AKA label).

        >>> from rdf.term import BNode
        >>> b = BNode()
        >>> b.__class__
        <class 'rdf.term.BNode'>


    "In non-persistent O-O software construction, support for object
    identity is almost accidental: in the simplest implementation,
    each object resides at a certain address, and a reference to the
    object uses that address, which serves as immutable object
    identity.

    ...

    Maintaining object identity in shared databases raises problems:
    every client that needs to create objects must obtain a unique
    identity for them; " -- Bertand Meyer
    """
    __slots__ = ()

    def __new__(cls, value=None):
        """
        only store implementations should pass in a value
        """
        if value==None:
            # so that BNode values do not collide with ones created
            # with a different instance of this module at some other
            # time.
            cls._bNodeLock.acquire()
            node_id = cls._sn_gen.next()
            cls._bNodeLock.release()
            value = "%s%s" % (cls._prefix, node_id)
        else:
            # TODO: check that value falls within acceptable bnode value range
            # for RDF/XML needs to be something that can be serialzed as a nodeID
            # for N3 ??
            # Unless we require these constraints be enforced elsewhere?
            pass #assert is_ncname(unicode(value)), "BNode identifiers must be valid NCNames"

        return Identifier.__new__(cls, value)

    def n3(self):
        """
        TODO:
        """
        return "_:%s" % self

    def __getnewargs__(self):
        """
        TODO:
        """
        return (unicode(self), )

    def __reduce__(self):
        """
        TODO:
        """
        return (BNode, (unicode(self),))

    def __ne__(self, other):
        """
        TODO:
        """
        return not self.__eq__(other)

    def __eq__(self, other):
        """
        >>> from rdf.term import URIRef
        >>> from rdf.term import BNode
        >>> BNode("foo")==None
        False
        >>> BNode("foo")==URIRef("foo")
        False
        >>> URIRef("foo")==BNode("foo")
        False
        >>> BNode("foo")!=URIRef("foo")
        True
        >>> URIRef("foo")!=BNode("foo")
        True

        """
        if isinstance(other, BNode):
            return unicode.__eq__(self, other)
        else:
            return False

    def __hash__(self):
        return unicode.__hash__(self)

    def __str__(self):
        """
        TODO:
        """
        return self.encode("unicode-escape")

    def __repr__(self):
        """
        TODO:
        """
        return """rdf.BNode('%s')""" % str(self)

    _bNodeLock = RLock()

    def _serial_number_generator():
        """
        TODO:
        """
        i = 0
        while 1:
            yield i
            i = i + 1

    _sn_gen = _serial_number_generator()

    def _unique_id():
        """
        Create a (hopefully) unique prefix
        """
        from string import ascii_letters
        from random import choice

        id = ""
        for i in xrange(0, 8):
            id += choice(ascii_letters)
        return id
    _prefix=_unique_id()


class Namespace(dict):

    def __new__(cls, uri=None, context=None):
        inst = dict.__new__(cls)
        inst.uri = uri # TODO: do we need to set these both here and in __init__ ??
        inst.__context = context
        return inst

    def __init__(self, uri, context=None):
        self.uri = uri
        self.__context = context

    def term(self, name):
        uri = self.get(name)
        if uri is None:
            uri = URIRef(self.uri + name)
            if self.__context and (uri, None, None) not in self.__context:
                _logger.warning("%s not defined" % uri)
            self[name] = uri
        return uri 

    def __getitem__(self, key, default=None):
        return self.term(key) or default

    def __str__(self):
        return str(self.uri)

    def __repr__(self):
        return """rdf.Namespace('%s')""" % str(self.uri)


class NamespaceHack(Namespace):

    def __getattr__(self, name):
        if name.startswith("__"): # ignore any special Python names!
            raise AttributeError
        else:
            return self.term(name)


XSD = Namespace(u'http://www.w3.org/2001/XMLSchema#')


class Literal(Term, unicode):
    """
    RDF Literal: http://www.w3.org/TR/rdf-concepts/#section-Graph-Literal

    >>> from rdf.term import Literal
    >>> Literal(1).toPython()
    1L
    >>> cmp(Literal("adsf"), 1)
    1
    >>> from rdf.term import XSD
    >>> from datetime import datetime
    >>> lit2006 = Literal('2006-01-01', datatype=XSD["date"])
    >>> lit2006.toPython()
    datetime.date(2006, 1, 1)
    >>> lit2006 < Literal('2007-01-01', datatype=XSD["date"])
    True
    >>> Literal(datetime.utcnow()).datatype
    rdf.URIRef('http://www.w3.org/2001/XMLSchema#dateTime')
    >>> oneInt     = Literal(1)
    >>> twoInt     = Literal(2)
    >>> twoInt < oneInt
    False
    >>> Literal('1') < Literal(1)
    False
    >>> Literal('1') < Literal('1')
    False
    >>> Literal(1) < Literal('1')
    False
    >>> Literal(1) < Literal(2.0)
    True
    >>> Literal(1) < URIRef('foo')
    True
    >>> Literal(1) < 2.0
    False
    >>> Literal(1) < object  
    True
    >>> lit2006 < "2007"
    True
    >>> "2005" < lit2006
    True

    """

    __slots__ = ("language", "datatype")

    _fromPython = {
        str: lambda i: (i, None),
        basestring: lambda i: (i, None),
        float: lambda i: (i, XSD[u'float']),
        int: lambda i: (i, XSD[u'integer']),
        long: lambda i: (i, XSD[u'long']),
        bool: lambda i: (i, XSD[u'boolean']),
        datetime.datetime: lambda i: (i.isoformat(), XSD[u'dateTime']),
        datetime.date: lambda i: (i.isoformat(), XSD[u'date']),
        datetime.time: lambda i: (i.isoformat(), XSD[u'time']),
        }

    _toPython = {
        XSD[u'time']               : _strToTime,
        XSD[u'date']               : _strToDate,
        XSD[u'dateTime']           : _strToDateTime,
        XSD[u'string']             : unicode,
        XSD[u'normalizedString']   : unicode,
        XSD[u'token']              : unicode,
        XSD[u'language']           : unicode,
        XSD[u'boolean']            : lambda i:i.lower() in ['1','true'],
        XSD[u'decimal']            : float,
        XSD[u'integer']            : long,
        XSD[u'nonPositiveInteger'] : int,
        XSD[u'long']               : long,
        XSD[u'nonNegativeInteger'] : int,
        XSD[u'negativeInteger']    : int,
        XSD[u'int']                : long,
        XSD[u'unsignedLong']       : long,
        XSD[u'positiveInteger']    : int,
        XSD[u'short']              : int,
        XSD[u'unsignedInt']        : long,
        XSD[u'byte']               : int,
        XSD[u'unsignedShort']      : int,
        XSD[u'unsignedByte']       : int,
        XSD[u'float']              : float,
        XSD[u'double']             : float,
        XSD[u'base64Binary']       : base64.decodestring,
        XSD[u'anyURI']             : unicode,
        }
 
    def __new__(cls, value, language=None, datatype=None, 
                encoding='utf-8', errors="strict"):
        """
        TODO:
        
        """
        if datatype is None and language is None:
            for c in value.__class__.__mro__:
                f = Literal._fromPython.get(c, None)
                if f:
                    value, datatype = f(value)
                    break
            else:
                raise Exception("Could not convert '%r'" % value)
        elif datatype is not None:
            assert language is None, "language is '%s' datatype is '%s" % (language, datatype)
            assert isinstance(datatype, URIRef), "%r" % datatype
        if isinstance(value, str):
            instance = unicode.__new__(cls, value, encoding=encoding, errors=errors)            
        else:
            instance = unicode.__new__(cls, value)
        instance.language = language
        instance.datatype = datatype
        return instance

    @classmethod
    def bind(cls, datatype, conversion_function):
        """bind a datatype to a function for converting it into a Python instance."""
        if datatype in _toPythonMapping:
            _logger.warning("datatype '%s' was already bound. Rebinding." % datatype)
        cls._toPython[datatype] = conversion_function

    def __reduce__(self):
        """
        TODO:
        """
        return (Literal, (unicode(self), self.language, self.datatype),)

    def __getstate__(self):
        """
        TODO:
        """
        return (None, dict(language=self.language, datatype=self.datatype))

    def __setstate__(self, arg):
        """
        TODO:
        """
        _, d = arg
        self.language = d["language"]
        self.datatype = d["datatype"]

    def __hash__(self):
        """
        >>> a = {Literal('1', datatype=XSD["integer"]): 'one'}
        >>> Literal('1', datatype=XSD["double"]) in a
        False
        
        [[
        Called for the key object for dictionary operations, 
        and by the built-in function hash(). Should return 
        a 32-bit integer usable as a hash value for 
        dictionary operations. The only required property 
        is that objects which compare equal have the same 
        hash value; it is advised to somehow mix together 
        (e.g., using exclusive or) the hash values for the 
        components of the object that also play a part in 
        comparison of objects. 
        ]] -- 3.4.1 Basic customization (Python)

    
        [[
        Two literals are equal if and only if all of the following hold:
        * The strings of the two lexical forms compare equal, character by character.
        * Either both or neither have language tags.
        * The language tags, if any, compare equal.
        * Either both or neither have datatype URIs.
        * The two datatype URIs, if any, compare equal, character by character.
        ]] -- 6.5.1 Literal Equality (RDF: Concepts and Abstract Syntax)
        
        """
        return unicode.__hash__(self) ^ hash(self.language) ^ hash(self.datatype) 

    def __ge__(self, other):
        if other is None:
            return False
        if self==other:
            return True
        else:
            return self > other

    def __ne__(self, other):
        """
        Overriden to ensure property result for comparisons with None via !=.
        Routes all other such != and <> comparisons to __eq__
        
        >>> Literal('') != None
        True
        >>> Literal('2') <> Literal('2')
        False
         
        """
        return not self.__eq__(other)

    def __eq__(self, other):
        """        
        >>> f = URIRef("foo")
        >>> f is None or f == ''
        False
        >>> Literal("1", datatype=URIRef("foo")) == Literal("1", datatype=URIRef("foo"))
        True
        >>> Literal("1", datatype=URIRef("foo")) == Literal("2", datatype=URIRef("foo"))
        False
        >>> Literal("1", datatype=URIRef("foo")) == "asdf"
        False
        >>> Literal('2007-01-01', datatype=XSD["date"]) == Literal('2007-01-01', datatype=XSD["date"])
        True
        >>> from datetime import date
        >>> Literal('2007-01-01', datatype=XSD["date"]) == Literal(date(2007, 1, 1))
        True
        >>> oneInt     = Literal(1)
        >>> oneNoDtype = Literal('1')
        >>> oneInt == oneNoDtype
        False
        >>> Literal("1", XSD[u'string']) == Literal("1", XSD[u'string'])
        True
        >>> Literal("one", language="en") == Literal("one", language="en")
        True
        >>> Literal("hast", language='en') == Literal("hast", language='de')
        False
        >>> oneInt == Literal(1)
        True
        >>> oneFloat   = Literal(1.0)
        >>> oneInt == oneFloat
        False
        
        """
        if other is None or not isinstance(other, Literal):
            return False
        else:
            if self.datatype==other.datatype and self.language==other.language and unicode.__eq__(self, other):
                return True
            else:
                return False

    def n3(self):
        """
        TODO:
        """
        language = self.language
        datatype = self.datatype
        # unfortunately this doesn't work: a newline gets encoded as \\n, which is ok in sourcecode, but we want \n
        #encoded = self.encode('unicode-escape').replace('\\', '\\\\').replace('"','\\"')
        #encoded = self.replace.replace('\\', '\\\\').replace('"','\\"')

        # TODO: We could also chose quotes based on the quotes appearing in the string, i.e. '"' and "'" ...

        # which is nicer?
        #if self.find("\"")!=-1 or self.find("'")!=-1 or self.find("\n")!=-1:
        if self.find("\n")!=-1:
            # Triple quote this string.
            encoded=self.replace('\\', '\\\\')
            if self.find('"""')!=-1: 
                # is this ok?
                encoded=encoded.replace('"""', '\\"""')
            if encoded.endswith('"'): encoded=encoded[:-1]+"\\\""
            encoded='"""%s"""'%encoded
        else: 
            encoded='"%s"'%self.replace('\n', '\\n').replace('\\', '\\\\').replace('"', '\\"')
        if language:
            if datatype:    
                return '%s@%s^^<%s>' % (encoded, language, datatype)
            else:
                return '%s@%s' % (encoded, language)
        else:
            if datatype:
                return '%s^^<%s>' % (encoded, datatype)
            else:
                return '%s' % encoded

    def __str__(self):
        r"""
        >>> from rdf.term import Literal
        >>> a = Literal("This \t is a test")

        The following need not be true in general as str() returns an
        'informal' string:

            >>> Literal(str(a))==a
            False

        But the following still needs to be true:

            >>> s = "%s" % a
            >>> s
            u'This \t is a test'

        We're using the unicode-escape encoding for the informal
        string:

            >>> str(a)
            'This \\t is a test'

            >>> b = Literal(u"\u00a9")
            >>> str(b)
            '\\xa9'

        """
        return self.encode("unicode-escape")

    def __repr__(self):
        """
        TODO
        """
        return """rdf.Literal(%s, language=%s, datatype=%s)""" % (
                super(Literal, self).__repr__(),
                repr(self.language),
                repr(self.datatype))

    def toPython(self):
        """
        Returns an appropriate python datatype derived from this RDF Literal
        """
        convFunc = Literal._toPython.get(self.datatype, None)
        if convFunc is not None:
            return convFunc(self)
        else:
            raise Exception("Could not convert '%r' to Python" % self)

    def __add__(self, val):
        """
        #>>> Literal(1) + 1
        #2L
        #>>> Literal("1") + "1"
        #rdf.Literal(u'11', language=None, datatype=None)

        """
        s = unicode.__add__(self, val)
        return Literal(s, self.language, self.datatype)


class Variable(Term, unicode):
    """
    TODO:
    """
    __slots__ = ()
    def __new__(cls, value):
        if value[0]=='?':
            value=value[1:]
        return unicode.__new__(cls, value)

    def __repr__(self):
        return self.n3()

    def n3(self):
        return "?%s" % self

    def __reduce__(self):
        return (Variable, (unicode(self),))


class Statement(Term, tuple):

    def __new__(cls, triple, context):
        return tuple.__new__(cls, (triple, context))

    def __reduce__(self):
        return (Statement, (self[0], self[1]))


class ClosedNamespace(NamespaceHack):
    """
    
    """

    def __init__(self, uri, terms):
        self.uri = uri
        self.__uris = {}
        for t in terms:
            self.__uris[t] = URIRef(self.uri + t)

    def term(self, name):
        uri = self.__uris.get(name)
        if uri is None:
            raise Exception("term '%s' not in '%r'" % (name, self.uri))
        else:
            return uri

    def __getitem__(self, key, default=None):
        return self.term(key)

    def __str__(self):
        return str(self.uri)

    def __repr__(self):
        return """rdf.ClosedNamespace('%s')""" % str(self.uri)


RDF = ClosedNamespace(URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#"), [
        # Syntax Names
        "RDF", "Description", "ID", "about", "parseType", "resource", "li", "nodeID", "datatype", 

        # RDF Classes
        "Seq", "Bag", "Alt", "Statement", "Property", "XMLLiteral", "List", 

        # RDF Properties
        "subject", "predicate", "object", "type", "value", "first", "rest", 
        # and _n where n is a non-negative integer
             
        # RDF Resources          
        "nil"])


RDFS = ClosedNamespace(URIRef("http://www.w3.org/2000/01/rdf-schema#"), [
        "Resource", "Class", "subClassOf", "subPropertyOf", "comment", "label", 
        "domain", "range", "seeAlso", "isDefinedBy", "Literal", "Container", 
        "ContainerMembershipProperty", "member", "Datatype"])
