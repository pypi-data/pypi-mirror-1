"""InputItems are yielded by the descriptor
an InputItem instance has an arbitrary number
of attributes that are described in the schema.

This "item" is the one that is accessible in the builder's context
and that can be used in the if clauses of the XML schemas.
"""

__all__ = ['InputItem']

class InputItem(object):
    """a black box that contains the attributes defined in a schema"""

    def __repr__(self):
        return str(self.__dict__)

