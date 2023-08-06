"""OneToOne MapperProperty and Python Property implementations"""

from sqlalchemy import exceptions as sa_exc
from sqlalchemy.sql import and_
from sqlalchemy.orm.interfaces import PropComparator
from sqlalchemy.orm.properties import PropertyLoader, ColumnProperty, ComparableProperty
from sqlalchemy.ext.associationproxy import AssociationProxy

__all__ = [
    'OneToOneProxy', 'OneToOneMapperProperty', 
    'OneToOnePropertyLoader', 'one_to_one'
]

class OneToOneProxy(AssociationProxy):
    """Property that proxies attribute access to columns on a related object.
    
    >>> class Publisher(object):
    ...     def __init__(self, name=None, address=None):
    ...         self.name = name
    ...         self.address = address

    >>> class Book(object):
    ...    def __init__(self, title=None, author=None, publisher=None):
    ...        self.title = title
    ...        self.author = author
    ...        self.publisher = publisher
    ...
    ...    publisher_name = OneToOneProxy('publisher_name', Publisher, 'name')
    ...    publisher_address = OneToOneProxy('publisher_address', Publisher, 'address')

    ... random_house = Publisher(name="Random House", address="NYC")
    ... beloved = Book(title='Beloved', author='Toni Morrison', publisher=random_house)

    ... beloved.publisher is random_house
    True

    .. beloved.publisher.name is beloved.publisher_name
    True
    
    """
    def __init__(self, relation_name, relation_class, attr_name):
        creator = lambda val: relation_class(**{attr_name: val})
        r = super(OneToOneProxy, self).__init__(relation_name, attr_name, creator=creator)
        # TODO: put this assert in a proper test, 
        # it raises an error if the AssociationProxy 'API' has changed
        assert(self.target_collection == relation_name)
        return r


class OneToOneMapperProperty(ComparableProperty):
    """Instruments a OneToOneProxy python property for use in query expressions.
    
    Queries on the mapped class will be modified to contain the join condition
    necessary to locate the proxied property.
    
    The property is also registered with the session's unit-of-work machinery,
    so that changes to the property will be persisted.
    
    """
    def __init__(self, proxy_property=None):
        """Construct a OneToOneMapperProperty."""
        if not isinstance(proxy_property, OneToOneProxy):
            raise sa_exc.ArgumentError("Unsupported proxy type: '%s'" % type(proxy_property))

        super(OneToOneMapperProperty, self).__init__(one_to_one_comparator, proxy_property)


def one_to_one_comparator(prop, mapper):
    """Return an appropriate OneToOneComparator for the given property."""
    intermediary_obj = mapper.get_property(prop.descriptor.target_collection) # ex: Book.publisher
    target_prop = intermediary_obj.mapper.get_property(prop.key) # ex: Publisher.publisher_name
    
    if isinstance(target_prop, ColumnProperty):
        return OneToOneColumnComparator(prop, mapper, intermediary_obj, target_prop)
    elif isinstance(target_prop, PropertyLoader):
        return OneToOneRelationComparator(prop, mapper, intermediary_obj, target_prop)
    else:
        raise sa_exc.ArgumentError("Unsupported property type: '%s'" % type(prop))


class OneToOneComparator(PropComparator):
    """Base class for other OneToOne Comparators"""
    def __init__(self, prop, mapper, intermediary_obj, target_prop):
        self.intermediary = intermediary_obj # ex: Book.publisher
        self.target = target_prop # ex: Publisher.publisher_name
        
        # Determine necessary join clauses (ex: book.publisher_id == publisher.publisher_id)
        self.join_clauses = self.intermediary.primaryjoin
        if self.intermediary.secondaryjoin:
            self.join_clauses = and_(self.join_clauses, self.intermediary.secondaryjoin)
            
        super(OneToOneComparator, self).__init__(prop, mapper)


class OneToOneColumnComparator(OneToOneComparator):
    """Comparator for a OneToOneProxy that's proxying to a ColumnProperty"""
    def __clause_element__(self):
        return self.target.columns[0]._annotate({"parententity": self.intermediary.mapper})

    def operate(self, op, *other, **kwargs):
        """Return 'where' clauses for this operation."""
        join_clauses = self.join_clauses # ex: book.publisher_id = publisher.publisher_id
        op_clauses = op(self.__clause_element__(), *other, **kwargs) # ex: publisher.publisher_name = 'Doubleday'
        return and_(join_clauses, op_clauses) 

    def reverse_operate(self, op, other, **kwargs):
        """Return 'where' clauses for this operation."""
        join_clauses = self.join_clauses # ex: book.publisher_id = publisher.publisher_id
        column = self.__clause_element__() # ex: publisher.publisher_name
        op_clauses = op(column._bind_param(other), column, **kwargs) # ex: 'Doubleday' = publisher.publisher_name
        return and_(join_clauses, op_clauses)


class OneToOneRelationComparator(OneToOneComparator):
    """Comparator for a OneToOneProxy that's proxying to a PropertyLoader property relation"""
    def operate(self, op, *other, **kwargs):
        """Return 'where' clauses for this operation."""
        join_clauses = self.join_clauses # ex: book.publisher_id = publisher.publisher_id
        op_clauses = op(self, *other, **kwargs) # ex: publisher.primary_contact_id == 1
        return sql.and_(join_clauses, op_clauses)

    def reverse_operate(self, op, other, **kwargs):
        return self.operate(self, op, *other, **kwargs)

    def __eq__(self, other):
        # self.target ex: Publisher.primary_contact (relation!)
        if other is None:
            raise sa_exc.InvalidRequestError("NOT IMPLEMENTED!")
        elif self.target.uselist:
            raise sa_exc.InvalidRequestError("NOT IMPLEMENTED!")
        else:
            return self.target._optimized_compare(other)


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
        for prop_key, prop in self.mapper._props.iteritems():
            # Skip foreign keys (they are already mapped)
            if isinstance(prop, ColumnProperty) and prop.columns[0] in self.remote_side:
                continue
            
            # Create the Python Property and add it to the mapped class
            proxy_property = OneToOneProxy(self.key, self.argument, prop_key)
            setattr(self.parent.class_, prop_key, proxy_property)
            
            # Create the MapperProperty so the proxied column will be query-able
            mapper_property = OneToOneMapperProperty(proxy_property)
            
            # Add the MapperProperty to the mapper.  Ideally this would be a
            # call to `self.parent.add_property`, but the mapper is in the
            # middle of compiling, meaning `add_property` doesn't work yet.
            # The `_compile_property` call below forces the added property
            # to initialize.
            self.parent._init_properties[prop_key] = mapper_property
            self.parent._compile_property(prop_key, mapper_property, True)


def one_to_one(*args, **kwargs):
    return OneToOnePropertyLoader(*args, **kwargs)