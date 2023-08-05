#!/usr/bin/env python

from distutils.core import setup

setup(name='atropine',
      license='Public Domain',
      description='HTML Scraper Thing',
      long_description='''atropine is a screen-scraping
      library built on top of BeautifulSoup, which helps
      programmers  make assertions about document structure
      while getting at the data they are interested in.''',
      author='Moe Aboulkheir',
      version=0.1,
      url='http://atropine.sourceforge.net',
      author_email='moe@divmod.com',
      maintainer='Moe Aboulkheir',
      maintainer_email='moe@divmod.com',
      packages=('atropine',))
