#!/usr/bin/env python
### -*- coding: utf-8 -*- #############################################
#######################################################################
from setuptools import setup, find_packages

setup(
    name='pd.requires',
    version='0.0.3',
    url='http://www.dreambot.ru/product/DreamBotOtherReleases/pd.requires',
    author='Andrey Orlov',
    author_email='cray@neural.ru',
    license='GPL v2.1',
    classifiers=[
                 'Intended Audience :: Developers',
                 'License :: OSI Approved :: GNU General Public License (GPL)',
                 'Programming Language :: Python',
                 'Operating System :: OS Independent',
                 ],
    description="Module and tools used to do dependenes analys in python modules",
    long_description=(open('README.txt').read() + '\n\n' + open('CHANGES.txt').read()),
    packages=find_packages('src'),
    package_dir={'': 'src'},
    namespace_packages=['pd'],
    include_package_data=True,
    install_requires=[x.strip() for x in open("DEPENDENCES.txt").read().split("\n") if x.strip()],
    zip_safe=False,
    entry_points = {
            'console_scripts': [
                'imalyzer = pd.requires.imalyzer:main',
                'find_provides = pd.requires.find_provides:main',
                'find_requires = pd.requires.find_requires:main',
            ]
        }
    )