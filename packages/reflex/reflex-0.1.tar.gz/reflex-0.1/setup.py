from ez_setup import use_setuptools
use_setuptools()

from setuptools import setup

import reflex

setup( name="reflex",
       version=reflex.__version__,
       description="A lightweight regex-based lexical scanner library.",
       long_description=reflex.__doc__,
       author=reflex.__author__,
       author_email="viridia@gmail.com",
       url="http://viridia.org/python-projects/",
       py_modules=[ "reflex" ],
       license="Choice of GPL or Python license",
       zip_safe = True,
       test_suite = "test.test_reflex.suite",
       platforms = [ "Any" ],
       package_data = {
        '': ["LICENSE.*"],
       },
       classifiers = [
            "Development Status :: 4 - Beta",
            "License :: OSI Approved :: GNU General Public License (GPL)",
            "License :: OSI Approved :: Python Software Foundation License",
            "Programming Language :: Python",
            "Topic :: Software Development :: Libraries :: Python Modules",
            "Operating System :: OS Independent",
            "Intended Audience :: Developers",
            "Topic :: Software Development :: Compilers",
        ],
      )
