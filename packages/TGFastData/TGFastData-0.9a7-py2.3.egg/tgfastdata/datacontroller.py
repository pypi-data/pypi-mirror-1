#import logging
import re

from turbogears import widgets, database, validators
import turbogears
import formmaker
from datawidgets import FastDataGrid, EditForm
import cherrypy
import simplejson
import formencode
from sqlobject import SQLObjectNotFound, IN
from sqlobject.sresults import SelectResults
from sqlobject.sqlbuilder import SQLExpression

#log = logging.getLogger("fastdata")

def join_items(sobj):
    d = {}
    for join in database.so_joins(sobj):
        attr_name = join.joinMethodName
        d[attr_name] = list(getattr(sobj, attr_name))
    return d

_mangle_rx = re.compile(r'_.')
def col2attrname(name):
    if name.endswith('_id'):
        name = name[:-3]
    return _mangle_rx.sub(lambda x: x.group(0)[1].upper(), name)

class BaseDataController(object):
    sql_class = None
    getter = None

    def __init__(self, sql_class=None, id_column=None, list_filter=None):
        if not (self.sql_class or sql_class):
            raise ValueError("You must set an sql_class to use a DataController")
        if sql_class:
            self.sql_class = sql_class
        if id_column:
            getterName = sql_class.sqlmeta.columns[id_column].alternateMethodName
            self.getter = getattr(self.sql_class, getterName)
        else:
            self.getter = self.sql_class.get
        self._list_filter = list_filter

    def _get_item(self, atom):
        '''
        Hook to allow retrieval by something other than meaningless (lame)
        integer primary key.
        '''
        # Coerce the ID to the correct db type
        try:
            #id = int(atom)
            return self.getter(int(atom))
        except SQLObjectNotFound:
            return None

    def default(self, *vpath, **params):
        """Do RESTful-style access to database objects. Based on
        the RESTful resource recipe by Robert Brewer."""
        if not vpath:
            return self.index(**params)
        # Make a copy of vpath in a list
        vpath = list(vpath)
        atom = vpath.pop(0)

        # See if the first virtual path member is a container action
        method = getattr(self, atom, None)
        if method and getattr(method, "expose_container"):
            return method(*vpath, **params)

        # Not a container action; the URI atom must be an existing ID
        item = self._get_item(atom)
        if item is None:
            raise cherrypy.NotFound

        # There may be further virtual path components.
        # Try to map them to methods in this class.
        if vpath:
            method = getattr(self, vpath[0], None)
            if method and getattr(method, "exposed"):
                return method(item, *vpath[1:], **params)

        # No further known vpath components. Call a default handler.
        return self.show(item, *vpath, **params)
    default = turbogears.expose()(default)
    
    def _filterJoins(self, obj, data):
        # check if the object has joins
        jdata = []
        for join in database.so_joins(self.sql_class):
            jname = join.joinMethodName
            # is join data present in the form?
            if jname in data.keys():
                # keep the data and update joins after object's update
                jdata.append((join, data.pop(jname)))
        return data, jdata
    
    def _updateJoins(self, obj, jdata):
        obj_id = getattr(obj, obj.sqlmeta.idName)
        for join, data in jdata:
            jname = join.joinMethodName
            addRelation = 'add' + join.addRemoveName
            removeRelation = 'remove' + join.addRemoveName
            if join.hasIntermediateTable(): 
                # many-to-many join
                # remove all relations
                relations = getattr(obj, jname)
                for relation in relations:
                    getattr(obj, removeRelation)(relation)
                # add selected relations
                if data:
                    relations = join.otherClass.select(IN(join.otherClass.q.id, data))
                    for relation in relations:
                        getattr(obj, addRelation)(relation)
            else:
                # one-to-many
                # get all current relations
                oldrelations = set(getattr(obj, jname))
                newrelations = []
                # KLUDGE: get attribute name of related class
                # referring to this class
                join_attr = col2attrname(join.joinColumn)
                for item in data:
                    try:
                        newrelation = join.otherClass.get(item)
                    except SQLObjectNotFound:
                        raise ValueError, 'Invalid ID for related object.'
                    else:
                        if newrelation not in oldrelations:
                            setattr(newrelation, join_attr, obj)
                        newrelations.append(newrelation)
                for relation in oldrelations.difference(newrelations):
                    setattr(relation, join_attr, None)
    
    def _update(self, obj=None, **data):
        data, join_data = self._filterJoins(self.sql_class, data)
        #log.debug(data)
        if obj:
            obj.set(**data)
        else:
            obj = self.sql_class(**data)
        self._updateJoins(obj, join_data)
        return obj

    def _get_instances(self):
        if self._list_filter:
            lfilter = self._list_filter
            if isinstance(lfilter, SelectResults):
                return lfilter
            if callable(lfilter):
                lfilter = lfilter()
            if isinstance(lfilter, (SQLExpression, basestring)):
                lfilter = self.sql_class.select(lfilter)
            return lfilter
        else:
            return self.sql_class.select()

class AjaxDataController(BaseDataController):
    '''
    A DataController specifically for use with Ajax requests.
    '''

    def __init__(self, sql_class=None, id_column=None, schema=None):
        super(AjaxDataController,self).__init__(sql_class, id_column)
        self.schema= schema
    
    def _read_incoming_data():
        '''
        Returns a tuple containing the incoming data and any errors
        '''
        values = simple_json.load(cherrypy.request.body)
        if self.schema:
            try:
                values= self.schema.to_python( values )
            except validators.Invalid, e:
                errors= {}
                for key,error in e.error_dict.items():
                    errors[key]= dict(message=str(error), invalid_value=e.value)
                # Return error code and info
                cherrypy.response.status=400 # Bad request
                return (None,errors)
        return (values,None)
        
    def index(self):
        return dict(objects=self._get_instances(), errors=None )
    index = turbogears.expose( format="json" )(index)

    def create(self, **data):
        obj_data,errors= self._read_incoming_data()
        if errors:
            cherrypy.response.status=400 # Bad request
            return dict( id=None, errors=errors )
            
        obj= self.sql_class(obj_data)
        return dict( id=obj.id, errors=None )
    create = turbogears.expose( format="json" )(create)

    def update(self, obj, **data):
        obj_data,errors= self._read_incoming_data()
        if errors:
            cherrypy.response.status=400 # Bad request
            return dict( id=obj.id, errors=errors )
        # If the update data specifies an ID, it *must* match the object's ID.
        if "id" in obj_data:
            if obj_data["id"]!=obj.id:
                # IDs don't match. Can't update this object.
                cherrypy.response.status=409 # Conflict
                return dict( id=obj.id,
                             errors= dict( id=dict( message="Object ID invalid",
                                                    value=obj_data["id"] ) ) )
            # IDs match, but we don't need to update the ID.
            del obj_data["id"]
        # Validate/convert the JSON data to data ready for SQLObject    
        errors= dict()
        for key in obj_data.keys():
            try:
                col= obj.sqlmeta.columns[key]
                validator= col.validator
                values[key] = validator.to_python( obj_data[key], None )
            except formencode.Invalid, e:
                # if the value doesn't validate correctly, then note it
                errors[key]= dict( message=str(e), invalid_value=e.value )
            except KeyError:
                # remove entries in updateValues that don't appear in the object
                del obj_data[key]
        # If any values didn't validate correctly, return a Bad Request (400)
        # status code and indicate the errors.
        if errors:
            cherrypy.response.status=400 # Bad request
            return dict( id=obj.id, errors=errors )
        # Update the SQLObject object
        obj.set( obj_data )
        return dict( id=obj.id, errors=None )
    update = turbogears.expose( format="json" )(update)
        
    def delete(self, obj):
        obj.destroySelf()
        return dict( id=obj.id, errors=None )
    delete = turbogears.expose( format="json" )(delete)

    def show(self, obj):
        return dict( object=obj, errors=None )
    show = turbogears.expose( format="json" )(show)

class DataController(BaseDataController):
    """Provides basic add/edit/delete capability"""
    list_widget = FastDataGrid()
    form_widget_class = EditForm
    form_template = "tgfastdata.templates.form"
    list_template = "tgfastdata.templates.list"
    item_template = "tgfastdata.templates.item"
    form_fields = None
    list_fields = None
    object_name = 'Record'

    def __init__(self, sql_class=None, form_widget_class=None, id_column=None,
            list_widget=None, form_widget=None, object_name=None,
            form_template=None, list_template=None, item_template=None,
            form_fields=None, list_fields=None, list_filter=None):
        super(DataController,self).__init__(sql_class, id_column, list_filter)

        if list_fields:
            self.list_fields = list_fields
        if form_fields:
            self.form_fields = form_fields
        if form_widget_class:
            self.form_widget_class = form_widget_class
        if form_widget:
            self.form_widget = form_widget
            self.form_widget_class = form_widget.__class__
        else:
            self.form_widget = self.form_widget_class(
                fields=formmaker.fields_for(self.sql_class, self.form_fields))
        if object_name:
            self.object_name = object_name
        if list_widget:
            self.list_widget = list_widget
        elif self.list_fields:
            self.list_widget = FastDataGrid(self.list_fields or self.form_fields)
        if form_template:
            self.form_template = form_template
        if list_template:
            self.list_template = list_template
        if item_template:
            self.item_template = item_template

    def _get_form(self):
        return self.form_widget

    def index(self):
        return dict(tg_template=self.list_template,
            list_widget=self.list_widget,
            data=self._get_instances())
    index = turbogears.expose()(index)

    def add(self):
        return dict(tg_template=self.form_template,
            obj=None, form=self.form_widget, action="create")
    add = turbogears.expose()(add)

    add.expose_container = True

    def create(self, **data):
        self._update(**data)
        turbogears.flash("%s Added!" % self.object_name)
        turbogears.redirect('./')
    create = turbogears.expose()(create)
    create = turbogears.validate(form=_get_form)(create)
    create = turbogears.error_handler(add)(create)

    def edit(self, obj):
        values = database.so_to_dict(obj)
        values.update(join_items(obj))
        return dict(tg_template=self.form_template, form=self.form_widget,
                    obj=values, action="update")
    edit = turbogears.expose()(edit)

    def update(self, obj, **data):
        self._update(obj, **data)
        turbogears.flash("Changes Saved!")
        turbogears.redirect('../')
    update = turbogears.expose()(update)
    update = turbogears.validate(form=_get_form)(update)
    update = turbogears.error_handler(edit)(update)

    def delete(self, obj):
        obj.destroySelf()
        turbogears.flash("%s deleted!" % self.object_name)
        turbogears.redirect('../')
    delete = turbogears.expose()(delete)
    
    def show(self, obj):
        value = database.so_to_dict(obj)
        columns = obj.sqlmeta.columns
        if self.form_fields:
            column_keys = self.form_fields
        else:
            column_keys = columns.keys()
        # Get the title from the sqlcolumn
        column_list = [ 
            (formmaker.column_parms(columns[key])['label'], key)
            for key in column_keys
        ]
        value["tg_columns"] = column_list
        value["tg_template"] = self.item_template
        return value
    show = turbogears.expose()(show)
