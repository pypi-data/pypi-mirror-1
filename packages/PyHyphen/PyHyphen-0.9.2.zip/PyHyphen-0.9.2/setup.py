
import sys, shutil
from distutils.core import setup, Extension

# Copy version-specific files
files = {'__init__.py' : 'hyphen/',
        'dictools.py' : 'hyphen/',
        'hnjmodule.c' : 'src/',
        'textwrap2.py' : './',
        'hyphen_config.py' : './'}
ver = sys.version[0]
for file_name, dest in files.items():
    shutil.copy(ver + '.x/' + file_name, dest + file_name)



longdescr = """PyHyphen is a wrapper around the high quality hyphenation library
*hyphen-2.4* (May 2008) that ships
with OpenOffice.org and Mozilla products. Hence, all *dictionaries
compatible with OpenOffice* can be used.

This source distribution runs with
all Python versions from 2.4 to 3.0.1.

The source distribution includes *pre-compiled Win32 binary files* of the extension
module hnj for Python 2.4, 2.5, 2.6 and 3.0.
By default, the appropriate binary, if available, will be installed rather
than compiling the C sources.

PyHyphen also contains *textwrap2*, an enhanced though backwards-compatible version of the standard Python module textwrap. Not very surprisingly, textwrap2 can hyphenate words when wrapping them.

New in version 0.9.2

* C extension compiles with Python 3.0.1
*  added win32 binary of the C extension for Python 3.x

New in version 0.9.1

* supports Python 2.4 or higher, including 3.0


 New in Version 0.9:

* removed the 'inserted' method from the hyphenator class as it is not used in practice
* Added a binary for Python 2.6
* in the Python 2.x-versionthe word to be hyphenated must now be unicode (utf-8 encoded strings raise
  TypeError). The restriction to unicode is safer and more 3.0-compliant.
  In the version for Python 3.0, word is of course a string.
* fixed important bug in 'pairs' method that could cause a unicode error if 'word'
  was not encodable to the dictionary's encoding. In the latter case, the new
  version returns an empty list (consistent with other cases where the word
  is not hyphenable).
* the configuration script has been simplified and improved: it does not
  raise ImportError even if the package cannot be imported. This tolerance is
  needed to create a Debian package.


New in version 0.8:

* upgraded to C library hyphen 2.4 (supports compound words and parameters for the
  minimum number of characters to be cut off by hyphenation) Note that this might
  require small code changes to existing applications.
* an enhanced dictionary for en_US
* support for Python 2.4-2.6 and 3.0
* many small improvements under the hood



Code example:


>>> from hyphen import hyphenator
from hyphen.dictools import *
# Download and install some dictionaries in the default directory using the default
# repository, usually the OpenOffice website
for lang in ['de_DE', 'fr_FR', 'en_UK', 'hu_HU']:
    if not is_installed(lang): install(lang)
# Create some hyphenators
h_de = hyphenator('de_DE')
h_en = hyphenator(lmin = 3, rmin = 3) # the en_US dictionary is used by default!
h_hu = hyphenator('hu_HU')
# Now hyphenate some words. Note that under Python 3.0, words are of type string.
    print h_en.pairs(u'beautiful')
    [[u'beau', u'tiful'], [u'beauti', u'ful']]
    print h_en.wrap(u'beautiful', 6)
    [u'beau-', u'tiful']
    print h_en.wrap(u'beautiful', 7)
    [u'beauti-', u'ful']

    >>> from textwrap2 import fill
    print fill(u'very long text...', width = 40, use_hyphenator = h_en)

PyHyphen's Subversion repository is hosted at http://pyhyphen.googlecode.com. 
There is also a public mailing list at http://groups.google.com/group/pyhyphen
"""

arg_dict = dict(
    name = "PyHyphen", version = "0.9.2",
    author = "Dr. Leo",
    author_email = "fhaxbox66@googlemail.com",
    url = "http://pyhyphen.googlecode.com",
    description = "The hyphenation library of OpenOffice and FireFox wrapped for Python",
    long_description = longdescr,
    classifiers = [
        'Intended Audience :: Developers',
         'Development Status :: 5 - Production/Stable',
        'License :: OSI Approved',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: C',
                'Topic :: Text Processing',
                'Topic :: Text Processing :: Linguistic'
    ],
    packages = ['hyphen'],
    ext_modules = [
      Extension('hyphen.hnj', ['src/hnjmodule.c',
                                  'src/hyphen.c',
                                   'src/csutil.c',
                                   'src/hnjalloc.c' ],
                                   include_dirs = ['include'])],
    package_data = {'hyphen':['hyph_en_US.dic']},
    py_modules = ['textwrap2']
)



exec(open('setup-' + ver + '.x.py').read())

