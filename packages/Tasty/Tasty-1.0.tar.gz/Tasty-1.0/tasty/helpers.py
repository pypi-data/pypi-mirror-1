from types import *
from sqlobject import *
from tasty.model import User,Item,Tag

def sqlobject_to_strings(d):
    if isinstance(d,SQLObject):
        if isinstance(d,User):
            return {'user' : d.username}
        if isinstance(d,Item):
            return {'item' : d.name}
        if isinstance(d,Tag):
            return {'tag' : d.name}
        return str(d)
    if isinstance(d,DictType):
        new_dict = {}
        for k in d.keys():
            new_dict[k] = sqlobject_to_strings(d[k])
        return new_dict
    if isinstance(d,ListType) or isinstance(d,TupleType):
        return [sqlobject_to_strings(i) for i in d]

    return d
