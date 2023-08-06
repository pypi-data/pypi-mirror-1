#!/usr/bin/python
# -*- coding: utf8 -*-

from distutils.core import setup
import re
import os

FULLAUTHOR = "Christoph Burgmer <christoph.burgmer@stud.uni-karlsruhe.de>"
LICENSE = 'GNU General Public License v2'
URL = "http://code.google.com/p/id3encodingconverter"
VERSION = "0.1alpha.svn20080501"

(AUTHOR, EMAIL) = re.match('^(.*?)\s*<(.*)>$', FULLAUTHOR).groups()

# get target directories for kde4 files
kde4DataTarget = os.popen("kde4-config --expandvars --install data")\
    .read().strip()
kde4DesktopTarget = os.popen("kde4-config --expandvars --install apps")\
    .read().strip()
kde4IconTarget = os.popen("kde4-config --expandvars --install icon")\
    .read().strip()
kde4LocaleTarget = os.popen("kde4-config --expandvars --install locale")\
    .read().strip()

def createMOPathList(targetDir, sourceDir):
    import os, stat
    names = os.listdir(sourceDir)
    fileList = []
    for name in names:
        try:
            st = os.lstat(os.path.join(sourceDir, name))
        except os.error:
            continue
        if stat.S_ISDIR(st.st_mode):
            for fileName in os.listdir(os.path.join(sourceDir, name)):
                target = os.path.join(targetDir, name, 'LC_MESSAGES')
                source = os.path.join(sourceDir, name, fileName)
                fileList.append((target, [source]))
    return fileList

data_files = [(os.path.join(kde4DataTarget, 'id3encodingconverter'),
        ['id3encodingconverterui.rc', 'data/id3encodingconverter_about.png']),
    (os.path.join(kde4DesktopTarget, 'id3encodingconverter'),
        ['id3encodingconverter.desktop']),
    ('share/doc/id3encodingconverter/', ['TODO', 'DEVELOPMENT']), # 'README', 'changelog', 'COPYING'
    (kde4IconTarget, ['data/id3encodingconverter.png']),]
data_files.extend(createMOPathList(kde4LocaleTarget, 'mo/'))

setup(name='id3encodingconverter',
    version=VERSION,
    description='ID3 tag viewer for conversion of different character sets',
    long_description="id3encodingconverter is a simple ID3 tag viewer for KDE written in" \
        + " Python which supports conversion of tags from different character" \
        + " sets to Unicode with ID3v2. Its goal is fast and simple" \
        + " conversion for multiple files, letting the user compare between" \
        + " ID3v1 and ID3v2 tags and choose the correct encoding.",
    author=AUTHOR,
    author_email=EMAIL,
    url=URL,
    download_url='http://code.google.com/p/id3encodingconverter/downloads/list',
    py_modules=['encoding', 'ngram', 'ID3EncodingConverterUI',
        'ID3GuessingSetupUI', 'ID3v2EncodingUI', 'kcombolistbox', 'pytagpy'],
    packages=[],
    package_data={},
    scripts=['id3encodingconverter'],
    data_files=data_files,
    license=LICENSE,
    classifiers=['Development Status :: 3 - Alpha',
        #'Development Status :: 4 - Beta',
        #'Development Status :: 5 - Production/Stable',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Operating System :: OS Independent',
        'Environment :: X11 Applications :: KDE',
        'Topic :: Desktop Environment :: K Desktop Environment (KDE)',
        'Topic :: Multimedia :: Sound/Audio',
        'Intended Audience :: End Users/Desktop',
        'Programming Language :: Python',])
