import os
import re
from setuptools import setup, find_packages
import trestle

DESCRIPTION = """\
Trestle: doctest for ReST(ful services)\
"""

LONG_DESCRIPTION = open(
    os.path.join(os.path.dirname(__file__), 'tests', 'about.rst')).read()
links = re.findall(r'^.. _.+$', LONG_DESCRIPTION, re.MULTILINE)
LONG_DESCRIPTION = LONG_DESCRIPTION[:LONG_DESCRIPTION.find('Examples')]
LONG_DESCRIPTION = LONG_DESCRIPTION.replace('.. fixtures:: about\n', '')
LONG_DESCRIPTION = LONG_DESCRIPTION.replace('.. contents::\n', '')
LONG_DESCRIPTION = LONG_DESCRIPTION + '\n\n' + '\n'.join(links)


CLASSIFIERS = [
    "Development Status :: 3 - Alpha",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Topic :: Software Development :: Testing"
    ]

setup(
    name='trestle',
    version=trestle.__version__,
    author=trestle.__author__,
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
    install_requires=['nose>=0.10.1', 'docutils>=0.4'],
    tests_require=['simplejson>=1.7.1', 'Paste', 'lxml>=2.0'],
    extras_require={'json': ['simplejson>=1.7.1'],
                    'xml': ['lxml>=2.0']}
    )
