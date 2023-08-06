#!/usr/bin/env python

import os
from setuptools import setup, find_packages

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = 'django-revcanonical',
    version = '1.0',
    url = 'http://hg.piranha.org.ua/django-revcanonical/',
    license = 'BSD',
    description = ('An implementation of rev=canonical '
                   'url shortening for Django.'),
    long_description = read('README'),

    author = 'Alexander Solovyov',
    author_email = 'piranha@piranha.org.ua',

    packages = find_packages(),

    classifiers = [
        'Development Status :: 4 - Beta',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP',
        ]
    )
