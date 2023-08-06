import os
import re
from setuptools import setup, find_packages

DESCRIPTION = """\
Trestle: doctest for ReST(ful services)\
"""

ld = []
ldf = open(os.path.join(os.path.dirname(__file__), 'tests', 'about.rst'))
copy = True
for line in ldf:
    if copy:
        if line.startswith('.. fixt') or line.startswith('.. contents'):
            continue
        if line.startswith('Examples'):
            copy = False
    elif line.startswith('.. _'):
        ld.append(line)
    if copy:
        ld.append(line)
LONG_DESCRIPTION = ''.join(ld)

CLASSIFIERS = [
    "Development Status :: 3 - Alpha",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Topic :: Software Development :: Testing"
    ]

setup(
    name='trestle',
    version=0.2,
    author='Jason Pellerin',
    author_email='jpellerin@leapfrogonline.com',
    packages=find_packages(),
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    classifiers=CLASSIFIERS,
    url="http://code.google.com/p/nose-trestle/",
    include_package_data = True,
    license="MIT License",
    entry_points = {
            'nose.plugins.0.10': [
                'trestle = trestle:Trestle'
                ]
            },
    install_requires=['nose>=0.10.1', 'docutils>=0.5'],
    tests_require=['simplejson>=1.7.1', 'Paste', 'lxml>=2.0'],
    extras_require={'json': ['simplejson>=1.7.1'],
                    'xml': ['lxml>=2.0']}
    )
