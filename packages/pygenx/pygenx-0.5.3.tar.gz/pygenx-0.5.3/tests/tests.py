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

import unittest
#from tempfile import TemporaryFile
import os
import random
from StringIO import StringIO

import genx

def get_file_pointer():
    """Returns a file pointer suitable for testing.
    
    Got sick of swapping different library calls in an out to facilitate
    different OS's points of view so using a single function to generate
    test file objects.
    """
    fp = StringIO()
    return fp

def read_file_pointer(fp):
    """Flushes, rewinds and reads the contents of the given file object"""
    fp.flush()
    fp.seek(0)
    output = fp.read().decode("UTF-8")
    return output

class GenxTestCase(unittest.TestCase):
    def setUp(self):
        self.writer = genx.Writer()
        self.ns1 = self.writer.declareNamespace("http://example.com/1")
        self.ns2 = self.writer.declareNamespace("http://example.com/2", "a-ns2")
        self.ela = self.writer.declareElement("a")
        self.elb = self.writer.declareElement("b", self.ns1)
        self.elc = self.writer.declareElement("c", self.ns2)
        self.a1 = self.writer.declareAttribute("a1")
        self.a2 = self.writer.declareAttribute("a2", self.ns2)
        self.a3 = self.writer.declareAttribute("a3", self.ns1)

    def tearDown(self):
        self.writer = None
        self.ns1 = None
        self.ns2 = None
        self.ela = None
        self.elb = None
        self.elc = None
        self.a1 = None
        self.a2 = None
        self.a3 = None

    def testGoodString(self):
        """checkUTF8()"""
        good_string = "\x26\xd0\x96\xe4\xb8\xad\xf0\x90\x8d\x86"
        self.assertEquals(self.writer.checkText(good_string), genx.GENX_SUCCESS)

    def testNonXmlString(self):
        """checkUTF8()"""
        non_xml_string = "<a>\x01"
        self.assertEquals(self.writer.checkText(non_xml_string), genx.GENX_NON_XML_CHARACTER)

    def testBadUTF8Strings(self):
        """checkUTF8()"""
        bad_utf8_strings = [
            "\xc0\xaf",
            "\xc2\x7f",
            "\x80\x80",
            "\x80\x9f",
            "\xe1\x7f",
            "\xe1\x80",
            "\xe1\x80\x7f",
        ]
        for bad_utf8_string in bad_utf8_strings:
            self.assertEquals(self.writer.checkText(bad_utf8_string), genx.GENX_BAD_UTF8)

    def testScrubGoodString(self):
        """checkScrub()"""
        good_string = "\x26\xd0\x96\xe4\xb8\xad\xf0\x90\x8d\x86"
        self.assertEquals(self.writer.scrubText(good_string), good_string)

    def testScrubXmlString(self):
        """checkScrub()"""
        xml_string = "<a>\x01"
        self.assertEquals(self.writer.scrubText(xml_string), "<a>")

    def testScrubBadStrings(self):
        """checkScrub()"""
        bad_utf8_strings = [
            ("\xc0\xaf", ""),
            ("\xc2\x7f", ""),
            ("\x80\x80", ""),
            ("\x80\x9f", ""),
            ("\xe1\x7f", ""),
            ("\xe1\x80", ""),
            ("\xe1\x80\x7f", ""),
            ("\x80a", "a"),
            ("\x05a", "a"),
        ]
        for (bad_utf8_string, result) in bad_utf8_strings:
            self.assertEquals(self.writer.scrubText(bad_utf8_string), result)
            self.assertEquals(self.writer.checkText(result), genx.GENX_SUCCESS)

    def testDeclareNS_1(self):
        """checkDeclareNS()"""
        #should have no problems
        ns = self.writer.declareNamespace("http://www.textuality.com/ns/")
        self.writer.declareNamespace("http://www.textuality.com/ns/", "foo")
    
    def testDeclareNS_2(self):
        """checkDeclareNS()"""
        #should throw a bad name exception
        self.assertRaises(genx.BadNamespaceNameError, self.writer.declareNamespace, None)
    
    def testDeclareNS_3(self):
        """checkDeclareNS()"""
        #should throw a bad name exception
        self.assertRaises(genx.BadNamespaceNameError, self.writer.declareNamespace, "")
    
    def testDeclareNS_4(self):
        """checkDeclareNS()"""
        ns = self.writer.declareNamespace("http://tbray.org/", "foo")
        ns = self.writer.declareNamespace("http://tbray.org/", "foo")
        #should throw a duplicate prefix exception
        self.assertRaises(genx.DuplicatePrefixError, self.writer.declareNamespace, "http://textuality.com/", "foo")
        
    def testDeclareNS_5(self):
        """checkDeclareNS()"""
        ns = self.writer.declareNamespace("http://tbray.org/")
        #should throw a duplicate prefix exception
        self.assertRaises(genx.DuplicatePrefixError, self.writer.declareNamespace, "http://foo.org/", "g1")
    
    def testDeclareNS_6(self):
        """checkDeclareNS()"""
        self.writer.declareNamespace("http://tbray.org/", "")
        #dupe URI with empty prefix
        self.assertRaises(genx.DuplicatePrefixError, self.writer.declareNamespace, "http://tbray2.org/xyz", "")

    def testDeclareEl(self):
        """checkDeclareEl()"""
        #Ordinary deeclare el
        el = self.writer.declareElement("a")
        #Should catch bad name
        self.assertRaises(genx.BadNameError, self.writer.declareElement, "???")
        
    def testDeclareEl_2(self):
        """checkDeclareEl()"""
        #Ordinary declare el (2)
        el = self.writer.declareElement("a")
        #Dupe declare el
        el = self.writer.declareElement("a")
        
        ns1 = self.writer.declareNamespace("http://tbray.org/")
        ns2 = self.writer.declareNamespace("http://foo.org/", "foo")

        #Basic with ns 1
        el = self.writer.declareElement("x", ns1)
        #Basic with ns 2
        el2 = self.writer.declareElement("y", ns2)
        #Dupe with ns
        el2 = self.writer.declareElement("x", ns1)
        #Dupe made new el object?!?
        #Not sure this is really a valid test in the python context
        self.assertEquals(el, el2)

    def testNamespace(self):
        """Tests the python Namespace class"""
        ns1 = genx.Namespace("http://example.com/1", "example")
        ns2 = genx.Namespace("http://example.com/1", "example")
        self.assertEquals(ns1, ns2)
        ns3 = genx.Namespace("http://example.com/2")
        ns4 = genx.Namespace("http://example.com/2")
        self.assertEquals(ns3, ns4)
        self.assertNotEquals(ns1, ns3)

    def testElement(self):
        """Tests the python Element class"""
        ns1 = genx.Namespace("http://example.com/1", "example")
        ns2 = genx.Namespace("http://example.com/2")
        el = genx.Element("foo")
        self.assertEquals(repr(el), "<Element None:foo>")
        el2 = genx.Element("bar", ns1)
        self.assertEquals(repr(el2), "<Element <Namespace http://example.com/1:example>:bar>")
        el3 = genx.Element("baz", ns2)
        self.assertEquals(repr(el3), "<Element <Namespace http://example.com/2:>:baz>")
        el4 = genx.Element("foo")
        self.assertEquals(el, el4)
        self.assertNotEquals(el, el3)

    def testDeclareAttr(self):
        """checkDeclareAttr()"""
        #Ordinary declare attr
        a = self.writer.declareAttribute("a")
        #Should catch bad name
        self.assertRaises(genx.BadNameError, self.writer.declareAttribute, "^^^")

    def testDeclareAttr_2(self):
        """checkDeclareAttr()"""
        #Ordinary declare attr (2)
        a = self.writer.declareAttribute("a")
        #Dupe declare attr
        a = self.writer.declareAttribute("a")

        ns1 = self.writer.declareNamespace("http://tbray.org/")
        ns2 = self.writer.declareNamespace("http://foo.org/", "foo")

        #Basic with ns 1
        a = self.writer.declareAttribute("x", ns1)
        #Basic with ns 2
        a2 = self.writer.declareAttribute("y", ns2)
        #Dupe with ns
        a3 = self.writer.declareAttribute("x", ns1)
        #Dupe made new attr object?!?
        self.assertEquals(a, a3)
        self.assertNotEquals(a, a2)

    def testAttribute(self):
        """Tests the python Attribute class"""
        ns1 = genx.Namespace("http://example.com/1", "example")
        ns2 = genx.Namespace("http://example.com/2")
        at = genx.Attribute("foo")
        self.assertEquals(repr(at), "<Attribute None:foo>")
        at2 = genx.Attribute("bar", ns1)
        self.assertEquals(repr(at2), "<Attribute <Namespace http://example.com/1:example>:bar>")
        at3 = genx.Attribute("baz", ns2)
        self.assertEquals(repr(at3), "<Attribute <Namespace http://example.com/2:>:baz>")
        at4 = genx.Attribute("foo")
        self.assertEquals(at, at4)
        self.assertNotEquals(at, at3)

    def testSeq1(self):
        """checkSeq1()"""
        fp = get_file_pointer()
        self.writer.startDocFile(fp)
        self.assertRaises(genx.SequenceError, self.writer.startDocFile, fp)

    def testSeq2(self):
        """checkSeq2()"""
        fp = get_file_pointer()
        self.assertRaises(genx.SequenceError, self.writer.startElement, self.ela)

    def testSeq3(self):
        """checkSeq3()"""
        fp = get_file_pointer()
        self.writer.startDocFile(fp)
        self.assertRaises(genx.SequenceError, self.writer.endElement)

    def testSeq4(self):
        """checkSeq4()"""
        fp = get_file_pointer()
        self.writer.startDocFile(fp)
        self.writer.startElement(self.ela)
        self.assertRaises(genx.SequenceError, self.writer.endDocument)

    def testSeq5(self):
        """checkSeq5()"""
        fp = get_file_pointer()
        self.writer.startDocFile(fp)
        self.writer.startElement(self.ela)
        self.writer.startElement(self.elb)
        self.writer.endElement()
        self.assertRaises(genx.SequenceError, self.writer.endDocument)

    def testDefaultNS(self):
        """checkDefaultNS"""
        fp = get_file_pointer()
        #Omitting genxSetUserData and genxStarDocSender
        #Though they would be useful for mapping onto a StringIO type buffer
        self.writer.startDocFile(fp)
        
        nDefault = self.writer.declareNamespace("http://def", "")
        nPrefix = self.writer.declareNamespace("http://pref", "pref")
        self.assertRaises(genx.AttributeInDefaultNamespaceError, self.writer.declareAttribute, "foo", nDefault)

        eNaked = self.writer.declareElement("e")
        eDefault = self.writer.declareElement("eD", nDefault)
        ePrefix = self.writer.declareElement("eP", nPrefix)

        self.writer.startElement(eDefault)
        self.writer.addNamespace(nPrefix)
        self.writer.startElement(eNaked)

        self.writer.declareNamespace("http://pref", "foobar")

        self.writer.endElement()
        self.writer.startElement(ePrefix)
        self.writer.unsetDefaultNamespace()
        self.writer.startElement(eNaked)
        self.writer.endElement()
        self.writer.startElement(eDefault)
    
        #Hmmm, not sure about this
        #Would a Writer.FinishDocument() would be neater for situations like this?
        while 1:
            try:
                self.writer.endElement()
            except genx.SequenceError:
                break
        
        self.writer.endDocument()

        #Read the file contents back in
        out = read_file_pointer(fp)

        #Check against the expected output
        self.assertEquals(out, "<eD xmlns=\"http://def\" xmlns:pref=\"http://pref\"><e xmlns=\"\"></e><foobar:eP xmlns=\"\" xmlns:foobar=\"http://pref\"><e></e><eD xmlns=\"http://def\"></eD></foobar:eP></eD>")

    def testHello(self):
        """checkHello"""

        greeting = self.writer.declareElement("greeting")

        #Not using genxSetUserData
        fp = get_file_pointer()

        self.writer.startDocFile(fp)
        self.writer.startElement(greeting)
        self.writer.addText("Hello world!")
        self.writer.endElement()
        self.writer.endDocument()

        output = read_file_pointer(fp)
        self.assertEquals(output, "<greeting>Hello world!</greeting>")

    def testHelloNS(self):
        """checkHelloNS"""
        ns = self.writer.declareNamespace("http://example.org/x", "eg")
        greeting = self.writer.declareElement("greeting", ns)

        #Not using genxSetUserData
        fp = get_file_pointer()
        self.writer.startDocFile(fp)

        self.writer.startElement(greeting)
        self.writer.addText("Hello world!")
        self.writer.endElement()
        self.writer.endDocument()

        output = read_file_pointer(fp)

        self.assertEquals(output, "<eg:greeting xmlns:eg=\"http://example.org/x\">Hello world!</eg:greeting>")

    def testAttrOrder(self):
        """checkAttrOrder"""
        #Not using genxSetUserData
        fp = get_file_pointer()
        self.writer.startDocFile(fp)

        self.writer.startElement(self.ela)
        self.writer.addAttribute(self.a1, "1")
        self.writer.addAttribute(self.a2, "2")
        self.writer.addAttribute(self.a3, "3")
        self.writer.endElement()
        self.writer.endDocument()

        output = read_file_pointer(fp)

        self.assertEquals(output, "<a xmlns:a-ns2=\"http://example.com/2\" xmlns:g1=\"http://example.com/1\" a1=\"1\" g1:a3=\"3\" a-ns2:a2=\"2\"></a>")

    def testDupeAttr(self):
        """checkDupeAttr"""
        #Not using genxSetUserData
        fp = get_file_pointer()
        self.writer.startDocFile(fp)

        self.writer.startElement(self.ela)
        self.writer.addAttribute(self.a1, "1")
        self.assertRaises(genx.DuplicateAttributeError, self.writer.addAttribute, self.a1, "1")

    def testIOError(self):
        """checkIOError"""
        greeting = self.writer.declareElement("greeting")
        
        #Not using genxSetUserData
        fp = os.tmpfile()
        self.writer.startDocFile(fp)

        #Close the file, in order to raise an IO error
        fp.close()
        self.writer.startElement(greeting)
        self.assertRaises(genx.IOError, self.writer.addText, "x")

    def testNSDecls(self):
        """checkNSDecls"""
        #Not using genxSetUserData
        fp = get_file_pointer()
        self.writer.startDocFile(fp)

        self.writer.startElement(self.ela)
        self.writer.startElement(self.elb)
        self.writer.endElement()
        self.writer.startElement(self.ela)
        self.writer.addAttribute(self.a3, "x")
        self.writer.endElement()
        self.writer.endElement()
        self.writer.endDocument()

        output = read_file_pointer(fp)

        self.assertEquals(output, "<a><g1:b xmlns:g1=\"http://example.com/1\"></g1:b><a xmlns:g1=\"http://example.com/1\" g1:a3=\"x\"></a></a>")

    #Omitting checkAllocator, don't think it's really relevant in a python context
    #def testAllocator(self):
    #    """checkAllocator"""
    #    pass

    def testGoodAttrVals(self):
        """goodAttrVals"""
        t1 = "\x26\xd0\x96\xe4\xb8\xad\xf0\x90\x8d\x86"
        t2 = ' < > \x0d " '

        fp = get_file_pointer()
        self.writer.startDocFile(fp)

        self.writer.startElement(self.ela)
        self.writer.addAttribute(self.a1, t1)
        self.writer.endElement()
        self.writer.endDocument()

        fp = get_file_pointer()
        self.writer.startDocFile(fp)

        self.writer.startElement(self.ela)
        self.writer.addAttribute(self.a1, t2)
        self.writer.endElement()
        self.writer.endDocument()

        output = read_file_pointer(fp)
        self.assertEquals(output, "<a a1=\" &lt; > &#xD; &quot; \"></a>")

    def testBadAttrVals(self):
        """checkBadAttrVals"""
        t2 = "<a>\x01"
        bad_utf8s = [
            "\xc0\xaf",
            "\xc2\x7f",
            "\x80\x80",
            "\x80\x9f",
            "\xe1\x7f",
            "\xe1\x80",
            "\xe1\x80\x7f"
        ]

        fp = get_file_pointer()
        self.writer.startDocFile(fp)
        self.writer.startElement(self.ela)
        self.assertRaises(genx.NonXMLCharacterError, self.writer.addAttribute, self.a1, t2)

        for bad_utf8 in bad_utf8s:
            writer = genx.Writer()
            fp = get_file_pointer()
            writer.startDocFile(fp)
            ela = writer.declareElement("a")
            a = writer.declareAttribute("a")
            writer.startElement(ela)
            self.assertRaises(genx.BadUTF8Error, writer.addAttribute, a, bad_utf8)

    def testAddChar(self):
        """checkAddChar"""
        expected = "&amp;\xd0\x96\xe4\xb8\xad\xf0\x90\x8d\x86"
        #Not quite sure about this string, omitting test 'till I figure
        #out what it is.
        input = "\x26\416"
        #TODO write the test :)

    def testAddText(self):
        """checkAddText"""
        raw_input = "&\xd0\x96\xe4\xb8\xad\xf0\x90\x8d\x86"
        input = raw_input.decode("UTF-8")
        raw_expected = "<greeting>&amp;\xd0\x96\xe4\xb8\xad\xf0\x90\x8d\x86</greeting>"
        expected = raw_expected.decode("UTF-8")
        raw_t2 = ' < > \x0d " '
        t2 = raw_t2.decode("UTF-8")
        
        writer = genx.Writer()
        greeting = writer.declareElement("greeting")
        fp = get_file_pointer()
        writer.startDocFile(fp)
        writer.startElement(greeting)
        writer.addText(input)
        writer.endElement()
        writer.endDocument()
        output = read_file_pointer(fp)
        self.assertEquals(output, expected)

        writer = genx.Writer()
        fp = get_file_pointer()
        writer.startDocFile(fp)
        greeting = writer.declareElement("greeting")
        writer.startElement(greeting)
        writer.addText(t2)
        writer.endElement()
        writer.endDocument()
        output = read_file_pointer(fp)
        self.assertEquals(output, '<greeting> &lt; &gt; &#xD; " </greeting>')
        
        #Omitting the excess buffer tests

    def testComment(self):
        """checkComment"""
        greeting = self.writer.declareElement("greeting")
        fp = get_file_pointer()
        self.writer.startDocFile(fp)

        self.writer.comment("1")
        self.writer.startElement(greeting)
        self.writer.comment("2")
        self.writer.addText("[1]")
        self.writer.comment("3")
        self.writer.addText("[2]")
        self.writer.endElement()
        self.writer.comment("4")
        self.writer.endDocument()

        output = read_file_pointer(fp)
        self.assertEquals(output, "<!--1-->\n<greeting><!--2-->[1]<!--3-->[2]</greeting>\n<!--4-->")

    def testPI(self):
        """checkPI"""
        greeting = self.writer.declareElement("greeting")
        fp = get_file_pointer()
        self.writer.startDocFile(fp)
        
        self.writer.PI("pi1", "1")
        self.writer.startElement(greeting)
        self.writer.PI("pi2", "2")
        self.writer.addText("[1]")
        self.writer.PI("pi3", "3")
        self.writer.addText("[2]")
        self.writer.endElement()
        self.writer.PI("pi4", "4")
        self.writer.endDocument()

        output = read_file_pointer(fp)

        self.assertEquals(output, "<?pi1 1?>\n<greeting><?pi2 2?>[1]<?pi3 3?>[2]</greeting>\n<?pi4 4?>")

        fp = get_file_pointer()
        writer = genx.Writer()
        writer.startDocFile(fp)
        self.assertRaises(genx.MalformedPIError, writer.PI, "pi5", "foo?>bar")

    def testHelloLiteral(self):
        """checkHelloLiteral"""
        ns = self.writer.declareNamespace("foo:bar", "baz")

        fp = get_file_pointer()

        self.writer.startDocFile(fp)

        #Hmm, is swapping the namespace and name confusing?
        self.writer.startElementLiteral("greeting", "foo:bar")
        self.writer.addText("Hello world!")
        self.writer.endElement()
        self.writer.endDocument()

        output = read_file_pointer(fp)

        self.assertEquals(output, "<baz:greeting xmlns:baz=\"foo:bar\">Hello world!</baz:greeting>")


    def testStress(self):
        """checkStress"""
        fp = get_file_pointer()
        self.writer.startDocFile(fp)

        self.writer.startElementLiteral("root")

        random_range_end = (2**31) -1
        for i in range(1, 100):
            if (i % 3) == 0:
                self.writer.endElement()
            nname = "n%d" % (random.randint(1, random_range_end) % 10000)
            ename = "e%d" % (random.randint(1, random_range_end) % 10000)
            self.writer.startElementLiteral(ename, nname)
            acount = random.randint(1, random_range_end) % 20
            for j in range(0, acount):
                alength = random.randint(1, random_range_end) % 10000
                #Using list as a quick optimization, force of habit, slightly cleaner
                avchar= chr(ord('A') + (random.randint(1, random_range_end) % 40))
                aval_list = []
                for k in range (0, alength):
                    aval_list.append(avchar)
                nname = "n%d" % (random.randint(1, random_range_end) % 10000)
                ename = "e%d" % (random.randint(1, random_range_end) % 10000)
                try:
                    self.writer.addAttributeLiteral(ename, nname, "".join(aval_list))
                except genx.DuplicateAttributeError:
                    pass
            self.writer.addText("\n")
        #unwind the elements, using nasty exception catching
        while True:
            try:
                self.writer.endElement()
            except genx.SequenceError:
                break

        self.writer.endDocument()

    def testUTF8(self):
        """Ensures UTF-8 text works"""
        fp = get_file_pointer()
        self.writer.startDocFile(fp)
        #TODO: I want to use unicode here, but genx doesn't like that, is this correct?
        tag = u"unicodetext"
        sample_string = u"Hello. Euro: \u20ac. Hebrew he: \u05d4. Arabic dad: \u0636."

        self.writer.startElementLiteral(tag)
        self.writer.addText(sample_string)
        self.writer.endElement()
        self.writer.endDocument()

        output = read_file_pointer(fp)
        self.assertEquals(output, u"<%s>%s</%s>" % (tag, sample_string, tag))

    def testVersion(self):
        """Make sure the __version__ variable is set properly"""
        self.assertNotEquals(genx.__version__, "@@version@@")
        self.assertNotEquals(genx._genx.__version__, "@@version@@")

    def testStringIO(self):
        """Test using StringIO with the callback mechanism"""
        writer = genx.Writer()
        import StringIO
        fp = StringIO.StringIO()
        writer.startDocFile(fp) 
        writer.startElementLiteral("foo")
        writer.addText("bar")
        writer.endElement()
        writer.endDocument()
        fp.seek(0)
        self.assertEquals("<foo>bar</foo>", fp.read())

    def testAddTextNone(self):
        """Test what happens when None is passed in"""
        fp = get_file_pointer()
        self.writer.startDocFile(fp)
        self.assertRaises(genx.BadUTF8Error, self.writer.startElementLiteral, None)
        self.assertRaises(genx.BadUTF8Error, self.writer.addText, None)
        self.assertRaises(genx.BadUTF8Error, self.writer.PI, None, None)
        self.assertRaises(genx.BadUTF8Error, self.writer.PI, "foo", None)
        self.assertRaises(genx.BadUTF8Error, self.writer.comment, None)
        self.assertRaises(genx.BadUTF8Error, self.writer.declareElement, None)
        self.assertRaises(genx.BadNamespaceNameError, self.writer.declareNamespace, None)
        self.assertRaises(genx.BadUTF8Error, self.writer.declareAttribute, None)

if __name__ == "__main__":
    unittest.main()

#arch-tag: main python unittests

