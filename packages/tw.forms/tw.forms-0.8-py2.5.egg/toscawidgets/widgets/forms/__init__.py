"""
Form widgets for ToscaWidgets.

To download and install::
   
   easy_install twForms
"""
from toscawidgets.api import Widget
from toscawidgets.widgets.forms.core import *
from toscawidgets.widgets.forms.fields import *
from toscawidgets.widgets.forms.datagrid import *
from toscawidgets.widgets.forms.calendars import *


# build all so doc tools introspect me properly
from toscawidgets.widgets.forms.core import __all__ as __core_all
from toscawidgets.widgets.forms.fields import __all__ as __fields_all
from toscawidgets.widgets.forms.datagrid import __all__ as __datagrid_all
from toscawidgets.widgets.forms.calendars import __all__ as __calendars_all
__all__ = __core_all + __fields_all + __datagrid_all + __calendars_all
