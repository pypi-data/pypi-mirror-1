from pyflow.core import *
import sys
import inspect

"""
setup of self-describing data structures. for use with dataform, et al.

design (and some of the metaclass code) are from the nifty elixir.ematia.de project.
"""

class CounterMeta(type):
    counter = 0
    def __call__(self, *args, **kwargs):
        inst = type.__call__(self, *args, **kwargs)
        inst._counter = CounterMeta.counter
        CounterMeta.counter += 1
        return inst

class Property(object):
    __metaclass__ = CounterMeta
    def __init__(self, *args, **kw):
        self.entity = None
        self.name = None

    def attach(self, entity, name):
        self.entity = entity
        self.name = name
        entity._props.append(self)
        if hasattr(entity, name):
            delattr(entity, name)

def _is_entity(class_): return isinstance(class_, EntityMeta)

class EntityMeta(type):
    _entities = {}

    def __init__(cls, name, bases, dict_):
        # only process subclasses of Entity, not Entity itself
        if bases[0] is object:
            return

        # build a dict of entities for each frame where there are entities
        # defined
        caller_frame = sys._getframe(1)
        cid = cls._caller = id(caller_frame)
        caller_entities = EntityMeta._entities.setdefault(cid, {})
        caller_entities[name] = cls

        # Append all entities which are currently visible by the entity. This 
        # will find more entities only if some of them where imported from 
        # another module.
        for entity in [e for e in caller_frame.f_locals.values() 
                         if _is_entity(e)]:
            caller_entities[entity.__name__] = entity

        # Process attributes (using the assignment syntax), looking for 
        # 'Property' instances and attaching them to this entity.
        properties = [(name, attr) for name, attr in dict_.iteritems() 
                                   if isinstance(attr, Property)]
        sortedProps = sorted(properties, key=lambda i: i[1]._counter)

        cls._props = []
        for name, prop in sortedProps:
            prop.attach(cls, name)

class Entity(object):
    __metaclass__ = EntityMeta
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

class TextArea:
    def __init__(self, rows, cols):
        self.rows = rows
        self.cols = cols
    def editor(self, prop, data):
        if 'label' in prop.kwargs:
            return textareal(prop.name, data, self.rows, self.cols, label=prop.kwargs['label'])
        else:
            return textarea(prop.name, data, self.rows, self.cols)

class Field(Property):
    def __init__(self, *args, **kw):
        super(Field, self).__init__()
        self.edit = kw.pop("edit", True)
        self.defedit = kw.pop("defedit", None)
        self.args = args
        self.kwargs = kw

class Unicode(Field):
    def __init__(self, *args, **kw):
        super(Unicode, self).__init__(*args, **kw)
    def editor(self, data):
        if data == None: data = u""
        if self.defedit: return self.defedit.editor(self, data)
        if 'label' in self.kwargs:
            return inputl(self.name, data, label=self.kwargs['label'])
        else:
            return input(self.name, data)
class Integer(Field):
    def __init__(self, *args, **kw):
        super(Integer, self).__init__(*args, **kw)
        self.edit = False # todo;
class Ref(Field):
    def __init__(self, refs, *args, **kw):
        super(Ref, self).__init__(*args, **kw)
        self.refs = self._entities[refs]
        self.edit = False

class SetOf(Field):
    def __init__(self, *args, **kwargs):
        super(SetOf, self).__init__()
        self.edit = False # todo; should be able to support sublist editing 
class ListOf(Field):
    def __init__(self, *args, **kwargs):
        super(SetOf, self).__init__()
        self.edit = False # todo; should be able to support sublist editing 


def _dataform(res, cls, inst, extras):
    # todo; need to make submit handler know about _args to be able to do
    # generic rather than pre-bounds
    def onsub(_args):
        pass
    frm = []
    for prop in cls._props:
        if prop.edit:
            data = None if inst == None else getattr(inst, prop.name)
            frm.append(prop.editor(data))
            frm.append(br())
    return aform(onsub, *frm)

def newdataform(typ, extraFields, callafter):
    return _dataform(callafter, typ, None, extraFields)

def editdataform(inst, extraFields, callafter):
    return _dataform(callafter, inst.__class__, inst, extraFields)
