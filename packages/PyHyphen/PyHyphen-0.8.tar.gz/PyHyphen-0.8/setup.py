import sys, os.path, shutil
from distutils.core import setup, Extension





longdescr = """PyHyphen is a wrapper around the high quality hyphenation library
hyphen-2.4 (May 2008) that ships
with OpenOffice.org and Mozilla products. Hence, all dictionaries
compatible with OpenOffice can be used.

This distribution of PyHyphen runs on Windows and Linux with Python 2.4, 2.5 and 2.6.
There is also a distribution for Python 3.0 (if not yet on the pypi, check out the svn repository).

The windows distributions may include pre-compiled binary files of the extension
module hnj containing the C library that does the ground work.
 
By default, the appropriate binary, if available, will be installed rather
than compiling the C sources.
Currently, the P2.x distribution ships with binaries for P2.4 and 2.5.

PyHyphen also contains textwrap2, an enhanced though backwards-compatible version of the standard Python module textwrap. Not very surprisingly, textwrap2 can hyphenate words when wrapping them.

Changes in version 0.8:
- upgraded to C library hyphen 2.4 (supports compound words and parameters for the
  minimum number of characters to be cut off by hyphenation) Note that this might
  require small code changes to existing applications.
- an enhanced dictionary for en_US
- many small improvements under the hood
- support for Python 2.4-2.6 and 3.0


Code example:

from hyphen import hyphenator
from hyphen.dictools import *

# Download and install some dictionaries in the default directory using the default
# repository, usually the OpenOffice website
for lang in ['de_DE', 'fr_FR', 'en_UK', 'hu_HU']:
    if not is_installed(lang): install(lang)

# Create some hyphenators
h_de = hyphenator('de_DE')
h_en = hyphenator(lmin = 3, rmin = 3) # the en_US dictionary is used by default!
h_hu = hyphenator('hu_HU')

# Now hyphenate some words

print h_hu.inserted(u'asszonnyal')
'asz=szony=nyal'

print h_en.pairs('beautiful')
[[u'beau', u'tiful'], [u'beauti', u'ful']]

print h_en.wrap('beautiful', 6)
[u'beau-', u'tiful']

print h_en.wrap('beautiful', 7)
[u'beauti-', u'ful']

from textwrap2 import fill
print fill('very long text...', width = 40, use_hyphenator = h_en)

The PyHyphen's Subversion repository is hosted at http://pyhyphen.googlecode.com. 
"""


arg_dict = dict(
    name = "PyHyphen", version = "0.8",
    author = "Dr. Leo",
    author_email = "fhaxbox66@googlemail.com",
    url = "http://pyhyphen.googlecode.com",
    description = "The hyphenation library of OpenOffice and FireFox wrapped for Python",
    long_description = longdescr,
    classifiers = [
        'Intended Audience :: Developers',
         'Development Status :: 4 - Beta',
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


if len(set(('install', 'bdist_wininst', 'bdist')) - set(sys.argv)) < 3:
    if  '--force_build_ext' in sys.argv:
        sys.argv.remove('--force_build_ext')
    else:
        bin_file = ''.join(('bin/hnj', '.', sys.platform, '-', sys.version[:3], '.pyd'))
        if os.path.exists(bin_file):
            shutil.copy(bin_file, './hyphen/hnj.pyd')
            arg_dict['package_data']['hyphen'].append('hnj.pyd')
            arg_dict.pop('ext_modules')
            print "Found a suitable binary version of the C extension module. This binary will be installed rather than building it from source.\n\
            However, if you prefer compiling, reenter 'python setup.py <command> --force_build_ext'."

# Include post installation script, if necessary.
if (sys.platform == 'win32') and ('--install-script' in sys.argv):
    arg_dict['scripts'] = ['hyphen_config.py']


setup(**arg_dict)

if 'install' in sys.argv: execfile('hyphen_config.py')
