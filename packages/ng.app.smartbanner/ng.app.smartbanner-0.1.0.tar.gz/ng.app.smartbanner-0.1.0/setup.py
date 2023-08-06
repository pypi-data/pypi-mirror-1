#!/usr/bin/env python
### -*- coding: utf-8 -*- #############################################
#######################################################################
from setuptools import setup, find_packages

setup(
    name='ng.app.smartbanner',
    version='0.1.0',
    url='http://www.dreambot.ru/DreamBotZope3Releases/ng.app.smartbanner',
    author='DreamBot Developers Team',
    author_email='dbdt@dreambot.ru',
    license='GPL v2.1',
    classifiers=['Environment :: Web Environment',
                 'Intended Audience :: Developers',
                 'License :: OSI Approved :: GNU General Public License (GPL)',
                 'Programming Language :: Python',
                 'Operating System :: OS Independent',
                 'Topic :: Internet :: WWW/HTTP',
                 'Framework :: Zope3',
                 ],
    description="",
    long_description=(open('README.txt').read() + '\n\n' + open('CHANGES.txt').read()),
    packages=find_packages('src'),
    package_dir={'': 'src'},
    namespace_packages=['ng','ng.app'],
    include_package_data=True,
    install_requires=[x.strip() for x in open("DEPENDENCES.txt").read().split("\n") if x.strip()],
    zip_safe=False,
    )
