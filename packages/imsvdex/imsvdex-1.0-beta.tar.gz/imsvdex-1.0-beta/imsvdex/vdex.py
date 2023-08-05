# File: vdex.py
#
# Copyright (c) 2007 by Martin Raspe
# Bibliotheca Hertziana (Max-Planck-Institute for Art History), Rome, Italy
# This code was written for the ZUCCARO Project
# see http://zuccaro.biblhertz.it
#
# German Free Software License (D-FSL)
#
# This Program may be used by anyone in accordance with the terms of the 
# German Free Software License
# The License may be obtained under <http://www.d-fsl.org>.

#

__author__ = 'Martin Raspe'
__docformat__ = 'plaintext'

import string
from types import StringTypes
from StringIO import StringIO

from xml.parsers.expat import ExpatError
from elementtreewriter.xmlwriter import XMLWriter
from _odict import OrderedDict

try:
    from celementtree.ElementTree import ElementTree
except ImportError:
    from elementtree.ElementTree import ElementTree
# from xml.dom.xmlbuilder import DOMBuilder, DOMInputSource

VDEX_FLAT_PROFILE_TYPES = ('thesaurus', 'glossaryOrDictionary', 'flatTokenTerms')
TRUE_VALUES = ('1', 'true', 'True', 'yes', 'Yes')
FALSE_VALUES = ('', '0', 'false', 'False', 'no', 'No')

class VDEXError(Exception):
    """
    Denotes an error while handling an IMS-VDEX vocabulary with a VDEXManager
    """

class VDEXManager(object):
    """
	Reads an IMS-VDEX vocabulary and constructs a VocabularyDict for ArcheTypes.
	  See "IMS Vocabulary Definition Exchange": http://www.imsglobal.org/vdex/.
      XML binding: http://www.imsglobal.org/vdex/vdexv1p0/imsvdex_bindv1p0.html
      Not yet supported:
          term/mediadescriptor elements
          relationship elements
    """

    vdex_namespace = 'http://www.imsglobal.org/xsd/imsvdex_v1p0'
    default_language = 'en'
    unnamed_term = '(unnamed term)'
    fallback_to_default_language = False
    order_significant = False
    term_dict = {}

    def __init__(self, file=None, lang=None, namespace=None, fallback=None):
        """
        constructs a VDEX manager and parses a XML vocabulary
		file: a file or string that is parsed
		lang: set the default language for output ('*' for multilingual terms) 
        namespace: declares the IMS-VDEX namespace in the vocab file
		  ('' handles VDEX files without any declared namespace).
        fallback: if no translation is found for the given language
          should the term be returned in the default language
          or as self.unnamed_term ?
        """
        if lang is not None:
            self.default_language = lang
        if namespace is not None:
            self.vdex_namespace = namespace
        if fallback is not None:
            self.fallback_to_default_language = fallback
        if file is not None:
            self.parse(file)

    def isVDEX(self):
        """
        checks if the parsed XML seems to be a valid VDEX vocabulary
        """
        # this method does not perform a complete schema validation
		# it just checks for a root element named 'vdex' in the expected  namespace
        return self.tree._root.tag == self.vdexTag('vdex')

    def parse(self, file):
        """
        parses a VDEX vocabulary file or XML string
        """
        if isinstance(file, StringTypes):
            file = StringIO(file)
        #        dom = DOMBuilder();
        #        input = DOMInputSource()
        #        input._set_byteStream(file)
        #        self.tree = dom.parse(input)
        try:
            self.tree = ElementTree(None, file)
        except ExpatError, e:
            raise VDEXError, 'Parse error in vocabulary XML: %s' % e
        try:
            filename = file.name
        except AttributeError:
            filename = 'parsed XML text'
        if not self.isVDEX():
            raise VDEXError, 'Vocabulary format not correct in %s' % filename
        self.order_significant = self.isOrderSignificant()
        self.makeTermDict()
        return self.tree

    def serialize(self, file=None):
        """
        returns the vocabulary as XML
        """
        writer = XMLWriter(self.tree)
        return writer(file)

    def getVocabIdentifier(self):
        """
        returns the vocabulary identifier
        """
        xpath = self.vdexTag('vocabIdentifier')
        return self.tree.findtext(xpath)

    def getVocabName(self, lang=None):
        """
        returns the vocabulary name in the given (or default) language.
        If lang is '*', returns a dict of all translations keyed by language
        """
        xpath = '%s/%s' % (self.vdexTag('vocabName'), self.vdexTag('langstring'))
        captions = self.tree.findall(xpath)
        return self.getLangstring(captions, lang, default='(unnamed vocabulary)')

    def getVocabMetadata(self):
        """
        returns the VDEX metadata element(s) for the Vocabulary
        """
        xpath = self.vdexTag('metadata')
        return self.tree._root.findall(xpath)

    def getVocabWildcard(self, foreign_ns, tagname):
        """
        returns 'wildcard' element(s) (with a foreign namespace) for the Vocabulary
        """
        xpath = self.nsTag(foreign_ns, tagname)
        return self.tree._root.findall(xpath)

    def isFlat(self):
        """
        returns true if the VDEX profile type denotes a flat vocabulary
        """ 
        vdex = self.tree._root
        return vdex.get('profileType') in VDEX_FLAT_PROFILE_TYPES

    def isOrderSignificant(self):
        """
        returns true if the order of the VDEX vocabulary is significant
        """ 
        vdex = self.tree._root
        return vdex.get('orderSignificant') not in FALSE_VALUES

    def showLeafsOnly(self):
        """
        this is not declared in VDEX vocabs, so we return false
        """
        return false

    def getVocabularyDict(self, lang=None):
        """
        returns a vocabulary dictionary (for ArcheTypes) in the given language.
        If lang is '*', returns dicts of all translations keyed by language
        """
        return self.getTerms(self.tree._root, lang)

    def getTerms(self, element, lang=None):
        """
        get all term elements recursively
          returns a hierarchic dictionary structure of the vocabulary
        """
        xpath = self.vdexTag('term')
        terms = element.findall(xpath)
        if len(terms) == 0:
            return None
        # we should not only test order significance globally, but also for every term
        if self.order_significant:
            result = OrderedDict()
        else:
            result = {}
        for term in terms:
            key = self.getTermIdentifier(term)
            value = self.getTermCaption(term, lang)
            result[key] = (value, self.getTerms(term, lang))
        return result

    def getTermIdentifier(self, term):
        """
        returns the termIdentifier for a given term element
        """
        xpath = self.vdexTag('termIdentifier')
        return term.findtext(xpath)

    def getTermCaption(self, term, lang=None):
        """
        returns the translated caption for a term
          for lang == "*" the method returns a dictionary with all translations 
          keyed by language
        """
        if term is None:
            return None
        xpath = '%s/%s' % (self.vdexTag('caption'), self.vdexTag('langstring'))
        captions = term.findall(xpath)
        return self.getLangstring(captions, lang)

    def getTermDescription(self, term, lang=None):
        """
        returns the translated description for a term
          for lang == "*" the method returns a dictionary with all translations 
          keyed by language
        """
        if term is None:
            return None
        xpath = '%s/%s' % (self.vdexTag('description'), self.vdexTag('langstring'))
        descriptions = term.findall(xpath)
        return self.getLangstring(descriptions, lang, default='')

    def getLangstring(self, elements, lang=None, default=None):
        """
        returns the langstring in the given language.
        for lang == "*" the method returns a dictionary with all translations 
        keyed by language
        """
        if lang == '*':
            return self.getAllLangstrings(elements)
        if lang is None:
            lang = self.default_language
        if default is None:
            default = self.unnamed_term
        result = None
        for element in elements:
            if element.get('language') == lang:
                result = element.text
            if self.fallback_to_default_language:
               if element.get('language') == self.default_language:
                    default = element.text
        if result is None:
            result = default
        return result

    def getAllLangstrings(self, elements):
        """
        returns a dictionary with all translations keyed by language
        """
        result = {}
        for element in elements:
            result[element.get('language')] = element.text
        return result

    def getTermById(self, identifier):
        """
        returns the VDEX term element for a given term identifier
        """
        return self.term_dict.get(identifier, None)

    def getTermCaptionById(self, identifier, lang=None):
        """
        returns the caption(s) for a given term identifier
        """
        term = self.getTermById(identifier)
        return self.getTermCaption(term, lang)

    def getTermDescriptionById(self, identifier, lang=None):
        """
        returns the description(s) for a given term identifier
        """
        term = self.getTermById(identifier)
        return self.getTermDescription(term, lang)

    def getTermMetadataById(self, identifier):
        """
        returns the VDEX metadata element(s) inside a term
          for a given term identifier
        """
        term = self.getTermById(identifier)
        xpath = self.vdexTag('metadata')
        return term.findall(xpath)

    def getTermWildcardById(self, identifier, namespace, tagname):
        """
        returns 'wildcard' element(s) (with a foreign namespace)
          inside a term for a given term identifier
        """
        term = self.getTermById(identifier)
        xpath = self.nsTag(namespace, tagname)
        return term.findall(xpath)

    def getTagname(self, nsname):
	    # not needed here
        if not nsname[:1] == "{":
            return nsname
        namespace_uri, tagname = string.split(name[1:], "}", 1)
        return tagname

    def nsTag(self, namespace, tagname):
        """
        returns a tag with a namespace of the form '{namespace_uri}tagname'
          or just the tag name if an empty namespace was given
        """
        if namespace == '':
            return tagname
        else:
            return '{%s}%s' % (namespace, tagname)

    def vdexTag(self, tagname):
        """
        returns a tag with the VDEX namespace or just the tag name
          if the VDEX namespace is the empty string
        """
        return self.nsTag(self.vdex_namespace, tagname)

    def makeTermDict(self):
        """
        constructs a flat dictionary of term elements, keyed by termIdentifier 
        """
        # the .// prefix finds all items recursively
        xpath = './/' + self.vdexTag('term')
        terms = self.tree._root.findall(xpath)
        self.term_dict = {}
        for term in terms:
            key = self.getTermIdentifier(term)
            self.term_dict[key] = term

if __name__ == '__main__':
    import doctest
    import unittest
    
    suite = doctest.DocFileSuite(
            'vdex.txt',
            optionflags=doctest.ELLIPSIS + doctest.REPORT_ONLY_FIRST_FAILURE)
            
    unittest.TextTestRunner().run(suite)

