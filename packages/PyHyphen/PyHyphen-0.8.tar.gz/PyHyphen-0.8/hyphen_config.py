import os, shutil


# Adjust the default path for dictionaries in module hyphen/config.py to the package root.
def cfg():
    print "Configuring...",
    import hyphen
    mod_path = '/'.join((hyphen.__path__[0], 'config.py'))
    f = open(mod_path, "w")
    contents = ''.join(("default_dic_path = '", hyphen.__path__[0], "'\n",
    "default_repository = 'http://ftp.services.openoffice.org/pub/OpenOffice.org/contrib/dictionaries/'\n"))
    f.write(contents)
    f.close()
    print "Done.\n"


# Prepare the import of hyphen by cfg(). It cannot be imported from the distribution root
# as hnjmodule may be missing there and __pyth__[0] needed to adjust the default
# directory path would point to the wrong directory. So we rename the hyphen
# directory temporarily.
if os.path.exists('hyphen'): shutil.move('hyphen', 'hyphen_')
cfg()
if os.path.exists('hyphen_'): shutil.move('hyphen_', 'hyphen')
