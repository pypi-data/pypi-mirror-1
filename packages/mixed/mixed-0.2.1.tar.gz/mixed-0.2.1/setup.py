#!/usr/bin/python
from setuptools import setup, find_packages

setup(
    name="mixed",
    version="0.2.1",
    py_modules = ['mixed',],
    
    # metadata for upload to PyPI
    author = 'Catherine Devlin',
    author_email = 'catherine.devlin@gmail.com',
    description = 'Class for fractions and mixed numbers',
    license = 'MIT',
    keywords = 'fraction arithmetic',
    url = 'http://trac-hg.assembla.com/mixed_python/',
    
    long_description = """Class that parses strings representing fractions
and mixed numbers and handles arithmetic using them properly.""",

    classifiers=[
        'Development Status :: 3 - Alpha',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'License :: OSI Approved :: MIT License',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Scientific/Engineering :: Mathematics',
    ],
    )

