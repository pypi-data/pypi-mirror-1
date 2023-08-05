#!/usr/bin/env python
#from distutils.core import setup
from setuptools import setup, find_packages
setup(name="workspace.plugins.gvim",
      version="0.2.1",
      author="Andy Smith",
      author_email="workspace_gvim_py@anarkystic.com",
      description="MacOS X gvim plugin for Workspace Overmind",
      long_description="Adds support for saving and loading gvim workspace on Mac",
      license="MIT License",
      namespace_packages=["workspace.plugins"],
      install_requires=["workspace>=0.3"],
      url="http://an9.org/w/WorkspaceGvimPy",
      packages=find_packages(),
      classifiers=["Development Status :: 4 - Beta",
                   "Intended Audience :: Developers",
                   "License :: OSI Approved :: MIT License",
                   "Natural Language :: English",
                   "Operating System :: MacOS :: MacOS X",
                   "Programming Language :: Python",
                   "Topic :: Software Development"],
      zip_safe=False)
