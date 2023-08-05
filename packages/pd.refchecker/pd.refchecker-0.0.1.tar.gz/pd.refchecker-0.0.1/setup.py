#!/usr/bin/env python
### -*- coding: utf-8 -*- #############################################
#######################################################################
from setuptools import setup, find_packages

setup(
    name='pd.refchecker',
    version='0.0.1',
    url='http://www.dreambot.ru/pd.refchecker/DreamBotOtherReleases/pd.refchecker',
    author='Andrey Orlov',
    author_email='dbdt@dreambot.ru',
    license='GPL v2.1',
    classifiers=[
                 'Intended Audience :: Developers',
                 'License :: OSI Approved :: GNU General Public License (GPL)',
                 'Programming Language :: Python',
                 'Operating System :: OS Independent',
                 ],
    description="Product intendent to check validity of external reference on site",
    long_description=(open('README.txt').read() + '\n\n' + open('CHANGES.txt').read()),
    packages=find_packages('src'),
    package_dir={'': 'src'},
    namespace_packages=['pd'],
    include_package_data=True,
    install_requires=[x.strip() for x in open("DEPENDENCES.txt").read().split("\n") if x.strip()],
    zip_safe=False,
    entry_points = {
            'console_scripts': [
                'pdrefchecker = pd.refchecker.pdrefchecker:main',
            ]
        }
    )