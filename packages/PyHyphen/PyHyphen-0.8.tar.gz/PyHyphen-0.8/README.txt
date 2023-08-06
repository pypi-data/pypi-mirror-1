2008-09-20

PyHyphen 0.8
============

(c) 2008 Dr. Leo

Contact: fhaxbox66@googlemail.com

Project home: http://pyhyphen.googlecode.com

What's new in Version 0.8?
- supports Python 2.x and 3.0 (in 2 separate distributions))
-   contains the new C library hyphen-2.4 which implements an extended algorithm
    supporting
        - compound words (dictionaries are under development))
        - parameters to fix the minimal number of characters to be cut off
        by hyphenation (lmin, rmin, compound_lmin and compound_rmin). )
    - new en_US dictionary. This may require code changes in existing apps.
    - many minor improvements under the hood
        



Contents


1. Overview
2. Code examples
3. Compiling and installing
4. How to get dictionaries
5. What's under the hood?
6. Testing
7. Contributing and reporting bugs





1. Overview

The gole of the PyHyphen project is to provide Python with a high quality hyphenation facility.
PyHyphen consists of the package 'hyphen' and the module 'textwrap2'. There are
source distributions for Python 2.4 or higher, and Python 3.0.

1.1 The hyphen package contains:
    - at top level the definition of the class 'hyphenator' each instance of which
      can hyphenate and wrap words using a dictionary compatible with the hyphenation feature of
      OpenOffice and Mozilla.
    - the module dictools contains useful functions such as automatic downloading and
      installing dictionaries from a configurable repository. After installation, the
      OpenOffice repository is used by default.
     - config is a configuration file initialized at install time with default values
       for the directory where dictionaries are searched, and the repository for future
       downloads of dictionaries. Initial values are the package root and the OpenOffice
       repository for dictionaries.
     - hyph_en_US.dic is the hyphenation dictionary for US English as found on
       the OpenOffice.org repository.
    - 'hnj' is the C extension module that does all the ground work. It
      contains the C library hyphen-2.4 (or higher). It supports non-standard hyphenation
      with replacements as well as compound word hyphenation.
      I cannot think of a reason
      to access the wrapper class exported by 'hnj' directly rather than through
      the top level wrapper class hyphen.hyphenator. So 'hnj' is disregarded by
      'from hyphen import *'. Note that hyphenation dictionaries are invisible to the
      Python programmer. But each hyphenator object has a member 'language' which is a
      string showing the language of the dictionary in use.


1.2 The module 'textwrap2'

This module is an enhanced though backwards compatible version of the module
'textwrap' known from the Python standard library. Not very surprisingly, it adds
hyphenation functionality to 'textwrap'. To this end, a new key word parameter
'use_hyphenator' has been added to the __init__ method of the TextWrapper class which
defaults to None. It can be initialized with any hyphenator object. Note that until version 0.7
this keyword parameter was named 'use_hyphens'. So older code may need to be changed.'

1.3 hyphen_test (in the demo/ subdirectory)

This Python script is a framework for running large tests of the hyphen package.
A test is a list of 3 elements: a text file (typically a word list), its encoding and a
list of strings specifying a dictionary to be applied to the word list. Adding a test
is as easy as writing a function call. All results are logged.


2. Code examples

from hyphen import hyphenator
from hyphen.dictools import *

# Download and install some dictionaries in the default directory using the derault
# repository, usually the OpenOffice website
for lang in ['de_DE', 'fr_FR', 'en_UK', 'ru_RU']:
    if not is_installed(lang): install(lang)

# Create some hyphenators
h_de = hyphenator('de_DE')
h_en = hyphenator('en_US')

# Now hyphenate some words

print h_de.inserted(u'Schönheitskönigin')
'Schön=heits=kö=ni=gin'

print h_en.pairs('beautiful')
[[u'beau', u'tiful'], [u'beauti', u'ful']]

print h_en.wrap('beautiful', 6)
[u'beau-', u'tiful']

print h_en.wrap('beautiful', 7)
[u'beauti-', u'ful']

from textwrap import fill
print fill('very long text...', width = 40, use_hyphens = h_en)


3. Compiling and installing

3.1 General requirements

There are source distributions for Python 2.4 or highter, and Python 3.0.
There are binaries of the hnj module for win32.
On other platforms you will need a build environment such as gcc, make
and so on. PyHyphen is likely to work also with Python 2.3, but this has not been
tested.

3.2 Compiling and installing from source

Choose and download the source distribution (eather a zip archive or a tarball) from

    http://cheeseshop.python.org/pypi/PyHyphen

and unpack it in a temporary directory. Then cd to this directory.

You can compile and install the hyphen package
as well as the module textwrap2 by entering at the command line somethin like:

    python setup.py install

The setup script will first check if the distribution contains a binary version
of hnj for your platform. If there is a binary that looks ok, this version is installed. Otherwise,
hnj is compiled from source. On Windows you will need MSVC 2003
or whatever fits to your Python version.
If the distribution comes with a binary of 'hnj'
that fits to your platform and python version, you can still force a compilation from
source by entering

    python setup.py install --force_build_ext

Under Linux you may need root privileges, so you may want to enter something like

    sudo python setup.py install


3.3 Installing binary versions under Windows

If there is a Windows installer for your Windows and Python versions, you can
obviously use it. However, it does not contain the test framework hyphen_test.py. Also,
the documentation of hyphen-2.4 (the C library) is missing.

 
 4. How to get dictionaries?
 
 Visit http://wiki.services.openoffice.org/wiki/Dictionaries for a
 complete list. If you know the language and country code of your favorite
 dictionary (e.g. 'it_IT' for Italian) and have internet access, you can take
 advantage of the install function in the hyphen.dictools module. See the code
 example above (2.) for more details, or read the module documentation.


5. What's under the hood?

the C extension module 'hnj' used by the hyphenator class defined in
__init__.py contains the C library hyphen-2.4 which is used by OpenOffice.org, Mozilla
and alike. The C sources have not been changed, let alone hnjmalloc.c which has
been slightly modify to use pythonic memory management and error handling.

For further information on the hyphenation library and available dictionaries visit
http://wiki.services.openoffice.org/wiki/Dictionaries.



6. Testing

Please see the instructions in Demo/hyphen_test.py. All you need is a text file,
and its encoding. Copy the text file into the Demo/input directory, add a new function
call to hyphen_test.py, run it and read the .log file and the files created in the
output directory. There you will see the results for each word. You can specify a list
of dictionaries to be used. Then, hyphen_test will create an output file for each
dictionary used with a given word list.


7. Contributing and reporting bugs

Contributions, comments, bug reports, criticism and praise can be sent to the author.

The sources of PyHyphen are found in a Subversion repository at

    http://pyhyphen.googlecode.com
    
This is also where you can submit bug reports.


 
