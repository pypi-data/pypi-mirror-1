#!/usr/bin/env python2.4

"""Setuptools setup file"""

import sys, os

try:
    from ez_setup import use_setuptools
    use_setuptools()
except ImportError:
    pass
from setuptools import setup, find_packages

if sys.version_info < (2, 4):
    raise SystemExit("Python 2.4 or later is required ATM")

execfile(os.path.join("toscawidgets", "widgets", "forms", "release.py"))

setup(
    name=__PACKAGE_NAME__,
    version=__VERSION__,
    description="Web Widgets for building and validating forms. (former ToscaWidgetsForms)",
    #long_description = "",
    install_requires=[
        'ToscaWidgets >= 0.2rc1,<0.8',
        'FormEncode >= 1.0.1',
        ],
    extras_require = dict(
        mako = ['Mako'],
        genshi = ['Genshi >= 0.3.6'],
        ),
    url = "http://toscawidgets.org",
    download_url = "http://toscawidgets.org/download",
    author=__AUTHOR__,
    author_email=__EMAIL__,
    license=__LICENSE__,
    test_suite = 'tests',
    packages=find_packages(exclude=['ez_setup', 'tests']),
    namespace_packages = ['toscawidgets.widgets'],
    include_package_data=True,
    zip_safe=False,
    entry_points="""
    [toscawidgets.widgets]
    widgets = toscawidgets.widgets.forms
    samples = toscawidgets.widgets.forms.samples
    """,
    dependency_links=[
        'http://toscawidgets.org/download/',
        ],
    classifiers = [
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Environment :: Web Environment :: ToscaWidgets',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Software Development :: Widget Sets',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        ],
)
