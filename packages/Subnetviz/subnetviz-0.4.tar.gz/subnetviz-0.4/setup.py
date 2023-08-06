#!/usr/bin/env python

from distutils.core import setup

setup (name = "Subnetviz",
       version = "0.4",
       description = "Hierarchal IP subnet visualization",
       long_description = """Subnetviz reads IP network addresses
(base IP addresses and CIDR prefix lengths) and produces
visualizations of the overall network tree structure.

HTML table and plaintext formats are supported for output.""",
       requires = ["IPy"],
       url = "http://www.thoughtcrime.us/software/subnetviz/",
       author = "J.P. Larocque",
       author_email = "jpl-software at thoughtcrime.us",
       license = "ISC-style",
       classifiers = ["Development Status :: 4 - Beta",
                      "Intended Audience :: System Administrators",
                      "Intended Audience :: Information Technology",
                      "Intended Audience :: Telecommunications Industry",
                      "License :: OSI Approved :: ISC License (ISCL)",
                      "Natural Language :: English",
                      "Operating System :: OS Independent",
                      "Programming Language :: Python",
                      "Topic :: Internet",
                      "Topic :: Utilities"],
       packages = ["subnetviz", "subnetviz.format"],
       scripts = ["bin/subnetviz", "bin/subnetviz.cgi"])
