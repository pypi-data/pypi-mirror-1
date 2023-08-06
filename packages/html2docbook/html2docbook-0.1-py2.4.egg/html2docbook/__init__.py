import os
import sys
import re

from htmlentitydefs import name2codepoint
from lxml import etree
from BeautifulSoup import BeautifulSoup

_debug=False

class Html2DocBook(object):
    """Transform HTML to DocBook XML.
    """

    def __init__(self, cleanup=False, verbose=False):
        self.cleanup = cleanup
        self.verbose = verbose

        # make the XSL stylesheet available
        xsl_html2docbook = os.path.abspath(os.path.join(os.path.dirname(__file__), 'html2docbook.xsl'))
        if not os.path.exists(xsl_html2docbook):
            raise IOError('%s does not exist' % xsl_html2docbook)

        self.xsl_html2docbook = xsl_html2docbook

    def handler(self, mo):
        """Replace all HTML entities with the corresponding numeric entities.
        """
        e = mo.group(1)
        v = e[1:-1]
        if not v.startswith('#'):
            codepoint =  name2codepoint.get(v)
            return codepoint and '&#%d;' % codepoint or ''
        else:
            return e

    def transform(self, html):
        """Transform the HTML input into DocBook XML.
        """

        # BeautifulSoup needs a complete HTML document as input.
        # So wrap an html and body tag around the input.
        html = "<html><body>%s</body></html>" % html

        if _debug:
            print "HTML Input:\n%s" % html

        # !!! HACK HACK HACK !!!
        html = html.replace(' & ', ' &amp; ')

        if _debug:
            print "HTML & Replace:\n%s" % html

        # Use BeautifulSoup for performing HTML checks
        # and the conversion to XHTML.
        soup = BeautifulSoup(html)

        # check if all image files exist
        for img in soup.findAll('img'):
            src = img['src']
            if not os.path.exists(src):
                raise IOError('No image file found: %s' % src)

        # do not prettify, remove all whitespace
        html = str(soup)

        if _debug:
            print "Beautiful Soup:\n%s" % html

        # replace all HTML entities
        entity_reg = re.compile('(&.*?;)')
        html = entity_reg.sub(self.handler, html)

        if _debug:
            print "Replace HTML entities:\n%s" % html

        # try to transform inputfn
        try:
            # xml -> elementtree
            # try to recover if not valid html, remove blanks between two tags
            parser = etree.XMLParser(recover=True, remove_blank_text=True)
            htmltree = etree.XML(html, parser)

            # parse the xslt stylesheet
            styletree = etree.parse(self.xsl_html2docbook)

            # load the xslt stylesheet
            transform = etree.XSLT(styletree)

            # transform the html tree
            resulttree = transform(htmltree)

            if _debug:
                print "DocBook:\n%s" % etree.tostring(resulttree)

            # strip whitespace inside two tags, e.g. <p> lorem ipsum </p> => <p>lorem ipsum</p>
            for element in resulttree.iter("*"):
                if element.text is not None and not element.text.strip():
                    element.text = None

            if _debug:
                print "DocBook after striping inner whitespace:\n%s" % etree.tostring(resulttree)

            docbook = etree.tostring(resulttree)

        except:
            print >>sys.stderr, 'Error transforming %s' % (html)
            raise

        return docbook