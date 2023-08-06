#!/usr/bin/env python
### -*- coding: utf-8 -*- #############################################
#######################################################################
from setuptools import setup, find_packages

setup(
    name='nd.semanticcore',
    version='0.1.1',
    url='http://www.dreambot.ru/product/network/nd.semanticcore',
    author='Andrey Orlov',
    author_email='dbdt@dreambot.ru',
    license='GPL v2.1',
    classifiers=['Environment :: Web Environment',
                 'Intended Audience :: Developers',
                 'License :: OSI Approved :: GNU General Public License (GPL)',
                 'Programming Language :: Python',
                 'Operating System :: OS Independent',
                 'Topic :: Internet :: WWW/HTTP',
                 ],
    description="Simple tool used to help assemple semantic core",
    long_description=(open('README.txt').read() + '\n\n' + open('CHANGES.txt').read()),
    packages=find_packages('src'),
    package_dir={'': 'src'},
    namespace_packages=['nd'],
    include_package_data=True,
    install_requires=[x.strip() for x in open("DEPENDENCES.txt").read().split("\n") if x.strip()],
    entry_points = {
        'console_scripts': [
            'semanticcore = nd.semanticcore.semanticcore:main',
        ]
    },
    zip_safe=False,
    )
