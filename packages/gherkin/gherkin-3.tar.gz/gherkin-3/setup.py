from ez_setup import use_setuptools
use_setuptools()

from setuptools import setup
setup(
    name = "gherkin",
    version = "3",
    py_modules = ['gherkin'],
    description='Gherkin is a safe serializer for simple Python types.',
    author='Simon Wittber',
    author_email='simonwittber@gmail.com',
    license='MIT',
    platforms=['Any'],
    url="http://code.google.com/p/gherkin/",
    long_description="""
Gherkin is a reponse to the pickle and marshal modules being documented
as unsafe.

It can serialize all the Python simple types, including sets.

Requires Python 2.5
""" 
)


