import sys, os, ez_setup

ez_setup.use_setuptools()

from setuptools import setup, find_packages

sys.path.append('src')
import daversy

setup(
    name = 'daversy',
    version = daversy.VERSION,
    author = 'Ashish Kulkarni',
    author_email = 'kulkarni.ashish@gmail.com',
    url = 'http://www.svn-hosting.com/trac/Daversy',
    description = 'Daversy is a source control tool for relational databases.',
    license = 'GPL',
    classifiers = [
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Database',
        'Topic :: Software Development :: Version Control',
        'Topic :: Utilities'
    ],

    install_requires = ['cx_Oracle >= 4.2', 'lxml >= 1.0.3'],
    dependency_links=[
        "http://starship.python.net/crew/atuining/cx_Oracle/index.html", # cx_Oracle
    ],

    package_dir = {'': 'src'},
    packages = find_packages('src', exclude=['ez_setup']),

    entry_points = {
        'console_scripts': [
            'dvs = daversy.dvs:main',
            'dvstool_oracle = daversy.tools.dvstool_oracle:main'
        ]
    }
)