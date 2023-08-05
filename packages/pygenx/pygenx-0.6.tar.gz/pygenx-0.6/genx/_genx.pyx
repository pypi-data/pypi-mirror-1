#
# Copyright (c) 2004 Michael Twomey
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY
# KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
# WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
# LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
# WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#

__version__ = "0.6"

cdef extern from "stdio.h":
    ctypedef struct FILE

cdef extern from "Python.h":

    FILE* PyFile_AsFile(object)
    ctypedef void *PyObject

cdef extern from "genx.h":
    ctypedef enum genxStatus:
        GENX_SUCCESS = 0,
        GENX_BAD_UTF8,
        GENX_NON_XML_CHARACTER,
        GENX_BAD_NAME,
        GENX_ALLOC_FAILED,
        GENX_BAD_NAMESPACE_NAME,
        GENX_INTERNAL_ERROR,
        GENX_DUPLICATE_PREFIX,
        GENX_SEQUENCE_ERROR,
        GENX_NO_START_TAG,
        GENX_IO_ERROR,
        GENX_MISSING_VALUE,
        GENX_MALFORMED_COMMENT,
        GENX_XML_PI_TARGET,
        GENX_MALFORMED_PI,
        GENX_DUPLICATE_ATTRIBUTE,
        GENX_ATTRIBUTE_IN_DEFAULT_NAMESPACE,
        GENX_DUPLICATE_NAMESPACE,
        GENX_BAD_DEFAULT_DECLARATION

    #Not sure about using void*, it seems to keep the compiler happy :)
    ctypedef void * genxWriter
    ctypedef void * genxNamespace
    ctypedef void * genxElement
    ctypedef void * genxAttribute

    ctypedef char * utf8
    ctypedef char * constUtf8

    #Constructors
    genxWriter genxNew(void *(*alloc)(void * userData, int bytes), void (* dealloc)(void * userData, void * data), void * userData)
    
    #Destructors
    void genxDispose(genxWriter w)

    #set/get

    void genxSetUserData(genxWriter w, void * userData)

    void * genxGetUserData(genxWriter w)

    #Memory management
    void genxSetAlloc(genxWriter w, void * (* alloc)(void * userData, int bytes))
    void genxSetDealloc(genxWriter w, void (* dealloc)(void * userData, void * data))

    #Get the prefix associated with a namespace
    utf8 genxGetNamespacePrefix(genxNamespace ns)

    #Declarations
    genxNamespace genxDeclareNamespace(genxWriter w, constUtf8 uri, constUtf8 prefix,
        genxStatus * statusP)

    genxElement genxDeclareElement(genxWriter w, genxNamespace ns,
        constUtf8 type, genxStatus * statusP)

    genxAttribute genxDeclareAttribute(genxWriter w, genxNamespace ns,
        constUtf8 name, genxStatus * statusP)

    #Start a new document
    genxStatus genxStartDocFile(genxWriter w, FILE * file)

    # Caller-provided I/O package.
    ctypedef struct genxSender:
        genxStatus (* send)(void * userData, constUtf8 s) 
        genxStatus (* sendBounded)(void * userData, constUtf8 start, constUtf8 end)
        genxStatus (* flush)(void * userData)

    genxStatus genxStartDocSender(genxWriter w, genxSender * sender)
    
    #End a document
    genxStatus genxEndDocument(genxWriter w)

    #Write a comment
    genxStatus genxComment(genxWriter w, constUtf8 text)

    #Write a PI
    genxStatus genxPI(genxWriter w, constUtf8 target, constUtf8 text)

    #Start an element
    genxStatus genxStartElementLiteral(genxWriter w, constUtf8 namespace, constUtf8 type)

    #Start a predeclared element
    genxStatus genxStartElement(genxElement e)

    #Add an attribute
    genxStatus genxAddAttributeLiteral(genxWriter w, constUtf8 xmlns,
        constUtf8 name, constUtf8 value)

    #Write a predeclared attribute
    genxStatus genxAddAttribute(genxAttribute a, constUtf8 value)

    #add a namespace declaration
    genxStatus genxAddNamespace(genxNamespace ns, utf8 prefix)

    #Clear default namespace declaration
    genxStatus genxUnsetDefaultNamespace(genxWriter w)

    #Write an end tag
    genxStatus genxEndElement(genxWriter w)
    
    #Write some text
    genxStatus genxAddText(genxWriter w, constUtf8 start)

    genxStatus genxAddCountedText(genxWriter w, constUtf8 start, int byteCount)

    genxStatus genxAddBoundedText(genxWriter w, constUtf8 start, constUtf8 end)

    #Write one character
    genxStatus genxAddCharacter(genxWriter w, int c)

    #Utility routines

    #Return the Unicode character encoded by the UTF-8 pointed-to by the
    #argument, and advance the argument past the encoding of the character.
    #Returns -1 if the UTF-8 is malformed, in which case advances the
    #argument to point at the first byte past the point past the malformed
    #ones.
    int genxNextUnicodeChar(constUtf8 * sp)

    #Scan a buffer of allegedly UTF-8 encoded characters, return one of
    #GENX_SUCCES, GENX_BAD_UTF8, GENX_NON_XML_CHARACTER
    genxStatus genxCheckText(genxWriter w, constUtf8 s)

    #Return character status, the OR of GENX_XML_CHAR, GENX_LETTER, GENX_NAMECHAR
    int genxCharClass(genxWriter w, int c)

    #Silent scrub non XML from a chunk of text
    #Returns true if changes were made
    int genxScrubText(genxWriter w, constUtf8 text_in, utf8 text_out)

    #Return error messages
    char * genxGetErrorMessage(genxWriter w, genxStatus status)

    char * genxLastErrorMessage(genxWriter w)

    #Return version
    char * genxGetVersion()

class GenxError(Exception):
    """Raised when an error occurs during one of the genx calls.
    
    This is a generic error, (i.e. when the status != GENX_SUCCESS).
    """
    pass

class DuplicateAttributeError(Exception):
    """Raised when a duplicate attribute is added to an element

    Represents GENX_DUPLICATE_ATTRIBUTE
    """
    pass

class BadNamespaceNameError(Exception):
    """Raised when the namespace given is invalid.

    Represents GENX_BAD_NAMESPACE_NAME
    """
    pass

class DuplicatePrefixError(Exception):
    """Raised when there is a duplicaten xmlns prefix

    Represents GENX_DUPLICATE_PREFIX
    """
    pass

class BadNameError(Exception):
    """Raised when an invalid name is used

    Represents GENX_BAD_NAME
    """
    pass

class SequenceError(Exception):
    """Raised when calls are mad in an invalid sequence.

    Represents GENX_SEQUENCE_ERROR
    """
    pass

class AttributeInDefaultNamespaceError(Exception):
    """

    Represents GENX_ATTRIBUTE_IN_DEFAULT_NAMESPACE
    """
    pass

class IOError(Exception):
    """Raised when there is an IO problem

    Represents GENX_IO_ERROR
    """
    pass

class BadUTF8Error(Exception):
    """Raised for invalid UTF-8 strings

    Represents GENX_BAD_UTF8
    """
    pass

class NonXMLCharacterError(Exception):
    """

    Represents GENX_NON_XML_CHARACTER
    """
    pass

class MalformedPIError(Exception):
    """Raised for bad Processing Instructions (PI)

    Represents GENX_MALFORMED_PI
    """
    pass

class DuplicateNamespaceError(Exception):
    """

    Represents GENX_DUPLICATE_NAMESPACE
    """
    pass

class BadDefaultDeclarationError(Exception):
    """

    Represents GENX_BAD_DEFAULT_DECLARATION
    """
    pass

def get_version():
    """Returns the genx version string, as defined in the original C library"""
    return genxGetVersion()

cdef class Namespace:
    """A simple class to contain the genxNamespace variable"""
    cdef genxNamespace ns
    cdef utf8 uri
    cdef utf8 xmlns

    def __init__(self, uri, xmlns=None):
        """Create an namespace using a namespace URI and an optional xmlns value.

        Note that on it's own it isn't a great deal of use, it's normally created from inside
        a Writer instance, which sets an elem attribute with a genxNamespace."""
        self.uri = uri
        if xmlns == None:
            self.xmlns = ""
        else:
            self.xmlns = xmlns

    def __repr__(self):
        """Returns a text representation of the element, useful for comparisons"""
        return "<Namespace %s:%s>" % (self.uri, self.xmlns)

    def __cmp__(self, other):
        """Compares one namespace to another, though anything with a meaningful repr will work"""
        return cmp(repr(self), repr(other))

cdef class Element:
    """A simple class to contain the genxElement variable"""
    cdef genxElement elem
    cdef utf8 name
    cdef Namespace namespace

    def __init__(self, name, Namespace namespace=None):
        """Create an element using an element name and an optional Namespace.

        Note that on it's own it isn't a great deal of use, it's normally created from inside
        a Writer instance, which sets an elem attribute with a genxElement."""
        self.name = name
        self.namespace = namespace

    def __repr__(self):
        """Returns a text representation of the element, useful for comparisons"""
        return "<Element %r:%s>" % (self.namespace, self.name)

    def __cmp__(self, other):
        """Compares one element to another, though anything with a meaningful repr will work"""
        return cmp(repr(self), repr(other))

cdef class Attribute:
    """A simple class to contain the genxAttribute variable"""
    cdef genxAttribute attr
    cdef utf8 name
    cdef Namespace namespace

    def __init__(self, name, Namespace namespace=None):
        """Create an attribute using an attribute name and an optional Namespace.

        Note that on it's own it isn't a great deal of use, it's normally created from inside
        a Writer instance, which sets an attr attribute with a genxAttribute."""
        self.name = name
        self.namespace = namespace
    
    def __repr__(self):
        """Returns a text representation of the attribute, useful for comparisons"""
        return "<Attribute %r:%s>" % (self.namespace, self.name)

    def __cmp__(self, other):
        """Compares one attribute to another, though anything with a meaningful repr will work"""
        return cmp(repr(self), repr(other))

#genxSender callbacks

cdef genxStatus send(void * userData, constUtf8 s):
    data_tuple = <object> userData
    fp = data_tuple[0]
    fp.write(s)
    return GENX_SUCCESS

cdef genxStatus send_bounded(void * userData, constUtf8 start, constUtf8 end):
    data_tuple = <object>userData
    fp = data_tuple[0]
    length = end - start
    fp.write(start[0:length])
    return GENX_SUCCESS

cdef genxStatus flush(void * userData):
    data_tuple = <object>userData
    fp = data_tuple[0]
    fp.flush()
    return GENX_SUCCESS

cdef genxSender sender
sender.send = &send
sender.sendBounded = &send_bounded
sender.flush = &flush

cdef class Writer:
    """The main genx class, each one of these typically represents a document"""
    cdef genxWriter writer
    cdef object userData # Keep a reference to the user data around, lest it gets garbage collected

    def __new__(self):
        self.writer = genxNew(NULL, NULL, NULL)

    def __dealloc__(self):
        genxDispose(self.writer)

    def startDocFile(self, fp):
        """Start a new document, using the given file pointer.

        The file should either be a Python file object or an object with
        write() and flush() methods.
        """
        cdef FILE * c_fp
        
        is_file = 1

        if not hasattr(fp, "fileno"):
            is_file = 0
            
        c_fp = PyFile_AsFile(fp)
        if c_fp == NULL:
            is_file = 0
            
        if is_file:
            status = genxStartDocFile(self.writer, c_fp)
        else:
            self.userData = [fp, ] # Wrap up the object in a PyObject tuple
            genxSetUserData(self.writer, <void *>self.userData)
            status = genxStartDocSender(self.writer, &sender)
        self.__checkStatus(status)

    def startElementLiteral(self, name, namespace=None):
        """Starts a new element, optionally with a namespace"""
        cdef constUtf8 c_namespace
        #Check if the name is None
        if name == None:
            raise BadUTF8Error, "Passed None in as element name"
        #Check if the namespace is empty (invalid) or not declared
        if namespace == None or namespace == "":
            c_namespace = NULL
        else:
            namespace = namespace.encode("UTF-8")
            c_namespace = namespace
        name = name.encode("UTF-8")
        status = genxStartElementLiteral(self.writer, c_namespace, name)
        self.__checkStatus(status)

    def addText(self, text):
        """Add text to the current element"""
        if text == None:
            raise BadUTF8Error, "Passed in None instead of text"
        text = text.encode("UTF-8")
        status = genxAddText(self.writer, text)
        self.__checkStatus(status)

    def comment(self, text):
        """Adds a comment to the generated XML"""
        if text == None:
            raise BadUTF8Error, "Passed in None instead of text"
        text = text.encode("UTF-8")
        status = genxComment(self.writer, text)
        self.__checkStatus(status)

    def PI(self, target, text):
        """Adds a processing instruction"""
        if text == None:
            raise BadUTF8Error, "Passed in None instead of text"
        text = text.encode("UTF-8")
        status = genxPI(self.writer, target, text)
        self.__checkStatus(status)
        
    def endElement(self):
        """Closes the current element"""
        status = genxEndElement(self.writer)
        self.__checkStatus(status)

    def addNamespace(self, Namespace namespace, prefix = None):
        """Add a namespace declaration"""
        cdef Namespace c_namespace
        cdef genxNamespace genx_namespace
        cdef constUtf8 c_prefix

        c_namespace = namespace
        genx_namespace = c_namespace.ns

        if prefix == None or prefix == "":
            c_prefix = NULL
        else:
            prefix = prefix.encode("UTF-8")
            c_prefix = prefix

        status = genxAddNamespace(genx_namespace, c_prefix)
        self.__checkStatus(status)

    def unsetDefaultNamespace(self):
        """Clears the default namespace declaration"""
        status = genxUnsetDefaultNamespace(self.writer)
        self.__checkStatus(status)

    def endDocument(self):
        """Closes the current document"""
        status = genxEndDocument(self.writer)
        self.__checkStatus(status)

    def addAttributeLiteral(self, name, value, namespace=None):
        """Adds a new attribute to the current element, with an optional namespace"""
        cdef char * c_namespace

        if namespace == None or namespace == "":
            c_namespace = NULL
        else:
            namespace = namespace.encode("UTF-8")
            c_namespace = namespace

        status = genxAddAttributeLiteral(self.writer, c_namespace, name, value)
        self.__checkStatus(status)

    def __checkStatus(self, status):
        """Checks the given status code, if it isn't GENX_SUCCESS, an
        exception is raised"""
        if status != GENX_SUCCESS:
            status_info = genxGetErrorMessage(self.writer, status)
            #TODO replace with a dict lookup
            if status == GENX_BAD_NAMESPACE_NAME:
                raise BadNamespaceNameError, "%r" % status_info
            elif status == GENX_DUPLICATE_PREFIX:
                raise DuplicatePrefixError, "%r" % status_info
            elif status == GENX_BAD_NAME:
                raise BadNameError, "%r" % status_info
            elif status == GENX_SEQUENCE_ERROR:
                raise SequenceError, "%r" % status_info
            elif status == GENX_ATTRIBUTE_IN_DEFAULT_NAMESPACE:
                raise AttributeInDefaultNamespaceError, "%r" % status_info
            elif status == GENX_DUPLICATE_ATTRIBUTE:
                raise DuplicateAttributeError, "%r" % status_info
            elif status == GENX_IO_ERROR:
                raise IOError, "%r" % status_info
            elif status == GENX_NON_XML_CHARACTER:
                raise NonXMLCharacterError, "%r" % status_info
            elif status == GENX_BAD_UTF8:
                raise BadUTF8Error, "%r" % status_info
            elif status == GENX_MALFORMED_PI:
                raise MalformedPIError, "%r" % status_info
            elif status == GENX_DUPLICATE_NAMESPACE:
                raise DuplicateNamespaceError, "%r" % status_info
            elif status == GENX_BAD_DEFAULT_DECLARATION:
                raise BadDefaultDeclarationError, "%r" % status_info
            else:
                raise GenxError("Problem with genx, %d, %r" % (status, status_info))

    def declareNamespace(self, uri, prefix=None):
        """Declares a namespace, returning a Namespace object which can be used later."""
        cdef genxNamespace ns
        cdef genxStatus status
        cdef constUtf8 c_prefix

        if uri == None:
            raise BadNamespaceNameError, "%r is an invalid namespace" % uri
        
        if prefix == None:
            c_prefix = NULL
        else:
            prefix = prefix.encode("UTF-8")
            c_prefix = prefix
        
        uri = uri.encode("UTF-8")
        ns = genxDeclareNamespace(self.writer, uri, c_prefix, &status)
        if ns == NULL:
            self.__checkStatus(<int>status)
        cdef Namespace namespace
        namespace = Namespace(uri, prefix)
        namespace.ns = ns
        return namespace

    def declareElement(self, type, Namespace namespace=None):
        """Create a new Element object, optionally using a Namespace object"""
        cdef genxElement elem
        cdef genxStatus status
        cdef genxNamespace ns
        cdef Namespace c_namespace

        if type == None:
            raise BadUTF8Error, "Passed in None for type, instead of text"

        if namespace == None:
            ns = NULL
        else:
            #Convert the python namespace to a more C friendly one
            c_namespace = namespace
            ns = c_namespace.ns
        
        type = type.encode("UTF-8")
        elem = genxDeclareElement(self.writer, ns, type, &status)
        if elem == NULL:
            self.__checkStatus(<int>status)

        cdef Element element
        element = Element(type, namespace)
        element.elem = elem
        return element

    def declareAttribute(self, name, Namespace namespace=None):
        """Create a new Attribute object, optionally using a Namespace object"""
        cdef genxAttribute attr
        cdef genxStatus status
        cdef genxNamespace ns
        cdef Namespace c_namespace

        if name == None:
            raise BadUTF8Error, "Passed in None for name, instead of text"

        if namespace == None:
            ns = NULL
        else:
            #convert the python to a more friendly c object
            c_namespace = namespace
            ns = c_namespace.ns

        name = name.encode("UTF-8")
        attr = genxDeclareAttribute(self.writer, ns, name, &status)
        if attr == NULL:
            self.__checkStatus(<int>status)

        cdef Attribute attribute
        attribute = Attribute(name, namespace)
        attribute.attr = attr
        return attribute

    def startElement(self, Element element):
        """Starts a new element using the given Element object"""
        cdef Element c_element
        cdef genxElement elem

        c_element = element
        elem = c_element.elem
        status = genxStartElement(elem)
        self.__checkStatus(status)

    def addAttribute(self, Attribute attribute, value):
        """Adds an attribute using the given Attribute object"""
        cdef Attribute c_attribute
        cdef genxAttribute attr
        cdef genxStatus status

        c_attribute = attribute
        attr = c_attribute.attr
        status = genxAddAttribute(attr, value)
        self.__checkStatus(status)

    def addAttributes(self, attributes):
        """Adds the attributes using the given dictionary

        This is a simple convenience function which will iterate over
        the items in the given dictionary, adding them using
        `genxAddAttributeLiteral` and the default namespace.

        This is currently more of an experimental method, it should be
        faster than iteratively adding attributes from python code as
        the loop is executed in C. This method doesn't support
        namespaces or use any declared Attribute objects.
        
        """
        for attr, value in attributes.items():
            status = genxAddAttributeLiteral(self.writer, NULL, attr, value)
            self.__checkStatus(status)

    def checkText(self, text):
        """Checks the validity of the given text"""
        #TODO: need a decode/encode here?
        status = genxCheckText(self.writer, text)
        return status

    def scrubText(self, text):
        """Silently wipes all non-XML characters out of the given string"""
        #TODO: need a decode/encode here?
        cdef constUtf8 out_string
        #Initialize out_string or we get into core dump land
        out_string = ""
        status = genxScrubText(self.writer, text, out_string)
        #not bothering to check the return, python's str cmp should be enough if you want
        #to check, besides to do that meaningfully in a python context would mean returning
        #a tuple with the status code and the string, and I'm not a fan of in place editing
        return out_string
