#!/usr/bin/env python

from commons.setup import run_setup

pkg_info_text = """
Metadata-Version: 1.1
Name: mailing-list-filter
Version: 0.2
Author: Yang Zhang
Author-email: yaaang NOSPAM at REMOVECAPS gmail
Home-page: http://assorted.sourceforge.net/mailing-list-filter/
Download-url: http://pypi.python.org/pypi/mailing-list-filter/
Summary: Mailing List Filter
License: Python Software Foundation License
Description: Filter mailing list email for relevant threads only.
Keywords: mailing,list,email,filter,IMAP,Gmail
Platform: any
Provides: commons
Classifier: Development Status :: 4 - Beta
Classifier: Environment :: No Input/Output (Daemon)
Classifier: Intended Audience :: End Users/Desktop
Classifier: License :: OSI Approved :: Python Software Foundation License
Classifier: Operating System :: OS Independent
Classifier: Programming Language :: Python
Classifier: Topic :: Communications :: Email
"""

run_setup(pkg_info_text, scripts = ['src/mlf.py'])
