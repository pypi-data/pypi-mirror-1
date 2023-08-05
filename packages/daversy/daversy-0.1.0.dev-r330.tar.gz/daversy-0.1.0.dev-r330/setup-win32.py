from distutils.core import setup
import py2exe
import os, sys, re

sys.path.append('src')
import daversy
src_dir = os.path.join(os.getcwd(), os.path.dirname(sys.argv[0]))
version = daversy.VERSION

try:
    svn_entries = open(os.path.join(src_dir, '.svn', 'entries')).read()
except IOError:
    svn_version = version
else:
    revision = re.search('<entry[^>]*name=""[^>]*revision="([^"]+)"',
                         svn_entries).group(1)
    svn_version = version + '.' + revision

setup(
    version = svn_version,
    description = 'Database Versioning System',
    name = 'dvs',

    # targets to build
    console = ['src/daversy/dvs.py', 'src/daversy/tools/dvstool_oracle.py'],
    options = {'py2exe': { 'dll_excludes': 'oci.dll', 'packages':['daversy.command'] } }
)
