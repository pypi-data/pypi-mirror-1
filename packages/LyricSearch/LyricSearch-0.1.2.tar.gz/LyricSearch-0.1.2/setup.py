# -*- coding: utf-8 -*-
from setuptools import setup

PACKAGE = 'LyricSearch'
VERSION = '0.1.2'

setup(
    name = PACKAGE,
    version = VERSION,
    author = 'Claudio Torcato',
    author_email = 'clauditorcato@gmail.com',
    description = 'script for letter of music in web',
    classifiers = [
          'Development Status :: 4 - Beta',
          'Environment :: Console',
          'Intended Audience :: End Users/Desktop',
          'Operating System :: MacOS :: MacOS X',
          'Operating System :: Microsoft :: Windows',
          'Operating System :: POSIX',
          'Programming Language :: Python',
    ],
    packages = ['lyricsearch'],
    install_requires = [
        "BeautifulSoup >= 3.0.3"],    
    entry_points = """
    [lyricsearch.search]
    terra = lyricsearch.lyricterra:LyricsTerra
    [console_scripts]
    lyse = lyricsearch.lyse:command
    """
)