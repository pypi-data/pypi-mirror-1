#!/usr/bin/env python

import os
from distutils.core import setup

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = 'django-cpserver',
    version = '1.0',
    url = 'http://hg.piranha.org.ua/cpserver/',
    license = 'BSD',
    description = ('Django runserver-like commands to run CherryPy web server'),
    long_description = read('README'),

    author = 'Alexander Solovyov',
    author_email = 'piranha@piranha.org.ua',

    package_dir = {'cpserver': '.'},
    packages = ['cpserver', 'cpserver.management',
                'cpserver.management.commands'],

    classifiers = [
        'Development Status :: 5 - Production/Stable',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP',
        ]
    )
