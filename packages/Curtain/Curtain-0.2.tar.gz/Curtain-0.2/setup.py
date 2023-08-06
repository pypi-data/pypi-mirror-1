#!/usr/bin/env python
from setuptools import setup, find_packages

setup(
    # descriptive metadata
    name = "Curtain",
    version = "0.2",
    author = "Mattia Belletti",
    author_email = "mattia.belletti@gmail.com",
    url = "http://curtain.sourceforge.net",
    description = "A lean compiled templating system with support for i18n",
    long_description = '''Curtain is a templating system akin to TAL, together
    with the METAL and Zope's i18n extensions. It's compiled, based on SAX, and
    thought to read and produce always well-formed XML. The syntax and semantic
    is kept very simple, and strive to be 100% tested and documented as a
    development principle.''',
    download_url = 'http://sourceforge.net/projects/curtain/files/',
    license = "BSD",
    keywords = "curtain template templating i18n macro tal",
    classifiers = [
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Framework :: BFG',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.5',
        'Programming Language :: Python :: 2.6',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Text Processing :: Markup :: XML'
        ],

    # program metadata
    packages = find_packages('src'),
    package_dir = {'': 'src'},
    install_requires = ['zope.interface', 'zope.i18n'],
    test_suite = 'curtain.tests.run',
)
