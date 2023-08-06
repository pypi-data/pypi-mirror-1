import re
import logging
from inspect import isclass
from copy import copy
from itertools import ifilter

from formencode import Invalid, FancyValidator
from formencode.schema import Schema
from formencode.foreach import ForEach
from formencode.variabledecode import NestedVariables, variable_decode

from toscawidgets.api import (Widget, WidgetRepeater, adapt_value,
                              RequestLocalDescriptor, RepeatedWidget)
from toscawidgets import core


__all__ = ["InputWidget", "InputWidgetRepeater"]

log = logging.getLogger(__name__)


class DefaultValidator(FancyValidator): pass



#------------------------------------------------------------------------------
# Base class for all widgets that can generate input for the app
#------------------------------------------------------------------------------

valid_name = re.compile(r'^[\w\_\:]*$').match

class InputWidget(Widget):
    params = ['name']
    validator = DefaultValidator
    strip_name_if_root_container = True
    # If this is True, validator's which are Schema subclasses/instances will
    # be called to adjust value with from_python.
    # This is off by default because it's usually not the desired behavior
    # since Schemas usually call their subvalidators' from_python recursively
    # and that will convert the whole form causing errors when the widgets'
    # children try to adjust the value themselves. Activate only if you know 
    # what you're doing.
    force_conversion = False
    
    def __new__(cls, id=None, parent=None, children=[], **kw):
        obj = super(InputWidget, cls).__new__(cls, id, parent, children, **kw)
        obj._name = kw.pop('name', id)
        if obj._name and not valid_name(obj._name):
            raise ValueError("%s is not a valid name for an InputWidget" %
                             obj._name)
        return obj
        
    @core.only_if_initialized
    def _as_repeated(self, *args, **kw):
        cls = self.__class__
        new_name = 'Repeated'+cls.__name__
        new_class = type(new_name, (RepeatedInputWidget, cls), {})
        log.debug("Generating %r for repeating %r", new_class, self)
        return core.Child(
            new_class, self._id, children=self.children, **self.orig_kw
            )(*args, **kw)
            
    @property
    def name_path_elem(self):
        if (len(self.children) > 0 and self.strip_name_if_root_container and 
            self.is_root
        ):
            return None
        else:
            return self._name

    @property
    def name(self):
        return '.'.join(reversed([w.name_path_elem for 
            w in self.path if getattr(w, 'name_path_elem', None)])) or None
    

    error_at_request = RequestLocalDescriptor('error', 
        __doc__ = """Validation error for current request.""",
        default = None,
        )

    value_at_request = RequestLocalDescriptor('value', 
        __doc__ = """Value being validated in current request.""",
        default = None,
        )

    @adapt_value.when("isinstance(value, basestring) and not value")
    def __set_empty_string_to_None(self, value):
        """This is needed when an ancestor's Schema has converted blank input
        for us into a blank string."""
        return None

    @adapt_value.when(
        "isinstance(value, str) and value and "
        "hasattr(self.validator, 'inputEncoding')",
        priority = 1 # Give it a higher priority than the rule for a US class
        )
    def __decode_string_if_not_decoded_US_instance(self, value):
        # Work around formencode.schema.Schema which doesn't
        # run UnicodeString sub-validators on encoded strings when validation
        # fails. This causes Genshi to choke when redisplaying a failed form.
        return unicode(value, self.validator.inputEncoding)

    @adapt_value.when(
        "isinstance(value, str) and value and "
        "hasattr(self.validator, 'encoding') and "
        "self.validator.encoding is not None"
        )
    def __decode_string_if_not_decoded_US_class(self, value):
        # Same as __decode_string_if_not_decoded_US_instance but works with
        # UnicodeString classes
        return unicode(value, self.validator.encoding)

    #XXX: use_request_local should default to False but that needs patching
    #     TG 1.0. If implementing this for the first time do not depend on this
    #     default and provide it explicitly so your code won't break when this
    #     changes.
    def validate(self, value, state=None, use_request_local=True):
        """Validate value using validator if widget has one. If validation fails
        a formencode.Invalid exception will be raised.
        
        If ``use_request_local`` is True and validation fails the exception and
        value will be placed at request local storage so if the widget is 
        redisplayed in the same request ``error`` and ``value`` don't have to 
        be passed explicitly to ``display``.
        """
        if self.validator:
            try:
                value =  self.validator.to_python(value, state)
            except Invalid, error:
                if use_request_local:
                    self.error_at_request = error
                    # Check for 'items' to support MultiDicts et al.
                    if hasattr(value, 'items'):
                        value = variable_decode(value)
                    self.value_at_request = value
                raise error
        return value

    def adjust_value(self,value, validator=None):
        validator = validator or self.validator
        if validator and ((not isinstance(self.validator, Schema)) or 
                           self.force_conversion):
            # Does not adjust_value with Schema because it will recursively
            # call from_python on all sub-validators and that will send
            # strings through their update_params methods which expect
            # python values. adjust_value is called just before sending the
            # value to the template, not before.
            # This behaviour can be overriden with the force_conversion flag
            try:
                value = validator.from_python(value)
            except Invalid:
                # Ignore conversion errors so bad-input is redisplayed
                # properly
                pass
            if value is None:
                # A None will skip renderingthe value attribute altogether in
                # Genshi templates and that's not what we want. Worse still,
                # String templates will render a "None", yuck! Convert it
                # into an empty string if the validator hasn't done it already.
                value = ""
        return value

    def safe_validate(self, value):
        """Tries to coerce the value to python using the validator. If
        validation fails the original value will be returned unmodified."""
        try:
            value = self.validate(value, use_request_local=False)
        except Exception:
            pass
        return value

    def prepare_dict(self, value, kw, adapt=True):
        if value is None:
            value = self.get_default()
        if adapt:
            value = self.adapt_value(value)
        if self.is_root:
            error = kw.setdefault('error', self.error_at_request)
        else:
            error = kw.setdefault('error', None)
        if error:
            if self.children:
                self.propagate_errors(kw, error)
            if self.is_root:
                value = self.value_at_request

        if not isinstance(self.validator, (ForEach,Schema)):
            # Need to coerce value in case the form is being redisplayed with 
            # uncoereced value so update_params always deals with python
            # values. Skip this step if validator will recursively validate
            # because that step will be handled by child widgets.
            value = self.safe_validate(value)
        kw['error_for'] = self._get_child_error_getter(kw['error'])
        kw = super(InputWidget, self).prepare_dict(value, kw, adapt=False)
        kw['field_for'] = lambda name: self.c[name]
        # Provide backwards compat. for display_field_for. should deprecate
        kw['display_field_for'] = kw['display_child']
        # Adjust the value with the validator if present and the form is not
        # being redisplayed because of errors *just before* sending  it to the
        # template.
        if not error:
            kw['value'] = self.adjust_value(kw['value'])
            # Rebind these getters with the adjusted value
            kw['value_for'] = self._get_child_value_getter(kw.get('value'))
            # Provide a shortcut to display a child field in the template
            kw['display_child'] = self._child_displayer(kw['value_for'],kw['args_for'])
        return kw

    def update_params(self, d):
        super(InputWidget, self).update_params(d)
        if d.error:
            d.css_classes.append("has_error")

    def propagate_errors(self, parent_kw, parent_error):
        child_args = parent_kw.setdefault('child_args',{})
        if parent_error.error_dict:
            for k,v in parent_error.error_dict.iteritems():
                child_args.setdefault(k, {})['error'] = v


    def _get_child_error_getter(self, error):
        def error_getter(child_id):
            try:
                if error and error.error_list:
                    if (isinstance(child_id, Widget) and 
                       hasattr(child_id, 'repetition')
                    ):
                        child_id = child_id.repetition
                    return error.error_list[child_id]
                elif error and error.error_dict:
                    if isinstance(child_id, Widget):
                        child_id = child_id._id
                    return error.error_dict[child_id]
                
            except (IndexError,KeyError): pass
            return None
        return error_getter


    def post_init(self, *args, **kw):
        if _has_child_validators(self) and not isinstance(self, WidgetRepeater):
            if isinstance(self.validator, Schema):
                log.debug("Extending Schema for %r", self)
                self.validator = _update_schema(_copy_schema(self.validator), self.children)
            elif isclass(self.validator) and issubclass(self.validator, Schema):
                log.debug("Instantiating Schema class for %r", self)
                self.validator = _update_schema(self.validator(), self.children)
            elif self.validator is DefaultValidator:
                self.validator = _update_schema(Schema(), self.children)

            if self.is_root and hasattr(self.validator, 'pre_validators'):
                #XXX: Maybe add VariableDecoder to every Schema??
                log.debug("Appending decoder to %r", self)
                self.validator.pre_validators.insert(0, VariableDecoder)
            assert isinstance(self.validator, Schema), repr(self.validator)
        
        


class InputWidgetRepeater(WidgetRepeater, InputWidget):
    name_path_elem = None

    def __new__(cls, id=None, parent=None, children=[], **kw):
        widget = kw.get('widget', getattr(cls, 'widget', None))
        if widget is None:
            warn("No repeated widget specified in %s" % cls.__name__)
            widget = Widget()
        if isclass(widget) and issubclass(widget, Widget):
            widget = widget()
        obj = InputWidget.__new__(cls,id,parent,**kw)
        for i in xrange(obj.max_repetitions):
            widget._as_repeated(obj, repetition=i, id=obj._id)
        return obj
        
    def propagate_errors(self, parent_kw, parent_error):
        child_args = parent_kw.setdefault('child_args',[])
        if parent_error.error_list:
            for i,e in enumerate(parent_error.error_list):
                try:
                    child_args[i]['error'] = e
                except IndexError:
                    child_args.append({'error':e})
    

    def post_init(self, *args, **kw):
        if self.validator is DefaultValidator and _has_child_validators(self):
            log.debug("Generating a ForEach validator for %r", self)
            self.validator = ForEach(self.children[0].validator)

    def adjust_value(self, value, validator=None):
        # no-op as value will be adjusted by repeated widgets
        return value

try:
    from sqlalchemy.orm.attributes import InstrumentedList
    @adapt_value.when(
        "self in InputWidgetRepeater and isinstance(value, InstrumentedList)")
    def __adapt_instrumented_list(self, value):
        return list(value)
except ImportError:
    pass

class RepeatedInputWidget(RepeatedWidget):
    @property
    def name_path_elem(self):
        return "%s-%d" % (self._name, self.repetition)
        
#------------------------------------------------------------------------------
# Automatic validator generation functions.
#------------------------------------------------------------------------------


def _has_validator(w):
    try:
        return w.validator is not None
    except AttributeError:
        return False


def _has_child_validators(widget):
    for w in widget.children:
        if _has_validator(w): return True
    return False



def _copy_schema(schema):
    """
    Does a deep copy of a Schema instance
    """
    new_schema = copy(schema)
    new_schema.pre_validators = copy(schema.pre_validators)
    new_schema.chained_validators = copy(schema.chained_validators)
    new_schema.order = copy(schema.order)
    fields = {}
    for k, v in schema.fields.iteritems():
        if isinstance(v, Schema):
            v = _copy_schema(v)
        fields[k] = v
    new_schema.fields = fields
    return new_schema
    
def _update_schema(schema, children):
    """
    Extends a Schema with validators from children. Does not clobber the ones
    declared in the Schema.
    """
    for w in ifilter(_has_validator, children): 
        _add_field_to_schema(schema, w._name, w.validator)
    return schema

def _add_field_to_schema(schema, name, validator):
    """ Adds a validator if any to the given schema """
    if validator is not None:
        if isinstance(validator, Schema):
            # Schema instance, might need to merge 'em...
            if name in schema.fields:
                assert (isinstance(schema.fields[name], Schema), 
                        "Validator for '%s' should be a Schema subclass" % name)
                validator = _merge_schemas(schema.fields[name], validator)
            schema.add_field(name, validator)
        elif _can_add_field(schema, name):
            # Non-schema validator, add it if we can...
            schema.add_field(name, validator)
    elif _can_add_field(schema, name):
        schema.add_field(name, DefaultValidator)

def _can_add_field(schema, field_name):
    """
    Checks if we can safely add a field. Makes sure we're not overriding
    any field in the Schema. DefaultValidators are ok to override. 
    """
    current_field = schema.fields.get(field_name)
    return bool(current_field is None or
                isinstance(current_field, DefaultValidator))

def _merge_schemas(to_schema, from_schema, inplace=False):
    """ 
    Recursively merges from_schema into to_schema taking care of leaving
    to_schema intact if inplace is False (default).
    """
    if not inplace:
        to_schema = _copy_schema(to_schema)

    # Recursively merge child schemas
    is_schema = lambda f: isinstance(f[1], Schema)
    seen = set()
    for k, v in ifilter(is_schema, to_schema.fields.iteritems()):
        seen.add(k)
        from_field = from_schema.fields.get(k)
        if from_field:
            v = _merge_schemas(v, from_field)
            to_schema.add_field(k, v)

    # Add remaining fields if we can
    can_add = lambda f: f[0] not in seen and _can_add_field(to_schema, f[0])
    for field in ifilter(can_add, from_schema.fields.iteritems()):
        to_schema.add_field(*field)
                
    return to_schema

class VariableDecoder(NestedVariables):
    pass

