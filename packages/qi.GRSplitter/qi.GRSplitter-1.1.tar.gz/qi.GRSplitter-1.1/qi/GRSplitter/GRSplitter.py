"""
GRSplitter - Greek word splitter for ZCTextIndex

(C) G. Gozadinoso
http://qiweb.net
ggozad _at_ qiweb.net
License: see LICENSE.txt

"""

from Products.ZCTextIndex.ISplitter import ISplitter
from Products.ZCTextIndex.PipelineFactory import element_factory

import re
from types import StringType

def getSupportedEncoding(encodings):
	return 'utf-8'

# GR charsets ranges, see this following pages:
#
# http://jrgraphix.net/research/unicode_blocks.php?block=7

rxNormal = re.compile(u"[a-zA-Z0-9_]+|[\u0370-\u03ff]+", re.UNICODE)
rxGlob = re.compile(u"[a-zA-Z0-9_]+[*?]*|[\u0370-\u03ff]+[*?]*", re.UNICODE)

class GRSplitter:

	default_encoding = "utf-8"

	#Greek accents dictionary

	accDict = {u'\u03ac':u'\u03b1', #alpha
			   u'\u0386':u'\u0391', #capital alpha
			   u'\u03ad':u'\u03b5', #epsilon
			   u'\u0388':u'\u0395', #capital epsilon
			   u'\u03ae':u'\u03b7', #eta
			   u'\u0389':u'\u0397', #capital eta
			   u'\u03af':u'\u03b9', #iota
			   u'\u03ca':u'\u03b9', #iota dial
			   u'\u0390':u'\u03b9', #iota dial + accent
			   u'\u038a':u'\u0399', #capital iotal
			   u'\u03aa':u'\u0399', #capital iota dial
			   u'\u03cc':u'\u03bf', #omicron
			   u'\u038c':u'\u039f', #capital omicron
			   u'\u03cd':u'\u03c5', #ipsilon
			   u'\u03cb':u'\u03c5', #ipsilon dial
			   u'\u03b0':u'\u03c5', #ipsilon dial+accent
			   u'\u038e':u'\u03a5', #capital ipsilon 
			   u'\u03ab':u'\u03a5', #capital ipsilon +dial
			   u'\u03ce':u'\u03c9', #omega
			   u'\u038f':u'\u03a9'	#capital omega
			   }

	def process(self, lst, isGlob=0):
		result = []
		if isGlob:
		  rx = rxGlob
		else:
		  rx = rxNormal
		for s in lst:
			if type(s) is StringType: # not unicode
				s = unicode(s, self.default_encoding, 'replace')
			deaccented = self.accent_replace(s)
			splitted = rx.findall(deaccented)
			for w in splitted:
				result.append(w)
		return result

	def processGlob(self, lst):
		return self.process(lst, 1)

	def accent_replace(self,text):
		rx = re.compile('|'.join(map(re.escape,self.accDict)))
		def one_xlat(match):
			return self.accDict[match.group(0)]
		return rx.sub(one_xlat,text)