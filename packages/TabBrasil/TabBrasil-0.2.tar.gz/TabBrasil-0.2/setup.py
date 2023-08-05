# -*- coding: utf-8 -*-
from setuptools import setup

PACKAGE = 'TabBrasil'
VERSION = '0.2'

setup(
    name = PACKAGE,
    version = VERSION,
    author = 'Claudio Torcato',
    author_email = 'clauditorcato@gmail.com',
    description = """
    Plugin for LyricSearch to search tablatures in CifraClub.com.br.""",
    classifiers = [
          'Development Status :: 4 - Beta',
          'Environment :: Console',
          'Intended Audience :: End Users/Desktop',
          'Operating System :: MacOS :: MacOS X',
          'Operating System :: Microsoft :: Windows',
          'Operating System :: POSIX',
          'Programming Language :: Python',
          'Natural Language :: Portuguese (Brazilian)',
    ],
    py_modules = ['cifrasearch'],
    install_requires = [
        "BeautifulSoup >= 3.0.3"],    
    entry_points = """
    [lyricsearch.search]
    cifraclub = cifrasearch:ClubCifra
    """
)
