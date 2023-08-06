##############################################################################
#
# Copyright (c) 2006-2008 Kapil Thangavelu <kapil.foss@gmail.com>
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""
Model Descriptions

$Id: model.py 299 2008-05-23 20:31:48Z kapilt $
"""

from zope import interface, component
from zope.interface.interfaces import IInterface
from interfaces import IIModelInterface, IModelDescriptor, IModelDescriptorField

def queryModelInterface( klass ):
    if not IInterface.providedBy( klass ):
        ifaces = filter( IIModelInterface.providedBy, list( interface.implementedBy( klass ) ) )
        assert len(ifaces), "No Model Interface on Domain Object"
        assert len(ifaces)==1, "Multiple Model Interfaces on Domain Object"
        klass = ifaces[0]
    else:
        assert IIModelInterface.providedBy( klass ), "Invalid Interface"
    return klass
    
def queryModelDescriptor( ob ):
    if not IInterface.providedBy( ob ):
        ob = filter( IIModelInterface.providedBy, list( interface.implementedBy( ob ) ) )[0]    
    name = "%s.%s"%(ob.__module__, ob.__name__)    
    return component.queryAdapter( ob, IModelDescriptor, name )
    
class Field( object ):

    interface.implements( IModelDescriptorField )

    name = ""        # field name
    label = ""       # title for field
    description = "" # description for field
    fieldset = "default"    
    modes = "edit|view|add" # see _valid modes for allows values, also can be done as bool keyword args
    omit = False
    required = False  # required flag can only be used if the field is not required by the database.
    property = None
    
    view_permission = "zope.Public"
    edit_permission = "zope.ManageContent"
    
    view_widget = None    # zope.app.form.interaces.IDisplayWidget
    edit_widget = None    # zope.app.form.interfaces.IInputWidget
    listing_column = None # zc.table.interfaces.IColumn object
    add_widget     = None # zope.app.form.interfaces.IInputWidget object
    search_widget  = None # zope.app.form.interfaces.IInputWidget object

    # for relations, we want to enable grouping them together based on
    # model, this attribute specifies a group. the relation name will be
    # used on a vocabulary. perhaps an example is cleaner, so say we
    # have a movie object with separate relations to directors and actors
    # if we specify both as group 'People', we inform the view machinery
    # to create a single relation viewlet, that displays and edits
    # via a single provider with a vocabulary for the relation.
    group = None
    
    _valid_modes = ('edit', 'view', 'read', 'add', 'listing', 'search')
    
    # track kw arguements consumed when used in from dict mode
    consumed = ()
    
    def get( self, k, default=None):
        return self.__dict__.get(k, default )

    def __getitem__( self, k ):
        return self.__dict__[k]
    
    @classmethod    
    def fromDict( cls, kw):
        d = {}
        if kw.get('property') and kw.get('omit'):
            raise SyntaxError("can't specify property and omit for field %s"%kw.get('name'))
            
        modes = filter(None, kw.get('modes', cls.modes).split("|"))
        consumed = []
        for k in kw:
            if k in cls._valid_modes:
                if kw[k]:
                    if not k in modes:
                        modes.append( k )
                elif k in modes:
                    modes.remove( k )
            elif k in cls.__dict__:
                d[k] = kw[k]
            else:
                raise SyntaxError(k)
            consumed.append(k)
            
        if kw.get('omit'):
            modes = ()
        d['modes'] = "|".join( modes )
        instance = cls()
        instance.consumed = consumed
        for k,v in d.items():
            setattr( instance, k, v )
        return instance
    
    
class ModelDescriptor( object ):
    """
    Annotations for table/mapped objects, to annotate as needed, the notion
     is that the annotation keys correspond to column, and values correspond
    to application specific column metadata.

    edit_grid = True # editable table listing
    
    # filtering perms on containers views as well
    
    use for both sa2zs and zs2sa
    
    fields = [
      dict( name='title', 
            edit=True,
            edit_widget = ""
            view=True,
            view_widget = ""
            listing=True, 
            listing_column=""
            search=True,
            search_widget=""
            fieldset="default"
            modes="edit|view|add|search|listing"
            read_widget=ObjectInputWidget,
            write_widget=ObjectEditWidget,
            read_permission="zope.View", 
            write_permission="zope.WritePermission" ),
      dict( name="id", omit=True )
    ]
    """

    interface.implements( IModelDescriptor )
    
    _marker = object()
    
    fields = () # sequence of mapping to field
    properties = ()
    schema_order = ()
    schema_invariants = ()
    
    def __init__( self ):
        self.fields = [ Field.fromDict( info ) for info in self.fields]
    
    def __call__( self, iface ):
        """ 
        models are also adapters for the underlying objects
        """
        return self
    
    def get( self, name, default=None ):
        for info in self.fields:
            if info.name == name:
                return info
        return default

    def keys( self ):
        for info in self.fields:
            yield info.name
        
    def __getitem__(self, name):
        value =  self.get( name, self._marker )
        if value is self._marker:
            raise KeyError( name)
        return value

    def values( self ):
        for info in self.fields:
            yield info

    def __contains__(self, name ):
        return not self._marker == self.get( name, self._marker )

    @property
    def listing_columns( self ):
        return [f.name for f in self.fields if 'listing' in f.modes]

    @property
    def search_columns( self ):
        return [f for f in self.fields if 'search' in f.modes]

    @property
    def edit_columns( self ):
        return [f for f in self.fields if 'edit' in f.modes]

    @property
    def add_columns( self ):
        return [f for f in self.fields if 'add' in f.modes]

    @property
    def view_columns( self ):
        return [f  for f in self.fields if 'view' in f.modes]
