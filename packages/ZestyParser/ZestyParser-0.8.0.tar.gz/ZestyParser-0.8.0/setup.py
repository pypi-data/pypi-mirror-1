#!/usr/bin/env python

from distutils.core import setup
from setuptools import setup
try: import squisher
except: pass

desc = '''
ZestyParser is a small parsing toolkit for Python. It doesn't use the traditional separated lexer/parser approach, nor does it make you learn a new ugly syntax for specifying grammar. Grammars are built with pure Python objects; its flow is very simple, but can handle nearly any parsing problem you throw at it.
'''

setup(
    name='ZestyParser',
    version='0.8.0',
    description='Write less parsing code. Write nicer parsing code. Have fun with it.',
    author='Adam Atlas',
    author_email='adam@atlas.st',
    url='http://adamatlas.org/2006/12/ZestyParser/',
    packages=['ZestyParser'],
    long_description=desc,
    license='MIT',
    classifiers=[
    	'Development Status :: 4 - Beta',
    	'Intended Audience :: Developers',
    	'License :: OSI Approved :: MIT License',
    	'Natural Language :: English',
    	'Programming Language :: Python',
    	'Topic :: Software Development :: Libraries :: Python Modules',
    	'Topic :: Text Processing',
    ],
    include_package_data=True,
)
