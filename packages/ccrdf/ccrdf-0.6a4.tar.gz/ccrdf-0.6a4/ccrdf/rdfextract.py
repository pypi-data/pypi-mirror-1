"""
rdfextract.py

A pluggable class for extracting RDF from blocks of text.  By default uses
a simple regex for finding RDF; can be extended with any number of other
function for specialized processing.

(c) 2004, Nathan R. Yergler
Licensed under the GNU GPL2
"""

__id__ = "$Id: rdfextract.py 5341 2007-02-16 15:07:34Z nyergler $"
__version__ = "$Revision: 5341 $"
__copyright__ = '(c) 2004, Nathan R. Yergler'
__license__ = 'licensed under the GNU GPL2'

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO
    
import urllib2
import urlparse
import re
import sets

import pkg_resources

import rdfdict

def null_extractor(text, url):
    """This is a sample extractor with no functionality; it exists in the
    source for the purpose of documenting the extractor function signature.

    An extractor function takes a single parameter, text, and returns a list
    of RDF blocks extracted from the text.  If no RDF is found, an empty
    list should be returned.
    """
    return []

def string_extractor(text, url):
    """
    Extracts RDF segments from a block of text using simple string
    methods; for fallback only.
    """

    START_TAG = '<rdf:rdf'
    END_TAG = '</rdf:rdf>'

    lower_text = text.lower()

    matches = []
    startpos = 0

    startpos = lower_text.find(START_TAG, startpos)
    while startpos > -1:
      endpos = lower_text.find(END_TAG, startpos)
      
      if endpos > -1:
         matches.append(text[startpos:endpos+len(END_TAG)])

      startpos = lower_text.find(START_TAG, endpos)

    return matches

def regex_extractor(text, url):
    """
    Extracts RDF segments from a textblock; returns a list of strings.
    """
    # compile the RegEx for extracting RDF
    rdf_regex = re.compile("<rdf:rdf.*?>.*?</rdf:rdf>",
                           re.IGNORECASE|re.DOTALL|re.MULTILINE)

    # extract the RDF bits from the incoming text
    matches = []
    text = text.strip()

    try:
       return rdf_regex.findall(text)
    except:
       return []

def link_extractor(text, url):
    """Extracts metadata stored in linked files specified by
    <link rel="meta" ...> as in:
    <link rel="meta" type="application/rdf+xml"
    href="/en/wiki/wiki.phtml?title=Main_Page&action=creativecommons">
    """

    results = []
    
    # extract the list of link tags
    link_regex = re.compile("<link .*?>",
                           re.IGNORECASE|re.DOTALL|re.MULTILINE)
    rel_regex = re.compile('rel="meta"',
                           re.IGNORECASE|re.DOTALL|re.MULTILINE)
    href_regex = re.compile('(href=["\'])(.*?)(["\'])',
                            re.IGNORECASE)
    
    # extract the RDF bits from the incoming text
    matches = []
    text = text.strip()

    links = link_regex.findall(text)

    # check if each link has the correct relationship
    for link in links:
        isrel = rel_regex.search(link)
        if isrel:
            # extract the href
            href = href_regex.search(link)
            if href:
                rdf_href = urlparse.urljoin(url, href.group(2))

		# handle possible HTML escaping
		rdf_href = rdf_href.replace('&amp;', '&')

                # retrieve the href and check for RDF
                results = results + \
                          RdfExtractor().extractRdfText(
                    retrieveUrl(rdf_href), url=rdf_href)
    
    return results

# ------------------------------------------------------------------

class RdfExtractor(object):
    """A pluggable class for extracting RDF from blocks of text."""

    @property
    def extractors(self):
        """Return a sequence of extractors which operate by returning
        blocks of plain text.

        Plain-text extractors are callables which take two parameters:

        * a block of text to operate on
        * the URL the text was retrieved from (for use when rdf:about='')

        Plain-text extractors must return a sequence of string objects,
        where each element in the sequence is a valid chunk of RDF.
        """

        return [e.load() for e in
                pkg_resources.iter_entry_points('ccrdf.extract_text')]

    @property
    def graph_extractors(self):
        """Return a sequence of extractors which operate by adding assertions
        to an RDF Graph.

        Graph extractors are callables which take three parameters:

        * a block of text to operate on
        * the URL the text was retrieved from (for use when rdf:about='')
        * the RDF Graph object to add the assertions to.

        Store extractors do not need to return a value.
        """
        
        return [e.load() for e in
                pkg_resources.iter_entry_points('ccrdf.extract_to_graph')]
        
    def extractRdfText(self, textblock, url=None):
        """Pass textblock through each extractor in sequence and return
        a list of RDF blocks extracted."""
        
        rdf_blocks = []
        
        for func in self.extractors:
            rdf_blocks = rdf_blocks + func(textblock, url)

        result = list(sets.Set([n.strip() for n in rdf_blocks]))
        
        return result

    def extractRdf(self, textblock, url=None):
        """Pass textblock through each extractor in sequence and return
        a list of rdfStore objects."""

        rdf_blocks = self.extractRdfText(textblock, url)

        for block in rdf_blocks:
            store = rdfdict.rdfStore()
            store.parse(block)

            yield store

    def extractUrlToGraph(self, url, rdf_graph):

        rdf_blocks = self.extractRdfText(retrieveUrl(url), url)

        for block in rdf_blocks:
            rdf_graph.parse(StringIO(block))

        for extractor in self.graph_extractors:
            extractor(retrieveUrl(url), url, rdf_graph)

# ------------------------------------------------------------------
# convenience functions

def retrieveUrl(url):
    """Returns the document contained at [url]."""
    
    headers = {'User-Agent':'ccRdf/Python'}
    request = urllib2.Request(url, headers=headers)
    
    resource = urllib2.urlopen(request)

    result =  "".join(resource.readlines())
    return result


    
