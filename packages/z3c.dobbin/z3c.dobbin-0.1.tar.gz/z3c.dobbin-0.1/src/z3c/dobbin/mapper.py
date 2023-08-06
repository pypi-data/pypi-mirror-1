from zope import interface
from zope import schema
from zope import component

from zope.dottedname.resolve import resolve

from interfaces import IMapper
from interfaces import IMapped

import sqlalchemy as rdb
from sqlalchemy import orm
from sqlalchemy.orm.attributes import proxied_attribute_factory

from ore.alchemist.interfaces import IDatabaseEngine
from ore.alchemist import Session
from ore.alchemist.zs2sa import FieldTranslator
from ore.alchemist.zs2sa import StringTranslator

import bootstrap
import factory

from itertools import chain

import types

from session import getTransactionManager

class ObjectTranslator(object):
    def __init__(self, column_type=None):
        self.column_type = column_type

    def __call__(self, field, metadata):
        return rdb.Column(
            field.__name__+'_uuid', rdb.String(length=32), nullable=False)

class ObjectProperty(object):
    """Object property.

    We're not checking type here, because we'll only be creating
    relations to items that are joined with the soup.
    """
    
    def __call__(self, field, column, metadata):
        relation_name = field.__name__+'_relation'
        
        def _get(self):
            item = getattr(self, relation_name)

            # try to acquire relation target from session
            session = Session()

            try:
                return session._d_pending[item.uuid]
            except (AttributeError, KeyError):
                pass

            # bootstrap item
            return bootstrap.build(item.spec, item.uuid)

        def _set(self, item):
            if not IMapped.providedBy(item):
                # create instance
                instance = factory.create(item.__class__)

                # set attributes
                for iface in interface.providedBy(item):
                    for name in iface.names():
                        value = getattr(item, name)
                        setattr(instance, name, value)

                # assign uuid to item
                item._d_uuid = instance.uuid

                # hook into transaction
                try:
                    manager = item._d_manager
                except AttributeError:
                    manager = item._d_manager = getTransactionManager(item)

                manager.register()

                # use ``instance`` as mutator value
                item = instance
                
            setattr(self, relation_name, item)
            
        return {
            field.__name__: property(_get, _set),
            relation_name: orm.relation(
            bootstrap.Soup,
            primaryjoin=(field.schema.__mapper__.c.uuid==column),
            foreign_keys=[column],
            enable_typechecks=False,
            lazy=True)
            }

class RelationList(object):
    def __init__(self):
        self.data = []
        
    def append(self, item):
        relation = self._create_relation(item)
        self.data.append(relation)
        
    def remove(self, item):
        for relation in self.data:
            if relation.right == item.uuid:
                self.data.remove(relation)

                session = Session()
                session.delete(relation)

                break

        return ValueError("Not in list: %s" % item)
        
    def extend(self, items):
        map(self.append, items)
        
    def __iter__(self):
        return iter(self.data)

    def __len__(self):
        return len(self.data)
    
    def __getitem__(self, index):
        return self.data[index].target
        
    def __setitem__(self, index, value):
        return NotImplementedError("Setting items at an index is not implemented.")

    def _create_relation(self, item):
        relation = bootstrap.Relation()

        relation.target = item
        relation.order = len(self.data)

        session = Session()
        session.save(relation)

        return relation
        
class ListProperty(object):
    """A list property.

    Model the schema.List
    """

    def __call__(self, field, column, metadata):
        relation_table = metadata.tables['relation']
        soup_table = metadata.tables['soup']
        
        return {
            field.__name__: orm.relation(
                bootstrap.Relation,
                #secondary=relation_table,
                primaryjoin=soup_table.c.uuid==relation_table.c.left,
                #secondaryjoin=relation_table.c.target==soup_table.c.uuid,
                #foreign_keys=[relation_table.c.source],
                collection_class=RelationList,
                enable_typechecks=False)
            }
                    
class DictProperty(object):
    """A dict property.

    In SQLAlchemy, we need to model the following two defintion types:

       schema.Dict(
           value_type=schema.Object(
                schema=ISomeInterface)
           )

       schema.Dict(
           value_type=schema.Set(
                value_schema.Object(
                     schema=ISomeInterface)
                )
           )

    Reference:

    http://blog.discorporate.us/2008/02/sqlalchemy-partitioned-collections-1
    http://www.sqlalchemy.org/docs/04/mappers.html#advdatamapping_relation_collections
    
    """
    
    def __call__(self, field, column, metadata):
        #
        #
        # TODO: Return column definition

        pass
    
fieldmap = {
    schema.ASCII: StringTranslator(), 
    schema.ASCIILine: StringTranslator(),
    schema.Bool: FieldTranslator(rdb.BOOLEAN),
    schema.Bytes: FieldTranslator(rdb.BLOB),
    schema.Bytes: FieldTranslator(rdb.BLOB),
    schema.Choice: StringTranslator(),
    schema.Date: FieldTranslator(rdb.DATE),
    schema.Dict: (ObjectTranslator(), DictProperty()),
    schema.DottedName: StringTranslator(),
    schema.Float: FieldTranslator(rdb.Float), 
    schema.Id: StringTranslator(),
    schema.Int: FieldTranslator(rdb.Integer),
    schema.List: (None, ListProperty()),
    schema.Object: (ObjectTranslator(), ObjectProperty()),
    schema.Password: StringTranslator(),
    schema.SourceText: StringTranslator(),
    schema.Text: StringTranslator(),
    schema.TextLine: StringTranslator(),
    schema.URI: StringTranslator(),
    interface.interface.Method: None,
}

def decode(name):
    return resolve(name.replace(':', '.'))

def encode(iface):
    return iface.__identifier__.replace('.', ':')

def expand(iface):
    yield iface

    for spec in iface.getBases():
        for iface in expand(spec):
            yield iface

@interface.implementer(IMapper)
@component.adapter(interface.Interface)
def getMapper(spec):
    """Return a mapper for the specification."""
    if not callable(spec):
        raise TypeError("Create called for non-factory", spec)

    if IMapped.providedBy(spec):
        return spec.__mapper__

    return createMapper(spec)

def createMapper(spec):
    """Create a mapper for the specification."""

    engine = component.getUtility(IDatabaseEngine)
    metadata = engine.metadata

    # expand specification
    if interface.interfaces.IInterface.providedBy(spec):
        ifaces = set(expand(spec))
        metaclass = object
    else:
        ifaces = set(
            chain(*[tuple(expand(iface)) for \
                    iface in interface.implementedBy(spec)]))

        # generate metaclass
        d = {}
        for name, value in spec.__class__.__dict__.items():
            if isinstance(value, interface.interface.Method):
                d[name] = value

        metaclass = type(spec.__name__, (spec,), d)

    # skip trivial interfaces
    ifaces = filter(lambda iface: iface.names(), ifaces)

    # create joined table
    table = metadata.tables['soup']
    properties = {}

    for (t, p) in (getTable(iface, metadata) for iface in ifaces):
        table = rdb.join(table, t, onclause=t.c.id)
        properties.update(p)

    class Mapper(metaclass):
        interface.implements(IMapped, *ifaces)

        __spec__ = '%s.%s' % (spec.__module__, spec.__name__)

    # set class representation method if not defined
    if not isinstance(Mapper.__repr__, types.MethodType):
        def __repr__(self):
            return "<Mapper (%s.%s) at %s>" % \
                   (spec.__module__, spec.__name__, hex(id(self)))

        Mapper.__repr__ = __repr__

    # set ``property``-derived properties directly on the mapper
    for name, prop in properties.items():
        if isinstance(prop, property):
            del properties[name]
            setattr(Mapper, name, prop)

    orm.mapper(Mapper, table, properties=properties)

    spec.__mapper__ = Mapper
    interface.alsoProvides(spec, IMapped)

    return Mapper

def removeMapper(spec):
    del spec.mapper
    interface.noLongerProvides(spec, IMapped)
        
def getTable(iface, metadata):
    columns = []
    properties = {}
    
    for field in map(lambda key: iface[key], iface.names()):
        property_factory = None

        try:
            column_factory, property_factory = fieldmap[type(field)]
        except TypeError:
            column_factory = fieldmap[type(field)]
        except KeyError:
            # raise NotImplementedError("Field type unsupported (%s)." % field)
            continue

        if column_factory is not None:
            column = column_factory(field, metadata)
            columns.append(column)
        else:
            column = None
            
        if property_factory is not None:
            props = property_factory(field, column, metadata)
            properties.update(props)
        
    kw = dict(useexisting=True)

    table = rdb.Table(
        encode(iface),
        metadata,
        rdb.Column('id', rdb.Integer, rdb.ForeignKey("soup.id"), primary_key=True),
        *columns,
        **kw)

    metadata.create_all(checkfirst=True)
    
    return table, properties
