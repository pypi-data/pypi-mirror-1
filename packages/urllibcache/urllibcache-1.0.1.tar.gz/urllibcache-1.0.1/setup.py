from setuptools import setup, find_packages

import os

version = '1.0.1'

long_description = open(os.path.join(os.path.dirname(__file__), 'README.txt')).read()

setup(
    name='urllibcache',
    version=version,
    description="Simple urllib2 caching handler",
    long_description=long_description[long_description.find('\n\n'):],
    classifiers=[
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords='urllib cache',
    author='Florian Schulze',
    author_email='florian.schulze@gmx.net',
    url='http://svn.plone.org/svn/collective/urllibcache',
    license='GPL',
    py_modules=['urllibcache'],
    zip_safe=True,
    install_requires=[
        'setuptools',
    ],
)
