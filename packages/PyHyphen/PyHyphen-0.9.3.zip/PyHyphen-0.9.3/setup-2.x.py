
# This file includes those parts of the setup script that are specific to Python 2.x.
# Currently this is only the print statement.

import os.path



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
