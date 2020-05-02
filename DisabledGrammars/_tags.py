__version__ = "$Rev: 606 $ on $Date: 2019-04-23 14:30:57 +0200 (di, 23 apr 2019) $ by $Author: quintijn $"
# This file is part of a SourceForge project called "unimacro" see
# http://unimacro.SourceForge.net and http://qh.antenna.nl/unimacro
# (c) copyright 2003 see http://qh.antenna.nl/unimacro/aboutunimacro.html
#    or the file COPYRIGHT.txt in the natlink\natlink directory 
#
#  _tags.py: make HTML tags
#
# written by: Quintijn Hoogenboom (QH softwaretraining & advies)
# august 2003
#
"""grammar that makes html tags, as defined in an inifile

"""

import natlink
natqh = __import__('natlinkutilsqh')
natut = __import__('natlinkutils')
natbj = __import__('natlinkutilsbj')
from actions import doAction as action
from actions import doKeystroke as keystroke
import nsformat

language = natqh.getLanguage()        

ancestor = natbj.IniGrammar
class ThisGrammar(ancestor):
    language = natqh.getLanguage()        
    iniIgnoreGrammarLists = ['character']

    name = "tags"
    gramSpec = """
<tags> exported = (Tag | HTML Tag | <prefix> Tag | <prefix> HTML Tag )({tagname}|{character}+);
<prefix> = Open | Close | Begin | End | Empty;
    """

    def initialize(self):
        if not self.language:
            print("no valid language in grammar "+__name__+" grammar not initialized")
            return

        self.load(self.gramSpec)
        self.setCharactersList('character')        
        self.switchOnOrOff()

    def gotBegin(self,moduleInfo):
        if self.checkForChanges:
            self.checkInifile()

    def gotResultsInit(self,words,fullResults):
        self.letters = ''
        self.pleft = ''
        self.pright = ''
        self.dictated = ''
        self.onlyOpen = self.onlyClose = self.empty = 0
        
    def gotResults_tags(self,words,fullResults):
        self.letters = self.getFromInifile(words, 'tagname', noWarning=1)
        if not self.letters:
            print('_tags, no valid tagname found: %s'% words)
            return
        for w in words:
            char = self.getCharacterFromSpoken(w)
            if char:
                self.letters += char

    #def gotResults_dgndictation(self,words,fullResults):
    #    """return dictated text, put in between (or before or after the tags)
    #    """
    #    self.dictated, dummy = nsformat.formatWords(words, state=-1)  # no capping, no spacing
    #    #print '-result of nsformat: |%s|'% repr(self.dictated)
    

    def gotResults_prefix(self,words,fullResults):
        self.empty = self.hasCommon(words, ['Empty', 'Lege'])
        self.onlyOpen = self.hasCommon(words, ['Begin', 'Open'])
        self.onlyClose = self.hasCommon(words, ['Sluit', 'Close', 'End', 'Eind'])


    def gotResults(self,words,fullResults):
        tag = self.letters.strip()
##        print 'rule gotResults: %s'% tag
        pleft = pright = ""
        if not tag:
            return
        pleft = '<%s>' % tag
        if tag.find(' ') >= 0:
            endTag  = ' '.split(tag)[0]
        else:
            endTag = tag
        pright = '</%s>' % endTag

        # see of something selected, leave clipboard intact 
        natqh.saveClipboard()
        keystroke('{ctrl+x}')  # try to cut the selection
        contents = natlink.getClipboard().replace('\r','').strip()
        natqh.restoreClipboard()
        
        leftText = rightText = leftTextDict = rightTextDict = ""
        #if contents:
        #    # strip from clipboard contents:
        #    contents, leftText, rightText = self.stripFromBothSides(contents)
        #if self.dictated.strip():
        #    contents, leftTextDict, rightTextDict = self.stripFromBothSides(self.dictated)
        #elif self.dictated:
        #    # the case of only a space-bar:
        #    leftTextDict = self.dictated
        #
        #lSpacing = leftText + leftTextDict
        #rSpacing = rightTextDict + rightText
        #
        #if lSpacing:
        #    keystroke(lSpacing)
        
        keystroke(pleft)
        if contents:
            #print 'contents: |%s|'% repr(contents)
            keystroke('{ctrl+v}')
        keystroke(pright)

        #if rSpacing:
        #    keystroke(rSpacing)

        if not contents:
            # go back so you stand inside the brackets:
            nLeft = len(pright)
            keystroke('{ExtLeft %s}'% nLeft)
    #
    #
    #def stripFromBothSides(self, text):
    #    """strip whitespace from left side and from right side and return the three parts
    #    
    #    input: text
    #    output: stripped, leftSpacing, rightSpacing
    #    """
    #    leftText = rightText = ""
    #    lSpaces = len(text) - len(text.lstrip())
    #    leftText = rightText = ""
    #    if lSpaces:
    #        leftText = text[:lSpaces]
    #    text = text.lstrip()
    #    rSpaces = len(text) - len(text.rstrip())
    #    if rSpaces:
    #        rightText = text[-rSpaces:]
    #    text = text.rstrip()
    #    return text, leftText, rightText
    #


    def fillDefaultInifile(self, ini):
        """filling entries for default ini file

        """
        ancestor.fillDefaultInifile(self, ini)
        if self.language == 'nld':
            tagNames = {
                'Hedder 1':  'h1',
                'Hedder 2':  'h2',
                'Hedder 3':  'h3',
                'tabel':  'table',
                'tabel honderd procent':  'table border="0" cellpadding="0" cellspacing="0" width="100%"',
                'tabel data':  'td',
                'tabel roo':  'tr',
                'Java script':  'script language="JavaScript"', 
                'script':  'script'
            }
            
        elif self.language == 'enx':
            tagNames = {
                'Header 1':  'h1',
                'Header 2':  'h2',
                'Header 3':  'h3',
                'table':  'table',
                'table data':  'td',
                'table row':  'tr',
                'Java script':  'script language="JavaScript"', 
                'script':  'script'
            }
        else:
            print('-----filling ini file %s , invalid language: "%s"! '% \
                  (self.__module__, self.language))
            ini.set('general', 'error', 'invalid language')
            return
        for k, v in list(tagNames.items()):
            ini.set('tagname', k, v)
        # by default switch off initially:
        ini.set('general', 'initial on', '0')

            
def stripSpokenForm(w):
    pos = w.find('\\')
    if pos == -1:
        return w
    elif pos == 0:
        return ' '
    else:
        return w[:pos]

# standard stuff Joel (adapted for possible empty gramSpec, QH, unimacro)
thisGrammar = ThisGrammar()
if thisGrammar.gramSpec:
    thisGrammar.initialize()
else:
    thisGrammar = None

def unload():
    global thisGrammar
    if thisGrammar: thisGrammar.unload()
    thisGrammar = None
