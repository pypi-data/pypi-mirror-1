#!/usr/bin/env python
# -*- coding: utf-8 -*-

from distutils.core import setup

setup(name='auf-refer',
    version='1.1.1',
    author='Progfou',
    author_email='jean-christophe.andre@auf.org',
    url='http://git.auf.org/?p=auf-refer.git',
    description='AuF utility to optimize access to reference data',
    long_description='Ce paquet fournit un outil permettant de copier puis de mettre régulièrement à jour une sélection des référentiels AuF.',
    license='LGPL',
    #download_url='git://git.auf.org/auf-refer.git',
    classifiers=[
        'License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Programming Language :: Python',
        'Topic :: Database :: Front-Ends',
        'Natural Language :: French',
    ],
    requires=['simplejson'],
    py_modules=['aufrefer'],
    data_files=[
        ('/etc/auf-refer',['auf-refer.conf','apache.conf']),
        ('/usr/sbin',['auf-refer']),
        ('/usr/share/man/man8',['auf-refer.8']),
        ],
    )

