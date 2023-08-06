"""
Python implementation of TagLibs FileRef class (fileref.cpp):
http://websvn.kde.org/trunk/kdesupport/taglib/taglib/fileref.cpp?revision=773935&view=markup.

Comparision on instances is not implemented (yet).

This classes now are in TagPy, this just stayes here for compatibility with old
versions.
"""

from tagpy import mpeg, flac, mpc # TODO , wavpack, trueaudio
from tagpy.ogg import vorbis as oggvorbis
from tagpy.ogg import flac as oggflac
# TODO from tagpy.ogg import speex as oggspeex
import tagpy

global _fileTypeResolvers
_fileTypeResolvers = []

class PyFileTypeResolver(object):
    def __init__(self):
        pass

    def createFile(self, fileName, readAudioProperties=True,
        audioPropertiesStyle=tagpy.ReadStyle.Average):
        raise NotImplementedError

class PyFileRef(object):

    def __init__(self):
        self._file = None

    def __init__(self, f, readAudioProperties=True,
            audioPropertiesStyle=tagpy.ReadStyle.Average):
        if isinstance(f, PyFileRef):
            self._file = f._file
        elif isinstance(f, tagpy.File):
            self._file = f
        else:
            self._file = PyFileRef.create(f, readAudioProperties)

    def audioProperties(self):
        return self._file.audioProperties()

    def tag(self):
        return self._file.tag()

    def file(self):
        return self._file

    def save(self):
        return self._file.save()

    @staticmethod
    def defaultFileExtensions():
        return ["ogg", "flac", "oga", "mp3", "mpc", "wv", "spx", "tta"]

    def isNull(self):
        try:
            return not self._file or not self._file.isValid()
        except AttributeError:
            # work around missing method isValid in tagpy < 0.94.X
            return not self._file

    @staticmethod
    def addFileTypeResolver(resolver):
        _fileTypeResolvers.insert(0, resolver)
        return resolver

    @staticmethod
    def create(fileName, readAudioProperties=True,
            audioPropertiesStyle=tagpy.ReadStyle.Average):
        for resolver in _fileTypeResolvers:
            file = resolver.createFile(fileName, readAudioProperties,
                audioPropertiesStyle)
            if file:
                return file
        if fileName.upper().endswith(".OGG"):
            return oggvorbis.File(fileName, readAudioProperties,
                audioPropertiesStyle)
        if fileName.upper().endswith(".MP3"):
            return mpeg.File(fileName, readAudioProperties,
                audioPropertiesStyle)
        if fileName.upper().endswith(".OGA"):
            return oggflac.File(fileName, readAudioProperties,
                audioPropertiesStyle)
        if fileName.upper().endswith(".FLAC"):
            return flac.File(fileName, readAudioProperties,
                audioPropertiesStyle)
        if fileName.upper().endswith(".MPC"):
            return mpc.File(fileName, readAudioProperties,
                audioPropertiesStyle)
        #if fileName.upper().endswith(".WV"):
            #return wavpack.File(fileName, readAudioProperties,
                #audioPropertiesStyle)
        #if fileName.upper().endswith(".SPX"):
            #return oggspeex.File(fileName, readAudioProperties,
                #audioPropertiesStyle)
        #if fileName.upper().endswith(".TTA"):
            #return trueaudio.File(fileName, readAudioProperties,
                #audioPropertiesStyle)
