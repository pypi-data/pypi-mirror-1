#!/usr/bin/env python


from setuptools import setup

from entwine.__init__ import __version__ as VERSION



setup(name="entwine",
    license = "GPL-2",
    version=VERSION,
    description="Command-line tool querying twine.com",
    long_description=open("README", "r").read(),
    maintainer="Rob Cakebread",
    author="Rob Cakebread",
    author_email="<cakebread@gmail.com>",
    url="http://code.google.com/p/entwine/",
    keywords="twine,semweb,RDF",
    classifiers=["Development Status :: 3 - Alpha",
                 "Intended Audience :: Developers",
                 "License :: OSI Approved :: BSD License",
                 "Programming Language :: Python",
                 "Topic :: Software Development :: Libraries :: Python Modules",
                 ],
    install_requires=["setuptools", "ConfigObj"],
    tests_require=["nose"],
    packages=['entwine'],
    package_dir={'entwine':'entwine'},
    entry_points={'console_scripts': ['entwine = entwine.cli:main',]},
    test_suite = 'nose.collector',
)

#Add this in when we get to the point we want to allow plugins:
#packages=['entwine', 'entwine.plugins'],

