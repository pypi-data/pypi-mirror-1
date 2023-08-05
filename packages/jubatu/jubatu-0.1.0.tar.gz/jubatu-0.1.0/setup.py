#!/usr/bin/env python
 
from distutils.core import setup
import sys

if sys.argv[1]=='bdist_wininst':
    SCRIPTS=['bin/jubatu','bin/win_setup.py']
else:
    SCRIPTS=['bin/jubatu']

setup(name='jubatu',
    version='0.1.0',
    license='X11/MIT',
    platforms=['Linux', 'Windows'],
    author='Andreas Naive',
    author_email='andreasnaive@gmail.com',
    url='http://andreasnaive.blogspot.com/',
    description='XMPP gaming client',
    long_description='XMPP client designed for allowing human players to play turn-based games.\
 It has a modular structure allowing new games to be added as plugins.',
    keywords=['XMPP', 'Jabber', 'client', 'games', 'board games'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: End Users/Desktop',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: POSIX :: Linux',
        'Operating System :: Microsoft :: Windows',
        'Programming Language :: Python',
        'Topic :: Games/Entertainment',
        'Topic :: Games/Entertainment :: Board Games',
        'Topic :: Games/Entertainment :: Turn Based Strategy'
    ],
    requires=['wxpython', 'pyxmpp', 'panda3d'],
    provides=['jubatu (0.1.0)'],
    scripts=SCRIPTS,
    packages=['jubatu'],
    package_data={'jubatu': ['default.cfg', 'icons/*.xpm', 'i18n/*/*/*.mo']},
)

