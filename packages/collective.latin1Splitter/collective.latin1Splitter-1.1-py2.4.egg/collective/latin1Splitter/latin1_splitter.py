"""
Latin1 Splitter - Latin1 word splitter for ZCTextIndex
"""

from Products.ZCTextIndex.ISplitter import ISplitter
from Products.ZCTextIndex.PipelineFactory import element_factory

import re
from types import StringType

def getSupportedEncoding(encodings):
  return 'utf-8'

# Basic latin charsets ranges, see this following pages:
#
# http://jrgraphix.net/research/unicode_blocks.php?block=1

rxNormal = re.compile(u"[a-zA-Z0-9_]+|[\\uc0-\\uff]+", re.UNICODE)
rxGlob = re.compile(u"[a-zA-Z0-9_]+[*?]*|[\\uc0-\\uff]+[*?]*", re.UNICODE)

class Latin1Splitter:

  default_encoding = "utf-8"

  #Latin1 (not complete) accents dictionary

  accDict = {u'\xC0':u'\x41', #À
             u'\xC1':u'\x41', #Á
             u'\xC2':u'\x41', #Â
             u'\xC3':u'\x41', #Ã
             u'\xC4':u'\x41', #Ä
             u'\xC5':u'\x41', #Å
             u'\xC6':u'\x41\x45', #Æ
             u'\xE0':u'\x61', #à
             u'\xC2':u'\x61', #á
             u'\xC3':u'\x61', #â
             u'\xC4':u'\x61', #ã
             u'\xC5':u'\x61', #ä
             u'\xC6':u'\x61', #ä
             u'\xC6':u'\x61', #å
             u'\xC6':u'\x61\x65', #æ
             
             u'\xC7':u'\x43', #Ç
             u'\xE7':u'\x63', #ç
             
             u'\xC8':u'\x45', #È
             u'\xC9':u'\x45', #É
             u'\xCA':u'\x45', #Ê
             u'\xCB':u'\x45', #Ë
             u'\xE8':u'\x65', #è
             u'\xe9':u'e', #é
             u'\xEA':u'\x65', #ê
             u'\xEB':u'\x65', #ë
           
             u'\xCC':u'\x49', #Ì
             u'\xCD':u'\x49', #Í
             u'\xCE':u'\x49', #Î
             u'\xCF':u'\x49', #Ï
             u'\xEC':u'\x69', #ì
             u'\xED':u'\x69', #í
             u'\xEE':u'\x69', #î
             u'\xEF':u'\x69', #ï
    
             u'\xD9':u'\x55', #Ù
             u'\xDA':u'\x55', #Ú
             u'\xDB':u'\x55', #Û
             u'\xDC':u'\x55', #Ü
             u'\xF9':u'\x75', #ù
             u'\xFA':u'\x75', #ú
             u'\xFB':u'\x75', #û
             u'\xFC':u'\x75', #ü
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