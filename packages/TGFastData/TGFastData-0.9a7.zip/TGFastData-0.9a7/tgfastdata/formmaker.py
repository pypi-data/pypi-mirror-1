#import logging

from turbogears import widgets
from turbogears import validators
from tgfastdata.datawidgets import (DataCheckBoxList, DataSelectField, 
  EmptyStringConverter, JoinSelect,
  #LoggingValidator,
  SaneCalendarDatePicker,  SaneDateConverter)
import dispatch
import re
from sqlobject import col, joins, classregistry
from turbogears.database import so_columns, so_joins

#log = logging.getLogger("fastdata")

def column_widget(column):
    pass
column_widget = dispatch.generic()(column_widget)

def name2label(name):
    """
    Convert a column name to a Human Readable name.
    """
    # Create label from the name:
    #   1) Convert _ to spaces
    #   2) Convert CamelCase to Camel Case
    #   3) Upcase first character of Each Word
    # Note: I *think* it would be thread-safe to
    #       memoize this thing.
    return ' '.join([s.capitalize() for s in
               re.findall(r'([A-Z][a-z0-9]+|[a-z0-9]+|[A-Z0-9]+)', name)])

def column_parms(column):
    """
    Helper function to convert column attributes to
    parameters needed to initialize a widget.
    """
    parms = { 'name' : column.name }
    if column.title:
        parms['label'] = column.title
    else:
        if isinstance(column, col.SOKeyCol) and column.name[-2:] == 'ID':
            parms['label'] = name2label(column.name[:-2])
        else:
            parms['label'] = name2label(parms['name'])
    if column.default != col.NoDefault:
        parms['default'] = column.default
    return parms

def validator_parms(column):
    """
    Helper function to convert column properties to
    parameters needed to create validators for its wiget.
    """
    parms = {}
    parms['not_empty'] = column.notNone
    if hasattr(column, 'length') and isinstance(column, 
      (col.SOUnicodeCol, col.SOStringCol)):
        parms['max'] = column.length
    return parms

def column_widget_generic_col(column):
    parms = column_parms(column)
    vparms = validator_parms(column)
    if vparms.get('not_empty'):
        parms['validator'] = validators.NotEmpty()
    return widgets.TextField(**parms)
column_widget_generic_col = column_widget.when(
        "isinstance(column, col.SOCol)")(column_widget_generic_col)

def column_widget_int_col(column):
    parms = column_parms(column)
    vparms = validator_parms(column)
    parms['validator'] = validators.Int(**vparms)
    return widgets.TextField(**parms)
column_widget_int_col = column_widget.when(
        "isinstance(column, col.SOIntCol)")(column_widget_int_col)

def column_widget_float_col(column):
    parms = column_parms(column)
    vparms = validator_parms(column)
    parms['validator'] = validators.Number(**vparms)
    return widgets.TextField(**parms)
column_widget_float_col = column_widget.when(
        "isinstance(column, (col.SOFloatCol))")(column_widget_float_col)
    
def column_widget_string_col(column):
    parms = column_parms(column)
    vparms = validator_parms(column)
    if isinstance(column, col.SOStringCol):
        parms['validator'] = validators.String(**vparms)
    elif isinstance(column, col.SOUnicodeCol):
        #parms['validator'] = LoggingValidator(**vparms)
        parms['validator'] = validators.UnicodeString(**vparms)
    if column.length:
        return widgets.TextField(**parms)
    else:
        return widgets.TextArea(rows=7, cols=50, **parms)
column_widget_string_col = column_widget.when(
        "isinstance(column, col.SOStringLikeCol)")(column_widget_string_col)

def column_widget_enum_col(column):
    parms = column_parms(column)
    vparms = validator_parms(column)
    parms['options'] = [(value, value) for value in column.enumValues ]
    parms['validator'] = validators.OneOf(column.enumValues, **vparms)
    return widgets.SingleSelectField(**parms)
column_widget_enum_col = column_widget.when(
        "isinstance(column,col.SOEnumCol)")(column_widget_enum_col)
        
def column_widget_date_col(column):
    parms = column_parms(column)
    vparms = validator_parms(column)
    # CalendarDatePicker uses wrong (DateTimeConverter) validator
    # so we set up our own
    parms['validator'] = SaneDateConverter(**vparms)
    if vparms.get('format'):
        parms['format'] = vparms['format']
    return SaneCalendarDatePicker(**parms)
column_widget_date_col = column_widget.when(
        "isinstance(column,col.SODateCol)")(column_widget_date_col)

def column_widget_datetime_col(column):
    parms = column_parms(column)
    vparms = validator_parms(column)
    # CalendarDateTimePicker supports 'not_empty' argument to set up validator
    parms['not_empty'] = vparms.get('not_empty', False)
    return widgets.CalendarDateTimePicker(**parms)
column_widget_datetime_col = column_widget.when(
        "isinstance(column,col.SODateTimeCol)")(column_widget_datetime_col)

def column_boolean_col(column):
    parms = column_parms(column)
    # Boolean fields can have no validator, because unchecked fields
    # don't submit a value and are therefore False
    return widgets.CheckBox(**parms)
column_boolean_col = column_widget.when("isinstance(column, col.SOBoolCol)")(column_boolean_col)

def column_widget_fkey_col(column):
    parms = column_parms(column)
    fkey_class = classregistry.findClass(column.foreignKey)
    items = fkey_class.select()
    # make options a callable to retrieve fresh data 
    # every time the widget is rendered
    parms['options'] = lambda: [(None, '')] + \
        [(item.id, unicode(item)) for item in items]
    vparms = validator_parms(column)
    parms['validator'] = EmptyStringConverter(**vparms)
    widget = DataSelectField(**parms)
    widget.validator
    return widget
column_widget_fkey_col = column_widget.when(
        "isinstance(column,col.SOKeyCol)")(column_widget_fkey_col)

def join_widget(join):
    pass
join_widget = dispatch.generic()(join_widget)

def join_parms(join):
    """
    Helper function to convert join attributes to
    parameters needed to initialize a widget.
    """
    parms = { 'name' : join.joinMethodName, 
              'label' : name2label( join.joinMethodName) }
    return parms

def join_widget_multiple_col(join):
    parms = join_parms(join)
    items = join.otherClass.select()
    # make options a callable to retrieve fresh data 
    # every time the widget is rendered
    parms['options'] = lambda: [(item.id, unicode(item)) for item in items]
    parms['attrs'] = dict(size=8)
    return JoinSelect(**parms)
join_widget_multiple_col = join_widget.when(
    "isinstance(join, joins.SOMultipleJoin)")(join_widget_multiple_col)

def join_widget_related_col(join):
    parms = join_parms(join)
    items = join.otherClass.select()
    # make options a callable to retrieve fresh data 
    # every time the widget is rendered
    parms['options'] = lambda: [(item.id, unicode(item)) for item in items]
    parms['attrs'] = dict(size=8)
    return JoinSelect(**parms)
join_widget_related_col = join_widget.when(
    "isinstance(join, joins.SORelatedJoin)")(join_widget_related_col)


def fields_for(sqlclass, fields=None):
    sqlclass_columns = so_columns(sqlclass)
    sqlclass_joins = so_joins(sqlclass)
    if fields:
        columnlist = fields
    elif hasattr(sqlclass, "form_order"):
        columnlist = sqlclass.form_order
    else:
        columnlist = sqlclass_columns.keys() + \
          [join.joinMethodName for join in sqlclass_joins]
    widgetlist = []
    for column in columnlist:
        widget = None
        if sqlclass_columns.has_key(column):
            widget = column_widget(sqlclass_columns[column])
        elif sqlclass_columns.has_key(column + 'ID'): #key column
            widget = column_widget(sqlclass_columns[column + 'ID'])
        else:
            for join in sqlclass_joins:
                if join.joinMethodName == column:
                    widget = join_widget(join)
                    break
        if not widget:
            raise Exception, "Join or column %r not found in class %r" % (column, sqlclass.__name__)
        widgetlist.append(widget)
    return widgetlist

def sqlwidgets(sqlclass, fields=None):
    import warnings
    warnings.warn("Use fields_for() rather than sqlwidgets().", DeprecationWarning, 2)
    return fields_for(sqlclass, fields)
