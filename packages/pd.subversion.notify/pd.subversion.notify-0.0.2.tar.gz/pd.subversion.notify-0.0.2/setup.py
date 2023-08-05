#!/usr/bin/env python
### -*- coding: utf-8 -*- #############################################
#######################################################################
from setuptools import setup, find_packages

setup(
    name='pd.subversion.notify',
    version='0.0.2',
    url='http://www.dreambot.ru/product/DreamBotOtherReleases/pd.subversion.notify',
    author='Andrey Orlov',
    author_email='cray@neural.ru',
    license='GPL v2.1',
    classifiers=[
                 'Intended Audience :: Developers',
                 'License :: OSI Approved :: GNU General Public License (GPL)',
                 'Programming Language :: Python',
                 'Operating System :: OS Independent',
                 ],
    description="This programm used in subversion postcommit hook to send list of modified files to xmlrpc server",
    long_description=(open('README.txt').read() + '\n\n' + open('CHANGES.txt').read()),
    packages=find_packages('src'),
    package_dir={'': 'src'},
    namespace_packages=['pd','pd.subversion'],
    include_package_data=True,
    install_requires=[x.strip() for x in open("DEPENDENCES.txt").read().split("\n") if x.strip()],
    zip_safe=False,
    entry_points = {
            'console_scripts': [
                'pdsubversionnotify = pd.subversion.notify.pdsubversionnotify:main',
            ]
        }
    )