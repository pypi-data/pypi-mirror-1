#!/usr/bin/env python

from distutils.core import setup
from setuptools import setup
try: import squisher
except: pass

desc = '''
ZestyParser is a small parsing toolkit for Python. It doesn't use the traditional separated lexer/parser approach, nor does it make you learn a new ugly syntax for specifying grammar. It is based entirely on Python regular expressions and callbacks; its flow is very simple, but can accomodate a vast array of parsing situations.
'''

setup(
    name='ZestyParser',
    version='0.7.0',
    description='A simple but highly flexible approach to parsing',
    author='Adam Atlas',
    author_email='adam@atlas.st',
    url='http://adamatlas.org/2006/12/ZestyParser/',
    packages=['ZestyParser'],
    long_description=desc,
    license='GPL',
    classifiers=[
    	'Development Status :: 4 - Beta',
    	'Intended Audience :: Developers',
    	'License :: OSI Approved :: GNU General Public License (GPL)',
    	'Natural Language :: English',
    	'Programming Language :: Python',
    	'Topic :: Software Development :: Libraries :: Python Modules',
    	'Topic :: Text Processing',
    ],
    include_package_data=True,
)
