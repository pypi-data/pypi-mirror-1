# -*- coding: utf-8 -*-
# 
#  setup.py
#  scrape-highlighted
#  
#  Created by Lars Yencken on 2009-05-04.
#  Copyright 2009 Lars Yencken. All rights reserved.
# 

from setuptools import setup

VERSION = '0.1.0'

setup(
        name='scrape-highlighted',
        description="A script to scrape highlighted text from a pdf [Mac only].",
        long_description="""
        A basic script scraping highlighted text from pdfs, making use of
        a Python-applescript bridge and the Skim pdf reader. [Mac only]
        """,
        url='http://bitbucket.org/lars512/scrape-highlighted/',
        version=VERSION,
        author='Lars Yencken',
        author_email='lljy@csse.unimelb.edu.au',
        license='BSD',
        install_requires=['appscript'],
        scripts=['scrape_highlighted.py'],
    )
