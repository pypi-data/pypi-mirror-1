#!/usr/bin/env python
from distutils.core import setup

setup(  
        name='yma2txt',
        version='0.1',
        description='A tool for converting the yahoo messenger archive to a readable good ol\' text format',
        author='Maries Ionel Cristian',
        author_email='ionel.mc@gmail.com  ',
        scripts=['yma2txt.py'],
        zip_safe=False,
        classifiers=[
            'Development Status :: 2 - Pre-Alpha',
            'Intended Audience :: Developers',
            'Intended Audience :: System Administrators',
            'License :: OSI Approved :: BSD License',
            'Operating System :: Microsoft :: Windows',
            'Programming Language :: Python',
        ],      
    )