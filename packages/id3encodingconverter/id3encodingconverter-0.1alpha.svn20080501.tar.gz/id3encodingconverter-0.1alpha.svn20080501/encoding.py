#!/usr/bin/env python

# encoding can guess the encoding and the language of a file using n-grams.
#
# It depends on Textcat originally by Gertjan van Noord [1], now hosted on
# WiseGuys Internet B.V. [3], and the python implementation ngram.py [2] by
# Thomas Mangin.
#
# Some languages can be and maybe are written in different encodings due to
# complete coverage in several ones. The goal here is to always return the
# "officially" propagated encoding or the encoding that is most frequently
# connected to the language's written form (e.g. german can be stored in more
# than only latin1, but german is always connected to latin1)
#
# [1] http://www.let.rug.nl/~vannoord/TextCat/
# [2] http://thomas.mangin.me.uk/software/python.html
# [3] http://software.wise-guys.nl/libtextcat/
#
# Copyright (c) 2007 Christoph Burgmer (christoph.burgmer@stud.uni-karlsruhe.de)
#
# changelog:
# * 0.3, 2007/11/29
#   - Updated documentation
#   - Added Textcat languages/encoding pairs when know
#   - Changed code as to potentially work without Textcat
# * 0.4, 2008/04/15
#   - Fixed handling of missing textcat language models
#
#This program is distributed under GNU General Public License.
#
#This program is free software; you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation; either version 2 of the License, or
#(at your option) any later version.
#
#This program is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#GNU General Public License for more details.
#
#You should have received a copy of the GNU General Public License
#along with this program; if not, write to the Free Software
#Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.

class EncodingUnknownError(Exception):
    pass

class EncodingGuesser:
    # encoding name to languages mapping (encoding names follow textcat scheme,
    # e.g. iso88597 instead of iso8859_7)
    defaultEncodings = {'windows1250': ('slovak', ),
        'windows1256': ('arabic', ), 'cp874': ('thai', ),
        'gb2312': ('chinese', ), 'big5': ('chinese', ), 'gbk': ('chinese', ),
        'euc_jp': ('japanese', ), 'shift_jis': ('japanese', ),
        'euc_kr': ('korean', ),
        'iso8859_1': ('english', 'german', 'french', 'africaans', 'spanish',
            'danish', 'swahili', 'finnish', 'portuguese', 'norwegian',
            'swedish', 'rumantsch', 'catalan', 'basque', 'latin'),
        'iso8859_2': ('bosnian', 'polish'), 'iso8859_6': ('arabic', ),
        'iso88597': ('greek', ), 'iso8859_8': ('hebrew', )}
    # 'tscii': ('tamil', ) # seems not to be supported in python

    # generic family names for encodings with multiple languages (encoding names
    # follow textcat scheme, e.g. utf instead of utf8)
    encodingGenericLang = {'iso8859_1': 'western european',
        'iso8859_2': 'central european', 'iso8859_5': 'cyrillic',
        'windows1251': 'cyrillic', 'koi8_r': 'cyrillic', 'utf': 'unicode'}

    # translation from Textcat names to python ones, if no entry, assume same
    pythonEncodingLookup = {'iso8859_1': 'latin1', 'iso88597': 'iso8859_7',
        'windows1250': 'cp1250', 'windows1251': 'cp1251',
        'windows1256': 'cp1256', 'utf': 'utf8'}

    def __init__ (self, folder="/usr/share/libtextcat/LM", language_order=[]):
        # initialize n-gram language detector
        try:
            import ngram
            self.languageDetector = ngram.NGram(folder,
                language_order=language_order)
            self._textcatAvailable = True
        except:
            self._textcatAvailable = False

        # create list of available encoding/language pairs
        self.encodingList = []
        self.descriptiveToEncoding = {}
        # generic families first
        for encoding, genericName in self.encodingGenericLang.iteritems():
            # get descriptive name for human readability
            descriptiveName = self.getDescriptiveEncodingName(genericName,
                encoding)
            self.encodingList.append(descriptiveName)
            self.descriptiveToEncoding[descriptiveName] = encoding
        # single language/encoding pairs
        # save encoding for language in case Textcat doesn't tell us
        self.languageDefaultEncoding = {}
        for encoding in self.defaultEncodings:
            if not self.encodingGenericLang.has_key(encoding):
                for realLang in self.defaultEncodings[encoding]:
                    # mapping form lang -> encoding
                    self.languageDefaultEncoding[realLang] = encoding
                    # get descriptive name for human readability
                    descriptiveName = self.getDescriptiveEncodingName(realLang,
                        encoding)
                    self.encodingList.append(descriptiveName)
                    self.descriptiveToEncoding[descriptiveName] = encoding

        ## other languages supported by the given language detector
        ## encodings not to include in supported conversions
        #ignoreEncodings = ('ascii', 'tscii') # tscii seems not to be supported
        #if self.textcatAvailable():
            #for lang in self.languageDetector.getLanguages():
                #realLang, encoding = self._splitLangEnc(lang)
                #if encoding != '' and not encoding in ignoreEncodings \
                    #and not self.encodingGenericLang.has_key(encoding):
                    #descriptiveName = self.getDescriptiveEncodingName(realLang,
                        #encoding)
                    #self.encodingList.append(descriptiveName)
                    #self.descriptiveToEncoding[descriptiveName] = encoding

    def textcatAvailable(self):
        """ Returns true if the textcat library is available and the classify()
            functionality can be used. """
        return self._textcatAvailable

    def _splitLangEnc(self, languageName):
        """ Splits the language name and the encoding off from the name given by
            the textcat language detector """
        realLang = languageName.split('-')[0]
        encoding = "".join(languageName.split('-')[1:])
        return realLang, encoding

    def classify(self, text):
        """ Classifies the language and encoding of the given text """
        if not self.textcatAvailable():
            raise Exception("Language guesser not available." \
                + " Install the python textcat implementation")
        detectedLang = self.languageDetector.classify(text)
        realLang, encoding = self._splitLangEnc(detectedLang)
        # check if textcat gives us an encoding with the language
        if encoding == '':
            # if not check our own table
            if self.languageDefaultEncoding.has_key(realLang):
                encoding = self.languageDefaultEncoding[realLang]
            else:
                # if our table doesn't include the encoding for the textcat
                # language raise an error and wait for somebody to tell us which
                # encoding this is to add it to self.defaultEncodings
                raise EncodingUnknownError("Encoding unknown")
        return realLang, encoding

    def getDescriptiveEncodingName(self, language, encoding):
        """ Returns a descriptive name of the encoding including a language name
            or language family name associated with this encoding. """
        if self.encodingGenericLang.has_key(encoding):
            return self.encodingGenericLang[encoding] + " (" + encoding + ")"
        else:
            return language + " (" + encoding + ")"

    def getEncodingForDescriptiveName(self, descriptiveName):
        """ Returns the python encoding name for the given descriptive name
            taken from getDescriptiveEncodingName(). """
        encoding = self.descriptiveToEncoding[descriptiveName]
        if self.pythonEncodingLookup.has_key(encoding):
            return self.pythonEncodingLookup[encoding]
        else:
            return encoding

    def getSupportedEncodingDict(self):
        """ Returns a dictionary of supported encodings including the associated
            language names matched to their python encoding name."""
        pairDict = {}
        for descriptive in self.encodingList:
            pairDict[descriptive] = \
                self.getEncodingForDescriptiveName(descriptive)
        return pairDict


if __name__ == '__main__':
    import sys

    text = sys.stdin.readline()
    n = EncodingGuesser()

    try:
        lang, encoding = n.classify(text)
        print "Language " + lang + ", Encoding " + encoding
    except:
        print "Error classifing language and encoding"
