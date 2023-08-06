import os
from distutils.command.install import INSTALL_SCHEMES
from distutils.core import setup

setup(
    name = "zamtools-profiles",
    version = '0.9',
    description = "Django application for creating team member profiles.",
    author = "Ian Zamojc",
    author_email = "zamtools@zamtools.com",
    url = "http://code.google.com/p/zamtools-profiles/",
    packages = ['profiles',
                'profiles.tests',],
    classifiers = ['Development Status :: 4 - Beta',
                   'Environment :: Web Environment',
                   'Framework :: Django',
                   'Intended Audience :: Developers',
                   'License :: OSI Approved :: BSD License',
                   'Operating System :: OS Independent',
                   'Programming Language :: Python',
                   'Topic :: Utilities'],
)