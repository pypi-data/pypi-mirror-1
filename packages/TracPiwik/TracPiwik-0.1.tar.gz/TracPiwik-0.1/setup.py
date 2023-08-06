#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: sw=4 ts=4 fenc=utf-8 et
# ==============================================================================
# Copyright © 2008 UfSoft.org - Pedro Algarvio <ufs@ufsoft.org>
# Copyright © 2009 Benjamin Wohlwend <bw@piquadrat.ch>
#
# Please view LICENSE for additional licensing information.
# ==============================================================================

import re
from setuptools import setup
import tracext.piwik as piwik

setup(
    name = piwik.__package__,
    version = piwik.__version__,
    author = piwik.__author__,
    author_email = piwik.__email__,
    description = piwik.__summary__,
    license = piwik.__license__,
    url = piwik.__url__,
    download_url = 'http://python.org/pypi/%s' % piwik.__package__,
    long_description = re.sub(r'(\.\.[\s]*[\w]*::[\s]*[\w+]*\n)+', r'::\n',
                              open('README.rst').read()),
    packages = ['tracext', 'tracext.piwik', ],
    namespace_packages = ['tracext', ],
    package_data = {'tracext.piwik': ['templates/*.html',
                                      'htdocs/*.css']},
    include_package_data = True,
    install_requires = ['Trac>=0.11'],
    keywords = "trac plugin piwik",
    entry_points = """
    [trac.plugins]
      tracext.piwik = tracext.piwik
      tracext.piwik.admin = tracext.piwik.admin
      tracext.piwik.web_ui = tracext.piwik.web_ui
    """,
    classifiers = ['Framework :: Trac']
)
