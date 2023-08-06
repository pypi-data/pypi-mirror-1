#!/usr/bin/env python

import os
from distutils.core import setup

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = 'django-pingback',
    version = '0.2',
    description = 'Pingback client/server implementation for Django framework.',
    long_description = read('README'),
    keywords = 'django apps',
    license = 'New BSD License',
    author = 'Alexander Solovyov',
    author_email = 'piranha@piranha.org.ua',
    url = 'http://hg.piranha.org.ua/django-pingback/',
    install_requires = ['django-xmlrpc>=0.1.0'],
    dependency_links = ['http://pypi.aartemenko.com'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Plugins',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Internet :: WWW/HTTP',
    ],
    packages = ['pingback', 'pingback.templatetags'],
    include_package_data = True,
)

