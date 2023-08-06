import unittest

import nose.tools
from lxml import objectify

class TestTransform(unittest.TestCase):

    def setUp(self):
        """Create an instance of Html2DocBook
        """
        from html2docbook import Html2DocBook
        h2d = Html2DocBook()
        self.h2d = h2d

    def tearDown(self):
        pass

    def test_paragraphs(self):
        """Transform HTML '<p>' paragraph to DocBook '<para>' paragraph
        """
        html = '<p>lorem</p><p>ipsum</p>'
        expect = '<section><para>lorem</para><para>ipsum</para></section>'
        xml = self.h2d.transform(html)
        self.assertEquals(xml, expect)

    def test_headline_h2(self):
        """Transform HTML '<h2>' headline to DocBook '<bridgehead role="headline">'
        """
        html = '<h2>What Makes Mainstream Media Mainstream</h2>'
        expect = '<section><bridgehead role="headline">What Makes Mainstream Media Mainstream</bridgehead></section>'
        xml = self.h2d.transform(html)
        self.assertEquals(xml, expect)

        html = '<h2>What Makes Mainstream Media Mainstream<br /></h2>'
        expect = '<section><bridgehead role="headline">What Makes Mainstream Media Mainstream</bridgehead></section>'
        xml = self.h2d.transform(html)
        self.assertEquals(xml, expect)

    def test_headline_h3(self):
        """Transform HTML '<h3>' headline to DocBook '<bridgehead role="subheadline">'
        """
        html = '<h3>What Makes Mainstream Media Mainstream</h3>'
        expect = '<section><bridgehead role="subheadline">What Makes Mainstream Media Mainstream</bridgehead></section>'
        xml = self.h2d.transform(html)
        self.assertEquals(xml, expect)

    def test_headline_h4(self):
        """Transform HTML '<h4>' headline to DocBook '<bridgehead role="question">'
        """
        html = '<h4>What makes mainstream media mainstream?</h4>'
        expect = '<section><bridgehead role="question">What makes mainstream media mainstream?</bridgehead></section>'
        xml = self.h2d.transform(html)
        self.assertEquals(xml, expect)

    def test_blockquote(self):
        """Transform HTML '<blockquote>' to DocBook '<blockquote>'
        """
        html = '<blockquote><p>Colorless green ideas sleep furiously</p></blockquote>'
        xml = self.h2d.transform(html)
        expect = '<section><blockquote><para>Colorless green ideas sleep furiously</para></blockquote></section>'
        self.assertEquals(xml, expect)

#    def test_strip_whitespace(self):
#        """Strip whitespace
#        """
#        html = '<p> lorem ipsum </p>'
#        expect = '<section><para>lorem ipsum</para></section>'
#        xml = self.h2d.transform(html)
#        self.assertEquals(xml, expect)

    def test_german_umlaute(self):
        """Transform HTML german Umlaute
        """
        html = '<p>öüä or ÄÜÖ are german Umlaute</p>'
        expect = '<section><para>&#246;&#252;&#228; or &#196;&#220;&#214; are german Umlaute</para></section>'
        xml = self.h2d.transform(html)
        self.assertEquals(xml, expect)

    def test_html_entities(self):
        """Transform HTML entities
        """
        html = '<p>Some & funny &lt; characters</p>'
        expect = '<section><para>Some &amp; funny &lt; characters</para></section>'
        xml = self.h2d.transform(html)
        self.assertEquals(xml, expect)

    def test_html_blankspace(self):
        """Transform HTML '&nbsp' to DocBook '&#160;' blankspace
        """
        html = '<p>lorem&nbsp;impsum</p>'
        expect = '<section><para>lorem&#160;impsum</para></section>'
        xml = self.h2d.transform(html)
        self.assertEquals(xml, expect)

    def test_html_emphasis(self):
        """Transform HTML '<em>' and '<i>' to DocBook '<emphasis>'
        """
        html = '<p>lorem <em>ipsum</em></p>'
        expect = '<section><para>lorem <emphasis>ipsum</emphasis></para></section>'
        xml = self.h2d.transform(html)
        self.assertEquals(xml, expect)

        html = '<p>lorem <i>ipsum</i></p>'
        expect = '<section><para>lorem <emphasis>ipsum</emphasis></para></section>'
        xml = self.h2d.transform(html)
        self.assertEquals(xml, expect)

    def test_html_underline(self):
        """Transform HTML '<b>' into DocBook '<citetitle>'
        """
        html = '<p>lorem <u>ipsum</u></p>'
        expect = '<section><para>lorem <citetitle>ipsum</citetitle></para></section>'
        xml = self.h2d.transform(html)
        self.assertEquals(xml, expect)

    def test_html_bold(self):
        """Transform HTML '<b>' to DocBook '<emphasis role="bold">'
        """

        html = '<p>lorem <b>ipsum</b></p>'
        expect = '<section><para>lorem <emphasis role="bold">ipsum</emphasis></para></section>'
        xml = self.h2d.transform(html)
        self.assertEquals(xml, expect)


    def test_hyperlinks(self):
        """Transform hyperlinks
        """
        html = '<a href="http://www.zmag.de">ZNet</a>'
        expect = '<section><ulink url="http://www.zmag.de">ZNet</ulink></section>'
        xml = self.h2d.transform(html)
        self.assertEquals(xml, expect)