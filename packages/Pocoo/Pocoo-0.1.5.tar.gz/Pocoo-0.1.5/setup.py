# -*- coding: utf-8 -*-
"""
Pocoo
=====

Pocoo is an open-source bulletin board written in Python. It provides an advanced
plugin system with a component architecture which allows other developers to
modify Pocoo to their liking without the need to touch existing source code.
Because it uses SQLAlchemy, it is possible to use either MySQL, SQLite, Oracle
or Postgres as storage backend.
"""
import ez_setup
ez_setup.use_setuptools()
from setuptools import setup, find_packages


AUTHORS = []
f = file('AUTHORS')
for line in f:
    if line.startswith('-'):
        AUTHORS.append(line[1:].strip())
f.close()

setup(
    name = 'Pocoo',
    version = '0.1.5',
    url = 'http://www.pocoo.org/',
    download_url = 'http://sourceforge.net/project/showfiles.php?group_id=176969',
    license = 'GNU General Public License (GPL)',
    author = ', '.join(AUTHORS),
    description = 'Pocoo is an open-source bulletin board software written in Python.',
    long_description = __doc__,
    keywords = 'forum pocoo wsgi web',
    packages = [
        'pocoo',
        'pocoo.utils',
        'pocoo.pkg',
        'pocoo.pkg.core',
        'pocoo.pkg.highlight',
        'pocoo.pkg.latex',
        'pocoo.pkg.pony',
        'pocoo.pkg.webadmin',
        'pocoo.wrappers',
    ],
    platforms = 'any',
    zip_safe = False,
    include_package_data = True,
    install_requires = [
        'simplejson >= 1.0',
        'SQLAlchemy >= 0.2.7',
        'Colubrid >= 0.10',
        'Jinja >= 0.9'
    ],
    classifiers = [
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Intended Audience :: Developers',
        'Intended Audience :: End Users/Desktop',
        'Intended Audience :: System Administrators',
        'Development Status :: 3 - Alpha',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content :: Message Boards',
        'Programming Language :: Python',
        'Programming Language :: JavaScript',
        'Operating System :: OS Independent',
    ]
)
