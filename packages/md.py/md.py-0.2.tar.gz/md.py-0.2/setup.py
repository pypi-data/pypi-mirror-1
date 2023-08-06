from __future__ import absolute_import
from setuptools import setup, find_packages

setup(
    name = 'md.py',
    version = '0.2',
    description = 'A collection of Python utilities.',
    author = 'Medium',
    author_email = 'labs@thisismedium.com',
    url = 'http://thisismedium.com/labs/mdpy/',
    license = 'BSD',
    keywords = 'utilities transaction transactions fluid dynamic',

    packages = list(find_packages(exclude=('tests', 'docs', 'docs.*'))),
    install_requires = 'importlib',
    scripts = ['bin/pytest'],
    test_suite = 'tests.all',

    classifiers = [
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Utilities'
    ]
)
