import sys, os.path, shutil
from distutils.core import setup, Extension





longdescr = '''PyHyphen is a wrapper around the high quality hyphenation library hnj_hyphen-2.3.1 (Feb 2008) that ships
with OpenOffice.org and Mozilla products. Consequently, all dictionaries compatible with OpenOffice can be used.

It compiles and runs at least on Windows and Linux with Python 2.4 and 2.5, maybe also with Python 2.3.


The PyHyphen project is now hosted at http://pyhyphen.googlecode.com. In order to obtain the latest sources,
you will need Subversion (www.tigris.org).

Code example:

from hyphen import hyphenator
from hyphen.dictools import *

# Download and install some dictionaries in the default directory using the derault
# repository, usually the OpenOffice website
for lang in ['de_DE', 'fr_FR', 'en_UK', 'hu_HU']:
    if not is_installed(lang): install(lang)

# Create some hyphenators
h_de = hyphenator('de_DE')
h_en = hyphenator('en_US')
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

from textwrap import fill
print fill('very long text...', width = 40, use_hyphens = h_en)


See the history of changes at http://pyhyphen.googlecode.com.


.'''


arg_dict = dict(
    name = "PyHyphen", version = "0.7",
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
        'Topic :: Text Processing'
    ],
    packages = ['hyphen'],
    ext_modules = [
      Extension('hyphen.hnjmodule', ['src/hnjmodule.c',
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
        bin_file = ''.join(('bin/hnjmodule', '.', sys.platform, '-', sys.version[:3], '.pyd'))
        if os.path.exists(bin_file):
            shutil.copy(bin_file, './hyphen/hnjmodule.pyd')
            arg_dict['package_data']['hyphen'].append('hnjmodule.pyd')
            arg_dict.pop('ext_modules')
            print "Found a suitable binary version of the C extension module. This binary will be installed rather than building it from source.\n\
            However, if you prefer compiling, reenter 'python setup.py <command> --force_build_ext'."

# Include post installation script, if necessary.
if (sys.platform == 'win32') and ('--install-script' in sys.argv):
    arg_dict['scripts'] = ['hyphen_config.py']


setup(**arg_dict)

if 'install' in sys.argv:
    execfile('hyphen_config.py')
