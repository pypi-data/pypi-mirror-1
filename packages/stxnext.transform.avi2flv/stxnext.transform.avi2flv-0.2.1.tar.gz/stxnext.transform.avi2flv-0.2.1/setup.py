# -*- coding: utf-8 -*-
import os
from setuptools import setup, find_packages

version = open('src/stxnext/transform/avi2flv/version.txt').read()

setup (
    name='stxnext.transform.avi2flv',
    version=version,
    author='STX Next Sp. z o.o, Wojciech Lichota, Maciej Zięba',
    author_email='info@stxnext.pl',
    description='Converts clips from AVI format to FLV during upload to Plone.',
    long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
    keywords='plone avi flv movie clip flash video',
    platforms=['any'],
    url='http://www.stxnext.pl/open-source',
    license='Zope Public License, Version 2.1 (ZPL)',
    packages=find_packages('src'),
    include_package_data=True,
    package_dir={'':'src'},
    namespace_packages=['stxnext'],
    zip_safe=False,

    install_requires=[
        'setuptools',
        'collective.monkeypatcher',
       ],

    entry_points="""
    [z3c.autoinclude.plugin]
    target = plone
    """,

    classifiers=[
        'Development Status :: 3 - Alpha',
        'Framework :: Zope2',
        'Framework :: Plone',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Zope Public License',
        'Natural Language :: English',
        'Programming Language :: Python',
        ]
    )
