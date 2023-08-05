from sqlalchemy.orm.mapper import MapperExtension, EXT_CONTINUE
from sqlalchemy import func, select
from warnings import warn
import sys
from weakref import proxy

if_func = getattr(func, 'if')

class _Aggregation(object):
    """Base class for aggregations"""
    def __init__(self, target):
        """Aggregation constructor
        
        target
            Field object which specifies where to store
            value of aggregation
        """
        self.target = target
    
    table = property(lambda self: self.target.table)

class Count(_Aggregation):

    def oninsert(self, aggregator, instance):
        return {self.target.name: func.ifnull(self.target, 0) + 1}

    def ondelete(self, aggregator, instance):
        return {self.target.name: func.ifnull(self.target, 0) - 1}

    def onrecalc(self, aggregator, instance):
        return {self.target.name: select([func.count(self.key.parent)],
            self.key.parent == getattr(instance, self.attribute))}

class Sum(_Aggregation):
    def __init__(self, target, source):
        """Sum aggregation constructor
        
        target
            Field object which specifies where to store
            value of aggregation
        source
            Field object which value will be summed
        """
        super(Max, self).__init__(target)
        self.source = source

    def oninsert(self, aggregator, instance):
        return {self.target.name: func.ifnull(self.target, 0) + getattr(instance, self.source.name)}

    def ondelete(self, aggregator, instance):
        return {self.target.name: func.ifnull(self.target, 0) - getattr(instance, self.source.name)}

    def onupdate(self, aggregator, instance):
        return {self.target.name:
            func.ifnull(self.target, 0)
                - instance._sa_attr_state['original'][self.source.name]
                + getattr(instance, self.source.name)}

    def onrecalc(self, aggregator, instance):
        return {self.target.name: select([func.sum(self.source)],
            self.key.parent == getattr(instance, self.attribute))}

class Max(_Aggregation):
    def __init__(self, target, source):
        """Max aggregation constructor
        
        target
            Field object which specifies where to store
            value of aggregation
        source
            Field object which value will be candidate for
            maximum
        """
        super(Max, self).__init__(target)
        self.source = source

    def oninsert(self, aggregator, instance):
        if aggregator.mapper.local_table.metadata.bind.url.drivername == 'mysql':
            return {self.target.name: if_func((func.ifnull(self.target,0) < getattr(instance, self.source.name)),
                getattr(instance, self.source.name), self.target)}
        else:
            return {self.target.name: func.max(func.ifnull(self.target,0), getattr(instance, self.source.name))}

    def onrecalc(self, aggregator, instance):
        return {self.target.name: select([func.max(self.source)],
            self.key.parent == getattr(instance, self.attribute))}

    ondelete = onrecalc # Can't guess, need recalc


class Min(_Aggregation):
    def __init__(self, target, source):
        """Max aggregation constructor
        
        target
            Field object which specifies where to store
            value of aggregation
        source
            Field object which value will be candidate for
            minimum
        """
        super(Min, self).__init__(target)
        self.source = source

    def oninsert(self, aggregator, instance):
        if aggregator.mapper.local_table.metadata.bind.url.drivername == 'mysql':
            return {self.target.name: if_func(func.ifnull(self.target,sys.maxint) > getattr(instance, self.source.name),
                getattr(instance, self.source.name), self.target)}
        else:
            return {self.target.name: func.min(func.ifnull(self.target,sys.maxint), getattr(instance, self.source.name))}

    def onrecalc(self, aggregator, instance):
        return {self.target.name: select([func.min(self.source)],
            self.key.parent == getattr(instance, self.attribute))}

    ondelete = onrecalc # Can't guess, need recalc

classes = {
    'max': Max,
    'min': Min,
    'count': Count,
    }

class Quick(MapperExtension):
    """Mapper extension which maintains aggregations
    
    Quick extension does maximum it can't without
    aggregated queries, e.g. `cnt = cnt + 1`  instead
    of `cnt = (select count(*) from...)`
    """
    def __init__(self, *aggregations):
        """Initialization method
        
        *aggregations
            Aggregation subclasses which specify what
            type of aggregations must be maintained
        table
            table which holds instances
        """
        groups = {}
        for ag in aggregations:
            groups.setdefault(ag.table,[]).append(ag)
        self.aggregations = groups

    def instrument_class(self, mapper, class_):
        self.mapper = proxy(mapper) # to avoid GC cycles
        self.attributes = {}
        self.immutable_fields = set()
        table = mapper.local_table
        for (othertable, aggs) in self.aggregations.items():
            for k in table.foreign_keys:
                if k.references(othertable):
                    self.immutable_fields.add(k.column)
                    break
            else:
                raise NotImplementedError("No foreign key defined for pair %s %s" % (table, othertable))
            try:
                if mapper.properties[k.parent.name] != k.parent:
                    # Field is aliased somewhere
                    for (attrname, column) in mapper.properties.items():
                        if column is k.parent: # "==" works not as expected
                            attribute = attrname
                            break
                    else:
                        raise NotImplementedError("Can't find property %s" % k.parent.name)
            except KeyError:
                attribute = k.parent.name
            for a in aggs:
                a.key = k
                a.attribute = attribute
        return super(Quick, self).instrument_class(mapper, class_)

    def before_update(self, mapper, connection, instance):
        """called before an object instance is UPDATED"""
        for k in self.immutable_fields:
            if getattr(instance, k, None) != instance._sa_attr_state['original'][k]:
                warn("Foreign key fields used in aggregations should not be updated")
        return super(Quick, self).before_update(mapper, connection, instance)
        
    def _make_updates(self, instance, action):
        for (table, fields) in self.aggregations.items():
            anyfield = fields[0] # They all have same key and attribute attributes
            update_condition = anyfield.key.column == getattr(instance, anyfield.attribute)
            updates = {}
            for f in fields:
                updates.update(getattr(f, action)(self, instance))
            table.update(update_condition, values=updates).execute()
        return EXT_CONTINUE

    def after_insert(self, mapper, connection, instance):
        """called after an object instance has been INSERTed"""
        return self._make_updates(instance, 'oninsert')

    def after_delete(self, mapper, connection, instance):
        """called after an object instance is DELETEed"""
        return self._make_updates(instance, 'ondelete')

class Accurate(Quick):
    """Mapper extension which maintains aggregations
    
    Accurate extension does all calculations using aggregated
    query at every update of related fields
    """
    def after_insert(self, mapper, connection, instance):
        """called after an object instance has been INSERTed"""
        return self._make_updates(instance, 'onrecalc')

    after_delete = after_insert
    after_update = after_insert ## Should check for changes
