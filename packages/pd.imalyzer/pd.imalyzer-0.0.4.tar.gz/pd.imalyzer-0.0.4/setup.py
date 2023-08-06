#!/usr/bin/env python
### -*- coding: utf-8 -*- #############################################
#######################################################################
from setuptools import setup, find_packages

setup(
    name='pd.imalyzer',
    version='0.0.4',
    url='http://www.dreambot.ru/product/DreamBotOtherReleases/pd.imalyzer',
    author='Andrey Orlov',
    author_email='dbdt@dreambot.ru',
    license='GPL v2.1',
    classifiers=[
                 'Intended Audience :: Developers',
                 'License :: OSI Approved :: GNU General Public License (GPL)',
                 'Programming Language :: Python',
                 'Operating System :: OS Independent',
                 ],
    description="Library for dependences analys",
    long_description=(open('README.txt').read() + '\n\n' + open('CHANGES.txt').read()),
    packages=find_packages('src'),
    package_dir={'': 'src'},
    namespace_packages=['pd'],
    include_package_data=True,
    install_requires=[x.strip() for x in open("DEPENDENCES.txt").read().split("\n") if x.strip()],
    zip_safe=True,
    entry_points = {
            'console_scripts': [
                'imalyzer_orphan = pd.imalyzer.orphan:main',
                'imalyzer_cluster = pd.imalyzer.cluster:main',
                'imalyzer_kernel = pd.imalyzer.kernel:main',
                'imalyzer_suborphan = pd.imalyzer.suborphan:main',
                'imalyzer_subtree = pd.imalyzer.subtree:main',
                'imalyzer_subtrees = pd.imalyzer.subtrees:main',
                'imalyzer = pd.imalyzer.imalyzer:main'
            ]
        }
    )