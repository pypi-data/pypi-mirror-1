from sqlalchemy import util
from sqlalchemy.orm import MapperExtension, class_mapper, EXT_CONTINUE
from sqlalchemy.exceptions import ArgumentError

from properties import one_to_one

__all__ = ['OneToOneMapperExtension']

class OneToOneMapperExtension(MapperExtension):
    """MapperExtension to proxy properties on one-to-one relations.

    This extension proxies access to all properties of the specified
    one-to-one relations without an intermediate layer. 
    
    The intended use case is to allow a type composed of multiple tables to
    be easily mapped and queried as if it were one table.

    """
    def __init__(self, *related_classes, **kwargs):
        # Raise exception if any class was specified more than once
        if len(util.to_list(related_classes)) != len(util.to_set(related_classes)):
            raise ArgumentError(
                "Name collision, classes may only be specified once: %r" % related_classes
            )
        self.related_classes = util.to_list(related_classes)
        self.property_prefix = kwargs.get('property_prefix', '_')
    
    def instrument_class(self, mapper, class_):
        # Iterate through the specified classes and create relations,
        # python properties, and mapper properties for all of them.
        for value_class in self.related_classes:
            value_mapper = class_mapper(value_class, compile=False)
            key = self.property_prefix + value_mapper.local_table.key
            # Raise exception if adding this property would overwrite another property
            if key in mapper._init_properties:
                raise ArgumentError(
                    "OneToOne relation '%s' conflicts with existing property" % key
                )
            # mapper.add_property isn't ready yet, so we use...
            mapper._init_properties[key] = one_to_one(value_class)
        return EXT_CONTINUE