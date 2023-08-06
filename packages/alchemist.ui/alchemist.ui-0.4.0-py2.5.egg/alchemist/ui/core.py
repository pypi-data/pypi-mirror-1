"""
$Id:$

Base class and functions for encaspulating dynamic fields,
form styling, and form name.

"""
import time, copy, math, itertools
from zope import interface, schema
from zope.formlib import form
from zope.formlib.namedtemplate import NamedTemplate
from zc.table import column

from sqlalchemy import orm
from sqlalchemy.orm import properties
from ore.alchemist import model, Session
from ore.alchemist.interfaces import IAlchemistContent

import pytz, datetime
import zope.event
from zope import security
from zope.security.proxy import removeSecurityProxy
from zope.lifecycleevent import Attributes
from zope.lifecycleevent import ObjectModifiedEvent

from zope.interface.common import idatetime
from zope.i18nmessageid import MessageFactory

_ = MessageFactory('zope')

class Getter( object ):
    def __init__(self, getter):
        self.getter = getter

    def __call__( self, item, formatter):
        return self.getter( item )
        
class DateGetter( object ):
    def __init__( self, getter, format="%d %B %Y %r" ):
        self.getter = getter
        self.format = format
    def __call__( self, item, formatter):
        value = self.getter( item )
        if not value:
            return "N/A"
        return value.strftime( self.format )

def filterFields( context, fields, mode ):
    """
    filter form fields, context should be an instance of the class.

    field mode should be in set of ('add', 'edit', 'search', 'view')
    
    There's a different set of use cases around field filtering,
    which involves editable, then readable, then omit based on
    permissions, but its a more involved as a use case with formlib
    """
    unwrapped = removeSecurityProxy( context )
    descriptor = model.queryModelDescriptor( unwrapped )

    check = mode in ('add', 'edit') \
            and security.canWrite or security.canAccess
    
    omit_names = []
    
    for f in fields:
        if check( context, f.__name__ ):
            continue
        omit_names.append( f.__name__)

    return fields.omit( *omit_names )
    
def setUpFields( domain_model, mode ):
    """
    setup form fields for add/edit/view/search modes, with custom widgets
    enabled from model descriptor. this expects the domain model and mode
    passed in and will return a form.Fields instance
    """
    
    domain_model = removeSecurityProxy( domain_model )
    t = time.time()

    domain_interface = model.queryModelInterface( domain_model )
    domain_annotation = model.queryModelDescriptor( domain_interface )

    search_mode = mode == 'search'

    if not domain_annotation:
        if search_mode:
            form_fields = form.Fields( *setUpSearchFields( domain_interface ) )
        else:
            form_fields = form.Fields( domain_interface )
        return form_fields

    fields = []
    columns = getattr( domain_annotation, '%s_columns'%mode )
    

    
    for field_info in columns:
        if not field_info.name in domain_interface:
            #print "bad field", field_info.name, domain_interface.__name__
            continue
        custom_widget = getattr( field_info, "%s_widget"%mode )
        if search_mode:
            fields.append(
                form.Field( setUpSearchField( domain_interface[ field_info.name ] ),
                            custom_widget = custom_widget )
                )
        else:
            fields.append(
                form.Field( domain_interface[ field_info.name ],
                            custom_widget = custom_widget )
                )
    form_fields = form.Fields( *fields )
    #print "field setup cost", time.time()-t    
    return form_fields


def setWidgetErrors( widgets, errors ):
    for widget in widgets:
        name = widget.context.getName()
        for error in errors:
            if isinstance(error, interface.Invalid) and name in error.args[1:]:
                if widget._error is None:
                    widget._error = error

def setUpColumns( domain_model ):
    """
    use model descriptor on domain model extract columns for table listings
    """
    columns = []
    domain_interface = model.queryModelInterface( domain_model )

    if not domain_interface:
        raise SyntaxError("Model must have domain interface %r"%(domain_model ) )

    domain_annotation = model.queryModelDescriptor( domain_interface )
    
    field_column_names = domain_annotation and domain_annotation.listing_columns \
                         or schema.getFieldNamesInOrder( domain_interface )

    # quick hack for now, dates are last in listings
    remainder = []
    
    for field_name in field_column_names:
        if not field_name in domain_interface:
            # we can specify additional columns for tables that are not present in the
            # the interface, iff they are fully spec'd as columns in the descriptor/annotation
            if domain_annotation \
                and field_name in domain_annotation \
                    and domain_annotation[ field_name ].listing_column:
                pass
            else:
                #print "bad field, container", field_name, domain_interface.__name__
                continue
            
        info = domain_annotation and domain_annotation.get( field_name ) or None
        
        if info is not None and info.listing_column:
            columns.append(
                info.listing_column
                )
            continue

        field = domain_interface[ field_name ]
        
        if isinstance( field, schema.Datetime ):
            remainder.append( 
                column.GetterColumn( title=field.title or field.__name__,
                                     getter=DateGetter( field.query ) )
                )
            continue
        columns.append(
            column.GetterColumn( title= ( field.title or field.__name__ ),
                                 getter = Getter( field.query ) )
            )
    columns.extend( remainder )
    return columns

def setUpSearchFields( iface ):
    " search fields shouldn't be required "
    fields = []
    for name, field in schema.getFieldsInOrder( iface ):
        if field.required:
            field = copy.deepcopy( field )
            field.required = False
        fields.append( field )
    return fields

def setUpSearchField( field ):
    " search fields shouldn't be required "    
    if not field.required:
        return field
    field = copy.deepcopy( field )
    field.required = False
    return field

def constructQuery( form_fields, domain_class, data ):
    d = {}
    for form_field in form_fields:
        field = form_field.field
        v = data.get( field.__name__ )
        if not v:
            continue
        if isinstance( field, (schema.Text, schema.ASCII)):
            # automatically convert text/schema fields into wildcards
            v = getattr(domain_class, field.__name__).like('%'+v+'%')
        else:
            v = getattr( domain_class, field.__name__) == v
        d[ field.__name__ ] = v
    return d

def getSelected( selection_column, request ):
    """
    the formlib selection column implementation wants us to pass a value
    set.. lame. we manually poke at it to get ids and dereference.

    these pair of functions assume single column integer primary keys
    """
    keys = [ k[len(selection_column.prefix):].decode('base64') \
             for k in request.form.keys() \
             if k.startswith( selection_column.prefix )  \
             and request.form.get(k,'') == 'on']
    return map( int, keys )    

def getSelectedObjects( selection_column, request, domain_model ):
    keys = getSelected( selection_column, request)
    session = Session()
    return filter( None, [ session.get( domain_model, k) for k in keys] )
    
def null_validator( form, action, data ):
    return ()
    
class BaseForm( form.FormBase ):
    
    template = NamedTemplate('alchemist.form')        
    
    def invariantErrors( self ):
        errors = []
        for error in self.errors:
            if isinstance( error, interface.Invalid ):
                errors.append( error )
        return errors


def columns( mapper ):
    for p in mapper.iterate_properties:
        if isinstance( p, properties.ColumnProperty ):
            yield p

def unique_columns( mapper ):
    for cp in columns( mapper ):
        for c in cp.columns:
            if c.unique:
                yield cp.key, c
            
class DynamicFields( object ):

    mode = None # required string attribute
    template = NamedTemplate('alchemist.form')
    form_fields = form.Fields()

    def getDomainModel( self ):
        return getattr( self.context, 'domain_model', self.context.__class__)
    
    def update( self ):
        """
        override update method to setup fields dynamically before widgets are
        setup and actions called.
        """
        domain_model = self.getDomainModel()
        self.form_fields = setUpFields( domain_model, self.mode )
        super( DynamicFields, self).update()
        setWidgetErrors( self.widgets, self.errors )
        
    @property
    def form_name( self ):
        # play nice w/ containers or content views, or content
        domain_model = getattr( self.context, 'domain_model', None)
        if domain_model is None:
            domain_model = getattr( self, 'domain_model', None)
            if domain_model is None and IAlchemistContent.providedBy( self.context ):
                domain_model = self.context.__class__
        if domain_model is None:
            return self.mode.title()
        return "%s %s"%(self.mode.title(), domain_model.__name__)

    def splitwidgets( self ):
        """
        return two lists of form fields split into two, int overflow into
        first column.
        """
        # give first and second set of field names
        field_count = len( self.form_fields )
        first_half_count = math.ceil( field_count / 2.0 )
        first_half_widgets, second_half_widgets = [], []
        
        for idx, field in itertools.izip( itertools.count(), self.form_fields ):
            if idx < first_half_count:
                first_half_widgets.append( self.widgets[ field.__name__ ] )
            else:
                second_half_widgets.append( self.widgets[ field.__name__ ] )

        return first_half_widgets, second_half_widgets

    def validateUnique( self, action, data ):
        """
        verification method for adding or editing against anything existing
        that conflicts with an existing row, as regards unique column constraints.
        
        this is somewhat costly as we basically reinvoke parsing form data twice,
        we need to extend zope.formlib to ignore existing values in the data dictionary
        to avoid this.
        
        its also costly because we're doing a query per unique column data we find, in
        order to unambigously identify the field thats problematic. but presumably those
        are very fast due to the unique constraint.
        
        TODO : assumes column == attribute         
        """
        errors = form.getWidgetsData( self.widgets, self.prefix, data ) + \
                 form.checkInvariants(self.form_fields, data) 
        if errors:
            return errors
        
        domain_model = removeSecurityProxy( self.getDomainModel() )
        
        # find unique columns in data model.. TODO do this statically
        mapper = orm.class_mapper( domain_model  )
        ucols = list( unique_columns( mapper ) )

        errors = []
        # query out any existing values with the same unique values,
        
        s = Session()        
        # find data matching unique columns
        for key, col in ucols:
            if key in data:
                # on edit ignore new value if its the same as the previous value
                if isinstance( self.context, domain_model ) \
                   and data[key] == getattr( self.context, key, None):
                   continue
                
                value = s.query( domain_model ).filter( col == data[key] ).count()
                if not value:
                    continue
                
                widget = self.widgets[ key ]
                error = form.WidgetInputError( widget.name, 
                                               widget.label, 
                                              u"Duplicate Value for Unique Field" )
                widget._error = error
                errors.append( error )
        
        if errors:
            return tuple(errors)

# formlib 3.5.0 backports.. these variants will send field descriptions on edit

def handle_edit_action(self, action, data):
    descriptions = applyData(self.context, self.form_fields, data,
                             self.adapters)
    if descriptions:
        descriptions = [Attributes(interface, *tuple(keys))
                        for interface, keys in descriptions.items()]
        zope.event.notify(ObjectModifiedEvent(self.context, *descriptions))
        formatter = self.request.locale.dates.getFormatter(
            'dateTime', 'medium')
        try:
            time_zone = idatetime.ITZInfo(self.request)
        except TypeError:
            time_zone = pytz.UTC
            
        status = _("Updated on ${date_time}",
                   mapping={ 'date_time':
                             formatter.format( datetime.datetime.now(time_zone) ) }
                   )
        self.status = status
    else:
        self.status = _('No changes')
        
def applyData(context, form_fields, data, adapters=None):
    if adapters is None:
        adapters = {}

    descriptions = {}

    for form_field in form_fields:
        field = form_field.field
        # Adapt context, if necessary
        interface = form_field.interface
        adapter = adapters.get(interface)
        if adapter is None:
            if interface is None:
                adapter = context
            else:
                adapter = interface(context)
            adapters[interface] = adapter

        name = form_field.__name__
        newvalue = data.get(name, form_field) # using form_field as marker
        if (newvalue is not form_field) and (field.get(adapter) != newvalue):
            descriptions.setdefault(interface, []).append(field.__name__)
            field.set(adapter, newvalue)

    return descriptions            
