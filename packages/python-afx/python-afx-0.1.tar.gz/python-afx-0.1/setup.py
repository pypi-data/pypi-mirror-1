#!/usr/bin/env python
# -*- mode: python; tab-width: 4; indent-tabs-mode: nil; py-indent-offset: 4; -*-
# vim:ft=python:et:sw=4:ts=4

from commons import setup

pkg_info_text = """
Metadata-Version: 1.1
Name: python-afx
Version: 0.1
Author: Yang Zhang
Author-email: yaaang NOSPAM at REMOVECAPS gmail
Home-page: http://assorted.sourceforge.net/python-afx/
Download-url: http://pypi.python.org/pypi/python-commons/
Summary: AFX
License: Python Software Foundation License
Description: Utilities and extensions to the AF asynchronous IO library.
Keywords: Python,utility,utilities,library,libraries,async,asynchronous,
          IO,networking,network,socket,sockets,I/O,threading,threads,
          thread
Platform: any
Provides: commons
Classifier: Development Status :: 4 - Beta
Classifier: Environment :: No Input/Output (Daemon)
Classifier: Intended Audience :: Developers
Classifier: License :: OSI Approved :: Python Software Foundation License
Classifier: Operating System :: OS Independent
Classifier: Programming Language :: Python
Classifier: Topic :: Communications
Classifier: Topic :: Internet
Classifier: Topic :: Software Development :: Libraries :: Python Modules
Classifier: Topic :: System
Classifier: Topic :: System :: Networking
Classifier: Topic :: Utilities
"""

setup.run_setup( pkg_info_text )
