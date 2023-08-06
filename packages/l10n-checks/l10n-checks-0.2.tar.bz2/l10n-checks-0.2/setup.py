"""Python scripts to assist in localizing Mozilla applications

This scripts provides a way to check a given localization for
completeness and corectness.
It needs the Python Silme-library to work.
"""

docstrings = __doc__.split("\n")

import ez_setup
ez_setup.use_setuptools()

from setuptools import setup, find_packages
import sys
import os.path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'lib'))

classifiers = """\
Development Status :: 4 - Beta
Intended Audience :: Developers
License :: OSI Approved :: GNU General Public License (GPL)
License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)
License :: OSI Approved :: Mozilla Public License 1.1 (MPL 1.1)
Operating System :: OS Independent
Programming Language :: Python
Programming Language :: Python :: 2.5
Programming Language :: Python :: 2.6
Topic :: Software Development :: Libraries :: Python Modules
Topic :: Software Development :: Localization
Topic :: Software Development :: Testing
"""

from setuptools import Command
import glob

setup(name="l10n-checks",
      version="0.2",
      author="Zbigniew Braniecki, Axel Hecht, Adrian Kalla",
      author_email="akalla@aviary.pl",
      description=docstrings[0],
      long_description="\n".join(docstrings[2:]),
      license="MPL 1.1/GPL 2.0/LGPL 2.1",
      url="https://wiki.mozilla.org/L10n-Checks",
      classifiers=filter(None, classifiers.split("\n")),
      platforms=["any"],
      scripts=['scripts/check-l10n-completeness.py'],
      package_dir={'': 'lib'},
      packages = find_packages('lib',exclude=['silme.*','silme','mozcomparelocales']),
      install_requires = "silme==0.8"
      #cmdclass={'web': web}
      )
