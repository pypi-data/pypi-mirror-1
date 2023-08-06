
from setuptools import setup

setup(name='beatbox',
    version='0.10',
    package_dir={'': 'src'},
    packages=['beatbox'],
    author = "Simon Fell",
    description = "A Python library for querying/updating Saleforce.com data via SOAP API",
    long_description = open('README.txt').read() + "\n" + open('CHANGES.txt').read(),
    license = "GNU GENERAL PUBLIC LICENSE Version 2",
    keywords = "python salesforce salesforce.com",
    url = "http://code.google.com/p/salesforce-beatbox/",
    classifiers = ("Development Status :: 5 - Production/Stable",)
    )
