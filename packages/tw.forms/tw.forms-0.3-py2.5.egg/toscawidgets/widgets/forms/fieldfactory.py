"""
This extension provides a lightweight interface for generating
ToscaWidgets fields with validators from a SQLAlchemy Mapper.
"""

import dispatch

from formencode import validators

from sqlalchemy import types
from sqlalchemy.orm.mapper import Mapper, class_mapper

from toscawidgets.widgets import forms

__all__ = ['generate_form_fields', 'render_form_fields']


def get_class_info(cls):
    name = cls.__name__
    return name, [(cls.__module__, name)]


def render_kwargs(kwargs, raw=[]):
    if isinstance(raw, basestring):
        raw = [raw]
    raw_items = []
    for key in raw:
        val = kwargs.pop(key, None)
        if val is not None:
            raw_items.append((key, val))
    items = kwargs.items()
    items.sort()
    new_items = []
    for key, val in items:
        new_val = isinstance(val, basestring) and "'%s'" % val or str(val)
        new_items.append((key, new_val))
    new_items.extend(raw_items)
    return ', '.join(['%s=%s' % (k, v) for k, v in new_items])


class FieldCreator(object):
    """
    """

    def __init__(self, id, widget_class, validator_class=None, 
                 widget_kwargs={}, validator_kwargs={}, nullable=True,
                 disabled=False):
        self.id = id
        
        self.widget_class = widget_class
        self.validator_class = validator_class

        self.widget_kwargs = widget_kwargs
        self.validator_kwargs = validator_kwargs

        self.nullable = nullable
        self.disabled = disabled

    def _get_validator_exists(self):
        return not (self.disabled or self.validator_class is None)
    
    validator_exists = property(_get_validator_exists, doc='')
    
    def _get_widget_kwargs(self, **kwargs):
        """
        """
        new_kwargs = self.widget_kwargs.copy()
        new_kwargs.setdefault('id', self.id)
        if self.disabled:
            new_kwargs['disabled'] = True
        new_kwargs.update(kwargs)
        return new_kwargs

    def render_field(self):
        """
        """
        kwargs = self._get_widget_kwargs()
        code = []
        type, imports = get_class_info(self.widget_class)

        if self.validator_exists:
            v_imports, v_code, v_defn = self.render_validator()
            imports.extend(v_imports)
            code.extend(v_code)
            kwargs['validator'] = v_defn

        id = kwargs.pop('id', 'unspecified_id')
        defn = '%s = %s(%s)' % (id, type, 
                                render_kwargs(kwargs, raw='validator'))
        return imports, code, defn

    def get_field(self):
        """
        """
        kwargs = self._get_widget_kwargs()
        validator = self.get_validator()
        return self.widget_class(validator=validator, **kwargs)

    def _get_validator_kwargs(self, **kwargs):
        """
        """
        new_kwargs = self.validator_kwargs.copy()
        if not self.nullable:
            new_kwargs['not_empty'] = True
        new_kwargs.update(kwargs)
        return new_kwargs

    def render_validator(self):
        """
        """
        if self.validator_exists:
            kwargs = self._get_validator_kwargs()
            code = []
            type, imports = get_class_info(self.validator_class)

            defn = len(kwargs) and '%s(%s)' % \
                    (type, render_kwargs(kwargs)) or type
            return imports, code, defn
        return [], [], ''

    def get_validator(self):
        """
        """
        if self.validator_exists:
            kwargs = self._get_validator_kwargs()
            return self.validator_class(**kwargs)
        return None


class SqlAlchemyFieldCreator(FieldCreator):
    """
    """

    def __init__(self, column, widget_class, validator_class=None, 
                 widget_kwargs={}, validator_kwargs={}):
        id = column.name.lower()
        disabled = (column.primary_key and column.autoincrement) or \
                    column.foreign_key
        nullable = column.nullable

        FieldCreator.__init__(self, id, widget_class, validator_class, 
                              widget_kwargs, validator_kwargs, nullable, 
                              disabled)


class SqlAlchemyPropertyFieldCreator(FieldCreator):
    """
    """

    def __init__(self, name, mapper):
        self.property = mapper.properties[name]
        self.options_attrs = []

        table = self.property.select_table

        id_attr = table.primary_key.keys()[0]
        self.options_attrs.append(id_attr)
        name_column = table.columns.get('title', 
                                        table.columns.get('name', None))
        if name_column:
            name_attr = name_column.name
            self.options_attrs.append(name_attr)
            self.options = lambda: [('', '')] + [(getattr(x, id_attr), 
                                    getattr(x, name_attr)) \
                                    for x in table.select().execute()]
        else:
            self.options = lambda: [('',)] + [(getattr(x, id_attr)) \
                                    for x in table.select().execute()]

        if self.property.secondary is None:
            widget = forms.SingleSelectField
            nullable = not len([x for x in self.property.foreign_keys \
                                if not x.nullable])
        else:
            nullable = True
            widget = forms.MultipleSelectField 

        FieldCreator.__init__(self, name, widget, nullable=nullable)

    def get_field(self):
        """
        """
        kwargs = self._get_widget_kwargs(options=self.options)
        return self.widget_class(**kwargs)
        
    def render_field(self):
        """
        """
        kwargs = self._get_widget_kwargs()
        code = []
        type, imports = get_class_info(self.widget_class)

        id = kwargs.pop('id', 'unspecified_id')

        kwargs['options'] = '%s_options' % id
        query_tuple = '(x.%s)' % (', x.'.join(self.options_attrs))
        query_empty = len(self.options_attrs) > 1 and "('', '')" or "('',)"
        mapper = self.property.argument.__name__
        query = '%s_options = lambda: [%s] + [%s for x in ' \
                'model.session_context.current.query(model.%s).list()]' % \
                (id, query_empty, query_tuple, mapper)
        code.append(query)

        defn = '%s = %s(%s)' % (id, type, render_kwargs(kwargs, raw='options'))
        return imports, code, defn


class SqlAlchemyFieldFactory(object):
    """
    """

    def __init__(self, apply_rules=True):
        self.apply_rules = apply_rules
    
    def _get_field_creators(self, mapper):
        """
        """
        if hasattr(mapper, 'mapper'):
            # Deal with assignmapper and Elixir Entities
            mapper = getattr(mapper, 'mapper')

        if not isinstance(mapper, Mapper):
            mapper = class_mapper(mapper)

        fields = []

        table = mapper.local_table
        for column in table.columns:
            field = self.field(column)
            if field is not None:
                fields.append(field) 

        # Mapper must be compiled for proper parsing of property object 
        mapper.compile()
        for name in mapper.properties.iterkeys():
            field = SqlAlchemyPropertyFieldCreator(name, mapper)
            if field is not None:
                fields.append(field)

        return fields

    def generate_form_fields(self, mapper, validators_only=False):
        """
        """
        fields = self._get_field_creators(mapper)
        if validators_only:
            items = [x.get_validator() for x in fields]
            return [x for x in items if x is not None]
        return [x.get_field() for x in fields]

    def render_form_fields(self, mapper, validators_only=False):
        """
        """
        modules = {}
        fields_defns = []
        fields_code = []

        fields = self._get_field_creators(mapper)

        for field in fields:
            if validators_only:
                imports, code, defn = field.render_validator()
            else:
                imports, code, defn = field.render_field()
            fields_defns.append(defn)
            fields_code.extend(code)
            for module, type in imports:
                types = modules.setdefault(module, [])
                if not type in types:
                    types.append(type)

        imports = []
        for module, types in modules.items():
            types.sort()
            imports.append('from %s import %s' % (module, ', '.join(types)))

        return imports, fields_code, fields_defns

    def generate_datagrid(self, mapper, page_size=25):
        """
        """
        raise NotImplementedError()

    [dispatch.generic()]
    def field(self, column):
        """
        Return a field widget creator for the specified column
        """

    [field.when('isinstance(column.type, types.String)')]
    def string_field(self, column):
        kwargs = {}
        v_kwargs = {}

        # Customize field size
        length = column.type.length
        if not length or length > 60:
            widget = forms.TextArea
            rows = not length and 6 or length//50 + 1
            kwargs['rows'] = rows
            kwargs['cols'] = 50 
        else:
            widget = forms.TextField

        if length:
            kwargs['size'] = length
            kwargs['max_size'] = length
            v_kwargs['max'] = length 

        validator = validators.String

        field = SqlAlchemyFieldCreator(column, widget, validator, kwargs, v_kwargs)

        if self.apply_rules:
            id = field.id
            if 'password' in id:
                field.widget_class = forms.PasswordField
            elif 'email' in id:
                field.validator_class = validators.Email
            elif 'url' in id:
                field.validator_class = validators.URL
            elif 'phone' in id and not 'ext' in id:
                field.validator_class = validators.PhoneNumber
            elif 'zip' in id and 'code' in id:
                field.validator_class = validators.PostalCode

        return field

    [field.when('isinstance(column.type, types.String) \
                 and isinstance(column.type, types.Unicode)')]
    def unicode_field(next_method, self, column):
        field = next_method(self, column)
        field.validator_class = validators.UnicodeString
        return field

    [field.when('isinstance(column.type, types.Numeric)')]
    def numeric_field(self, column):
        return SqlAlchemyFieldCreator(column, 
                                      forms.TextField, 
                                      validators.Number)

    [field.when('isinstance(column.type, types.Integer)')]
    def integer_field(self, column):
        return SqlAlchemyFieldCreator(column, 
                                      forms.TextField, 
                                      validators.Int,
                                      widget_kwargs={'size': 10})

    [field.when('isinstance(column.type, types.Boolean)')]
    def boolean_field(self, column):
        return SqlAlchemyFieldCreator(column, 
                                      forms.CheckBox, 
                                      validators.Bool)

    [field.when('isinstance(column.type, types.Binary)')]
    def file_field(self, column):
        return SqlAlchemyFieldCreator(column, 
                                      forms.FileField, 
                                      validators.FieldStorageUploadConverter)

    [field.when('isinstance(column.type, types.Date)')]
    def date_field(self, column):
        return SqlAlchemyFieldCreator(column, 
                                      forms.CalendarDatePicker, 
                                      forms.validators.DateTimeConverter,
                                      validator_kwargs={'format': '%m/%d/%Y'})

    [field.when('isinstance(column.type, types.Time)')]
    def time_field(self, column):
        return SqlAlchemyFieldCreator(column, 
                                      forms.TextField, 
                                      validators.TimeConverter)

    [field.when('isinstance(column.type, types.DateTime)')]
    def datetime_field(self, column):
        format = '%m/%d/%Y %H:%M' 
        return SqlAlchemyFieldCreator(column, 
                                      forms.CalendarDateTimePicker, 
                                      forms.validators.DateTimeConverter,
                                      widget_kwargs={'date_format': format}, 
                                      validator_kwargs={'format': format})


def generate_form_fields(mapper, apply_rules=True):
    """
    """
    factory = SqlAlchemyFieldFactory(apply_rules)
    return factory.generate_form_fields(mapper)


def render_form_fields(mapper, apply_rules=True):
    """
    """
    factory = SqlAlchemyFieldFactory(apply_rules)
    return factory.render_form_fields(mapper)


