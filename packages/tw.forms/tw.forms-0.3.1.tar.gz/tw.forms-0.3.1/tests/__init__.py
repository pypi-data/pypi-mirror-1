import os
import pkg_resources

pkg_resources.require('Genshi')

import toscawidgets.api
from toscawidgets.testutil import get_doctest_suite

dist_base = pkg_resources.get_distribution('tw.forms').location

DOCTEST_FILES = [
    os.path.join(dist_base, 'tests', 'test_*.txt'),
    ]

DOCTEST_MODULES = [
    "toscawidgets.widgets.forms.core",
    "toscawidgets.widgets.forms.fields",
    "toscawidgets.widgets.forms.datagrid",
    "toscawidgets.widgets.forms.calendars",
    "toscawidgets.widgets.forms.validators",
    ]

def additional_tests():
    return get_doctest_suite(DOCTEST_FILES, DOCTEST_MODULES)
