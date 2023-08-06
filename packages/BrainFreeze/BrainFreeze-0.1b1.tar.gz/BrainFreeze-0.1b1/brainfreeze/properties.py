"""OneToOne MapperProperty and Python Property implementations."""

from sqlalchemy.orm.interfaces import PropComparator, MapperProperty
from sqlalchemy.orm.properties import PropertyLoader
from sqlalchemy.orm.session import register_attribute

__all__ = [
    'OneToOneProxy', 'OneToOneMapperProperty', 
    'OneToOnePropertyLoader', 'one_to_one'
]

class OneToOneProxy(object):
    """Property that proxies attribute access to columns on a related object."""    
    def __init__(self, key, remote_class, remote_property_name):
        self.key = key
        self.remote_class = remote_class
        self.remote_property_name = remote_property_name
    
    def __get__(self, obj, type=None):
        if obj is None:
            return self
        value = None
        related_obj = getattr(obj, self.key, None)
        if related_obj:
            value = getattr(related_obj, self.remote_property_name, None)
        return value
    
    def __set__(self, obj, value):
        related_obj = getattr(obj, self.key, None)
        if related_obj is None:
            related_obj = self.remote_class()
            setattr(obj, self.key, related_obj)
        setattr(related_obj, self.remote_property_name, value)


class OneToOneMapperProperty(MapperProperty):
    """MapperProperty that proxies access to one column on a related object.
    
    This is a type of `MapperProperty` that proxies to the mapper's class
    property of the same name and allows queries to reference this property.
    The property's queries will be modified to contain a join condition
    from the parent mapper to the mapper used in the relation() given by the
    `one_to_one_relation` argument.
    
    This class is meant to be used with `OneToOnePropertyLoader` for the sole
    purpose of allowing proxied columns to be queried through the parent
    mapper.
    
    """
    def __init__(self, proxy_property, relation):
        """Tell the people what this does!"""
        self.proxy_property = proxy_property
        self.remote_property_name = self.proxy_property.remote_property_name
        self.relation = relation
        self.comparator = OneToOneMapperProperty.Comparator(self, None)
    
    def do_init(self):
        """Automatically called after key and parent are determined"""
        # Determine the table column this property is proxying to
        self.column = self.relation.mapper.get_property(
            self.remote_property_name
        ).columns[0]
        # Let the SQLAlchemy UOW know about this property
        register_attribute(self.parent.class_, self.key,
            uselist=False,
            proxy_property=self.proxy_property,
            useobject=False,
            comparator=self.comparator
        )
    
    def create_row_processor(self, *args, **kwargs):
        return (None, None)
    
    class Comparator(PropComparator):
        """
        This property comparator adds an extra condition to all comparison
        operations, so that the resulting clause will include the join
        condition between self.prop's parent mapper and
        self.prop.one_to_one_relation.
        
        This class is meant to be used with OneToOneMapperProperty for the
        sole purpose of ensuring that the correct comparison clause is
        generated when querying proxied columns.
        
        """
        def operate(self, op, *other, **kwargs): 
            join_clause = self.prop.relation.primaryjoin # ex. book.author_id = author.author_id
            op_clause = op(self.prop.column, *other, **kwargs) # ex. author.name == 'Maya Angelou'
            return join_clause & op_clause # ex. book.author_id = author.author_id AND author.name == 'Maya Angelou'
        
        def clause_element(self):
            return self.prop.column
        
        def reverse_operate(self, op, other, **kwargs):
            join_clause = self.prop.relation.primaryjoin
            column = self.prop.column
            op_clause = op(column._bind_param(other), column, **kwargs)
            return join_clause & op_clause


class OneToOnePropertyLoader(PropertyLoader):
    """PropertyLoader that proxies access to all columns on a related object.
    
    Because this PropertyLoader adds other properties, it must be added
    after the mapper's ``properties`` mapping is already defined, 
    meaning it must be added using ``my_mapper.add_property`` after the
    mapper has already defined.
    """
    def __init__(self, *args, **kwargs):
        kwargs['uselist'] = False
        super(OneToOnePropertyLoader, self).__init__(*args, **kwargs)
    
    def do_init(self):
        super(OneToOnePropertyLoader, self).do_init()
        # It's likely that no mappers have been compiled yet, so the 
        # properties in self.mapper.iterate_properties won't know their key...
        # SO we have to do something really unpolite to get the list of
        # properties.  Hopefully Alchemy will provide a better way soon...
        for prop_key, prop in self.mapper._Mapper__props.iteritems():
            # Skip foreign keys, they are already mapped
            if prop.columns[0] in self.remote_side:
                continue
            # Create the Python Property and add it to the mapped class
            proxy_property = OneToOneProxy(self.key, self.argument, prop_key)
            setattr(self.parent.class_, prop_key, proxy_property)
            
            # Create the MapperProperty so the proxied column will be query-able
            mapper_property = OneToOneMapperProperty(proxy_property, self)
            
            # Add the MapperProperty to the mapper.  Ideally this would be a
            # call to `self.parent.add_property`, but the mapper is in the
            # middle of compiling, meaning `add_property` doesn't work yet.
            # The `_compile_property` call below forces the added property
            # to initialize.
            self.parent._init_properties[prop_key] = mapper_property
            self.parent._compile_property(prop_key, mapper_property, True)

            
def one_to_one(*args, **kwargs):
    return OneToOnePropertyLoader(*args, **kwargs)