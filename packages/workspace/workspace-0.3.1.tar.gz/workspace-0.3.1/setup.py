#!/usr/bin/env python
#from distutils.core import setup
from setuptools import setup, find_packages
setup(name="workspace",
      version="0.3.1",
      author="Andy Smith",
      author_email="workspace_py@anarkystic.com",
      description="Workspace Overmind",
      long_description="A little extensible package for managing your workspace",
      license="MIT License",
      url="http://an9.org/w/WorkspacePy",
      packages = find_packages(),
      install_requires=["sprinkles>=0.4.4"],
      namespace_packages=['workspace','workspace.plugins'],
      classifiers=["Development Status :: 4 - Beta",
                   "Intended Audience :: Developers",
                   "License :: OSI Approved :: MIT License",
                   "Natural Language :: English",
                   "Operating System :: POSIX",
                   "Programming Language :: Python",
                   "Topic :: Software Development"],
      zip_safe=False,
      scripts = ['scripts/ws'])
