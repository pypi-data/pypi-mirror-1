"""
    turboentity.py
    
    Declarative layer on top of SQLAlchemy, somewhat
    "thicker" than ActiveMapper.

    Created by Daniel Haus <daniel.haus@ematia.de> on 2006-10-06.
    Copyright (c) 2006 Ematia. All rights reserved.
    
    Depends on sqlalchemy 0.2.x (http://www.sqlalchemy.org) and is
    heavily inspired by Jonathan LaCour's ActiveMapper extension.
"""

import sys
import re
import sqlalchemy as sa

from sqlalchemy import DynamicMetaData, create_session, ForeignKey
from sqlalchemy.types import *
from sqlalchemy.ext.sessioncontext import SessionContext
from sqlalchemy.ext.assignmapper import assign_mapper



######
    ## some constants
    ##

_DEFAULT_PRIMARY_KEY_NAME = "id"
_DEFAULT_PRIMARY_KEY_TYPE = sa.Integer
_DEFAULT_FOREIGN_KEY_SCHEME = "TE_FK_%s_%s"
_DEFAULT_SECONDARY_TABLE_SCHEME = "TE_ST_%s_%s__%s_%s"
_DEFAULT_POLYMORPHIC_COLUMN_NAME = "TE_P_type"
_DEFAULT_POLYMORPHIC_COLUMN_TYPE = sa.String(255)

_RE_NAME_ENDS_WITH_NUMBER = re.compile("^([^0-9]+)([0-9]+)$")



######
    ## connect
    ##

metadata = DynamicMetaData("turboentity")

try:
    objectstore = sa.objectstore
except AttributeError:
    # thread local SessionContext
    class Objectstore(object):
        def __init__(self, *args, **kwargs):
            self.context = SessionContext(*args, **kwargs)
        def __getattr__(self, name):
            return getattr(self.context.current, name)
        session = property(lambda s:s.context.current)
    
    objectstore = Objectstore(create_session)



######
    ## relationships
    ##

class Relationship (object):
    """
        Baseclass for all types of relationships.
        
        Never instantiate this class directly! Always
        use an appropriate subclass (ie. one of
        OneToOne, OneToMany, ManyToOne or ManyToMany)
    """
    
    def __init__(self, target, backref=None, **kws):
        """
            Initializes a relationship.
            
            Parameters include:
                target:     Name of the target entity, either the class name
                            (if source and target share the same module) or
                            the full path in the form "module.ClassName"
                            (as string).
                backref:    The column name of the inverse, this is optional
                            if you also define the other end of the relationship
                            on the target-entity.
                colname:    Name of the property, this is optional.
                order_by:   How the target list should be ordered, optional
                            (only applies to OneToMany, ManyToMany) specified as
                            a string of comma separated colnames. a leading "-"
                            will reverse the order.
            
            Any other parameters (eg. cascade, private, index, ...) are simply
            passed through to sqlalchemy's relation function.
        """
    
        self.target = target
        self.backref = backref
        
        self.colname = kws.get('colname', None)
        self.order_by = kws.get('order_by', False)
        
        self.source_class = None
        self._target_class = None
        self.inverse = None
        
        self.processed = False
    
    
    ######
        ## target_class property
        ##
    
    def get_target_class(self):
        if not self._target_class is None:
            return self._target_class
        
        if EntityMeta.classes.has_key(self.target):
            self._target_class = EntityMeta.classes[self.target]
        else:
            key = self.source_class.__module__ +"."+ self.target
            if EntityMeta.classes.has_key(key):
                self._target_class = EntityMeta.classes[key]
        
        return self._target_class
        
    def set_target_class(self, target_class):
        self._target_class = target_class
    
    target_class = property(fget=get_target_class, fset=set_target_class)
    
    
    ######
        ## misc
        ##
    
    def __repr__(self):
        cls = self.__class__.__name__
        src = self.source_class.__name__
        return "<%s %s.%s to %s>" % (cls, src, self.colname, self.target)



class OneToOne (Relationship):
    """
        Defines a one-to-one-relationship
    """
    
    def __init__(self, *args, **kws):
        self.foreign_key = None
        super(OneToOne, self).__init__(*args, **kws)



class ManyToOne (Relationship):
    """
        Defines a one-to-one-relationship
    """
    
    def __init__(self, *args, **kws):
        self.foreign_key = None
        super(ManyToOne, self).__init__(*args, **kws)



class OneToMany (Relationship):
    """
        Defines a one-to-one-relationship
    """
    
    def __init__(self, *args, **kws):
        self.foreign_key = None
        super(OneToMany, self).__init__(*args, **kws)



class ManyToMany (Relationship):
    """
        Defines a one-to-one-relationship
    """
    
    def __init__(self, *args, **kws):
        self.secondary = None
        super(ManyToMany, self).__init__(*args, **kws)



######
    ## columns
    ##

class Column (object):
    """
        Stores column specification
    """
    
    def __init__(self, coltype, *args, **kws):
        """
            Initializes a column
            
            Parameters are:
                coltype:            The column's type, any type from sqlalchemy.types,
                                    this parameter is mandatory.
                primary_key:        If set to "True", this column will be a primary key.
                polymorphic_column: If set to "True", this column will store the concrete
                                    type ("module.ClassName") of the stored entity, when
                                    using polymorphic inheritance.
            
            Any other parameters (eg. cascade, private, index, post_update, ...)
            are simply passed through to sqlalchemy's Column function, if specified.
        """
        
        self.primary_key = kws.get('primary_key', None)
        self.colname = kws.get('colname', None)
        self.coltype = coltype
        self.polymorphic_column = kws.get('polymorphic_column', None)
        
        self.args = args
        self.kws = kws
    
    def _process(self):
        """
            create the corresponding sqlalchemy-column-object
        """
        
        return sa.Column(self.colname, self.coltype, *self.args, **self.kws)
    


######
    ## Entity meta class
    ##

class EntityMeta (type):
    """
        Entity meta class.
        
        This is doing all the work, like defining
        tables, setting up mappers and the like.
    """
    
    metadatas = set()
    classes = {}
    deferred_classes = set()
    deferred_relations = set()
    
    def __init__(cls, classname, classbases, classdict):
        # skip Entity base class
        if classbases[0] is object: return
        
        class TurboEntityDescriptor (object):
            def __init__(self, cls, metadata, settings):
                self.cls = cls
                self.columns = {}
                self.relations = {}
                self.primary_key = None
                self.parent = None
                self.polymorphic_column = None
                self.deferred_polymorphic_entities = None
                
                if cls.__module__ == "__main__":
                    self.path = cls.__name__
                else:
                    self.path = cls.__module__ +"."+ cls.__name__
                
                self.polymorphic_dict = None
                self.settings = settings
                self.metadata = getattr(settings, "metadata", metadata)
            
            def properties(self):
                return dict(columns.items() + relations.items())
            properties = property(fget=properties)
        
        _metadata = getattr(sys.modules[cls.__module__], "metadata", metadata)
        
        EntityMeta.metadatas.add(_metadata)
        te = cls._te = TurboEntityDescriptor(cls, _metadata,
                                             getattr(cls, "turboentity", None))
        
        EntityMeta.classes[te.path] = cls
        EntityMeta.deferred_classes.add(cls)
        
        # inheritance: find parent class
        if Entity not in classbases:
            for base in classbases:
                if issubclass(base, Entity):
                    te.parent = base
                    break
        
        # determine tablename
        te.tablename = getattr(te.settings, "tablename",
                               _create_tablename(cls,
                                getattr(te.settings, "use_shortnames", None)))
        
        columns, relations = te.columns, te.relations
        
        # sort and prepare properties
        for key, value in classdict.items():
            if isinstance(value, Column):
                if value.colname is None:
                    value.colname = key
                
                if value.primary_key:
                    te.primary_key = value._process()
                    columns[te.primary_key.key] = te.primary_key
                elif value.polymorphic_column:
                    te.polymorphic_column = value._process()
                    columns[te.polymorphic_column.key] = te.polymorphic_column
                else:
                    col = value._process()
                    columns[col.key] = col
                
            elif isinstance(value, Relationship):
                if value.colname is None:
                    value.colname = key
                
                value.source_class = cls
                relations[value.colname] = value
            else:
                continue
            
            delattr(cls, key)
        
        # create a primary key, if none was found
        if not te.primary_key:
            if te.parent is None:
                keyname = _find_name(_DEFAULT_PRIMARY_KEY_NAME, te.properties.keys())
                te.primary_key = sa.Column(keyname, _DEFAULT_PRIMARY_KEY_TYPE,
                                           primary_key=True)
            else:
                parent = te.parent._te
                te.primary_key = sa.Column(parent.primary_key.key, parent.primary_key.type,
                                           ForeignKey(parent.primary_key), primary_key=True)

                
                # FIXME: obviously this don't fully work yet?
                
                # te.primary_key = sa.Column(parent.primary_key.key, parent.primary_key.type,
                #                            ForeignKey(parent.primary_key, use_alter=True,
                #                                       # FIXME:
                #                                       name="CONSTR_"+parent.primary_key.key),
                #                            primary_key=True)
            
            columns[te.primary_key.key] = te.primary_key
        
        EntityMeta.deferred_relations.update(relations.values())
        
        _setup_deferred_classes()
                
        super(EntityMeta, cls).__init__(classname, classbases, classdict)
    


######
    ## Entity base class
    ##

class Entity (object):
    """
        Entity base class.
        
        All entities inherit this class. A couple of options can be
        specified by defining a nested class named "turboentity"
        like this:
        
        class MyEntity (Entity):
            class turboentity:
                option1_name = value1
                option2_name = value2
            ...
        
        Options are:
            use_shortnames: By default the name of the table of the entity's
                            database representation is the full module path,
                            with dots replaced by underscores, appended by
                            a single underscore, appended by the classname.
                            
                            Example:    the table's name for the entity
                                        "myproject.model.Customer"
                                        will be "myproject_model_Customer"
                            
                            If you set use_shortnames to "True", the tablename
                            will just be the name of the entity, in the example
                            above this would be just "Customer"
                            
            tablename:      By setting the option "tablename" you can define
                            a custom tablename.
            
            metadata:       Specifies a custom metadata-object.
            
            
    """
    
    __metaclass__ = EntityMeta
    
    def __repr__(self):
        return "<%s entity at 0x%x>" % (self.__class__.__name__, id(self))
    


######
    ## create/drop table commands
    ##

def create_all():
    """
        Creates all required tables for all defined entities
        and relationships.
    """
    
    if len(EntityMeta.deferred_classes) > 0:
        classes = map(lambda x:x.__name__, EntityMeta.deferred_classes)
        raise Exception("undefined classes left: %s" % ", ".join(classes))
    
    for metadata in EntityMeta.metadatas:
        metadata.create_all()


def drop_all():
    """
        Drops all created tables.
    """
    
    if len(EntityMeta.deferred_classes) > 0:
        classes = map(lambda x:x.__name__, EntityMeta.deferred_classes)
        raise Exception("undefined classes left: %s" % ", ".join(classes))
    
    for metadata in EntityMeta.metadatas:
        metadata.drop_all()



######
    ## helpers and utility functions
    ##

def _setup_deferred_classes():
    """
        Test for all entites if we have all information
        we need to define and create tables.
    """
    
    for entity in list(EntityMeta.deferred_classes):
        if _has_undefined_references(entity):
            continue
        
        te = entity._te
        relations = _setup_relations(te)
        entity.table = sa.Table(te.tablename, te.metadata, *te.columns.values())
        session = getattr(sys.modules[entity.__module__], "session", objectstore)
        order_by = _translate_order_by(entity, getattr(te.settings, "order_by", False))
        
        if te.parent:
            parent = te.parent
            _add_polymorphic_identity(parent, entity)
            
            inherit_condition = (parent._te.primary_key==te.primary_key)
            assign_mapper(session.context, entity, entity.table,
                          properties=relations, inherits=getattr(parent, "mapper", None),
                          inherit_condition=inherit_condition,
                          order_by=order_by, polymorphic_identity=te.path)
        else:
            te.relations = relations
            
            # will be base class?
            if te.deferred_polymorphic_entities:
                te.polymorphic_dict = {
                    te.path: entity.table.select(te.polymorphic_column==te.path)
                }
                
                for subentity in te.deferred_polymorphic_entities:
                    onclause = (entity._te.primary_key==subentity._te.primary_key)
                    te.polymorphic_dict[subentity._te.path] = entity.table.join(subentity.table,
                                                                                onclause=onclause)
                
                pjoin = sa.polymorphic_union(te.polymorphic_dict, None, "pjoin")
                
                assign_mapper(session.context, entity, entity.table,
                              polymorphic_on=te.polymorphic_column,
                              polymorphic_identity=te.path,
                              select_table=pjoin,
                              order_by=order_by, properties=relations)
        
                subentity.mapper.inherits = entity.mapper
                
            else: # plain and simple
                assign_mapper(session.context, entity, entity.table,
                              order_by=order_by, properties=relations)
        
        EntityMeta.deferred_classes.remove(entity)


def _add_polymorphic_identity(parent, subentity):
    """
        Add an inherited sub entity to an existing entity.
    """
    
    te = parent._te
    col = sa.Column(_find_name(_DEFAULT_POLYMORPHIC_COLUMN_NAME, te.properties.keys()),
                    _DEFAULT_POLYMORPHIC_COLUMN_TYPE)
    te.columns[col.key] = col
    te.polymorphic_column = col
    
    # case 1: parent is setup -> parent.table and parent.mapper exist
    if hasattr(parent, "table"):
        if te.polymorphic_dict is None:
            parent.table.append_column(col)
            parent.mapper.add_property(col.key, col)
        
            te.polymorphic_dict = {
                te.path: parent.table.select(te.polymorphic_column==te.path)
            }
        
            parent.mapper.polymorphic_identity = te.path
            parent.mapper.polymorphic_on = te.polymorphic_column
        
        onclause = parent._te.primary_key == subentity._te.primary_key
        te.polymorphic_dict[subentity._te.path] = parent.table.join(subentity.table,
                                                                    onclause=onclause)
    
        pjoin = sa.polymorphic_union(te.polymorphic_dict, None, "pjoin")
        parent.mapper.select_table = pjoin
    
    else: # (parent has not been initialized yet)
        if te.deferred_polymorphic_entities is None:
            te.deferred_polymorphic_entities = []
        te.deferred_polymorphic_entities.append(subentity)

def _setup_relations(te):
    """
        Setup and return relationships.
        
        Automatically create necessary foreign keys
        and secondary tables (at this point all required
        classes have been defined and do have primary keys).
    """
    
    results = {}
    
    for relation in te.relations.values():
        # 1. determine inverse
        for inverse in list(EntityMeta.deferred_relations):
            if _relations_match(relation, inverse):
                relation.inverse = inverse
                inverse.inverse = relation
        
        if not relation.inverse:
            inverse = None
        else:
            relation.backref = relation.inverse.colname
            relation.inverse.backref = relation.colname
            inverse = relation.inverse
        
        # skip if this relation is set up already
        if relation.processed or (inverse and inverse.processed):
            continue
        
        # 2. add foreign key to class or create secondary tables, if necessary
        # 3. setup relationships and add to results
        
        order_by = _translate_order_by(relation.target_class, relation.order_by)
        order_by_inv = False
        if inverse:
            order_by_inv = _translate_order_by(inverse.target_class, inverse.order_by)
        
        if isinstance(relation, ManyToMany):
            if not relation.secondary:
                _create_secondary(relation, inverse)
            
            # create relationship
            results[relation.colname] = sa.relation(relation.target_class,
                                                    secondary=relation.secondary,
                                                    backref=sa.backref(relation.backref,
                                                                       uselist=True,
                                                                       order_by=order_by_inv),
                                                    order_by=order_by,
                                                    uselist=True)
            
        else:            
            from_entity = relation.source_class
            to_entity = relation.target_class
            
            if isinstance(relation, OneToOne):
                if from_entity.__name__ > to_entity.__name__:
                    from_entity, to_entity = to_entity, from_entity
                
                if relation.foreign_key:
                    foreign_key, primary_key = relation.foreign_key, relation.primary_key
                else:
                    foreign_key, primary_key = _create_foreign_key(from_entity, to_entity,
                                                                  relation.colname)
                
                primaryjoin=(foreign_key==primary_key)
                results[relation.colname] = sa.relation(relation.target_class, 
                                                        primaryjoin=primaryjoin,
                                                        foreignkey=primary_key,
                                                        backref=sa.backref(relation.backref,
                                                                           uselist=False,
                                                                           primaryjoin=primaryjoin,
                                                                           foreignkey=foreign_key,
                                                                           order_by=order_by_inv),
                                                        order_by=order_by,
                                                        post_update=getattr(relation, "post_update", True),
                                                        uselist=False)
            
            elif isinstance(relation, ManyToOne):
                if relation.foreign_key:
                    foreign_key, primary_key = relation.foreign_key, relation.primary_key
                else:
                    foreign_key, primary_key = _create_foreign_key(from_entity, to_entity,
                                                                  relation.colname)
                
                primaryjoin=(foreign_key==primary_key)
                results[relation.colname] = sa.relation(relation.target_class, 
                                                        primaryjoin=primaryjoin,
                                                        foreignkey=primary_key,
                                                        backref=sa.backref(relation.backref,
                                                                           uselist=True,
                                                                           primaryjoin=primaryjoin,
                                                                           foreignkey=foreign_key,
                                                                           order_by=order_by_inv),
                                                        order_by=order_by,
                                                        post_update=getattr(relation, "post_update", True),
                                                        uselist=False)
            
            elif isinstance(relation, OneToMany):
                if relation.foreign_key:
                    foreign_key, primary_key = relation.foreign_key, relation.primary_key
                else:
                    foreign_key, primary_key = _create_foreign_key(to_entity, from_entity,
                                                                  relation.backref)
                
                primaryjoin=(foreign_key==primary_key)
                results[relation.colname] = sa.relation(relation.target_class, 
                                                        primaryjoin=primaryjoin,
                                                        foreignkey=foreign_key,
                                                        backref=sa.backref(relation.backref,
                                                                           uselist=False,
                                                                           primaryjoin=primaryjoin,
                                                                           foreignkey=primary_key,
                                                                           order_by=order_by_inv),
                                                        order_by=order_by,
                                                        post_update=getattr(relation, "post_update", True),
                                                        uselist=True)
        
        EntityMeta.deferred_relations.discard(relation)
        EntityMeta.deferred_relations.discard(inverse)
        
        relation.processed = True
        if inverse: inverse.processed = True
        
    return results    


def _create_foreign_key(from_entity, to_entity, relation_name):
    """
        Automatically create foreign keys for one-to-..
        and ..-to-one-relationships on "from_entity".
    """
    
    primary_key = to_entity._te.primary_key
    
    colname = _find_name(_DEFAULT_FOREIGN_KEY_SCHEME % (relation_name, primary_key.key),
                         from_entity._te.properties.keys())
    foreign_key = sa.Column(colname, primary_key.type, ForeignKey(primary_key), index=True)
    from_entity._te.columns[foreign_key.key] = foreign_key
    
    return (foreign_key, primary_key)


def _create_secondary(relation, inverse):
    """
        Create secondary table for a
        many-to-many-relationship
    """
    
    assert isinstance(relation, ManyToMany)
    
    entity1, entity2 = relation.source_class, relation.target_class
    column1, column2 = relation.colname, relation.backref
    
    # keep table name consistent
    if column1 < column2:
        entity1, entity2 = entity2, entity1
        column1, column2 = column2, column1
    
    primary_key1 = entity1._te.primary_key
    primary_key2 = entity2._te.primary_key
    
    tablename = _DEFAULT_SECONDARY_TABLE_SCHEME % \
        (entity1._te.tablename, column1, entity2._te.tablename, column2)
        
    colname1 = entity1._te.tablename +"_"+ primary_key1.key
    colname2 = entity2._te.tablename +"_"+ primary_key2.key
    
    relation.secondary = sa.Table(tablename, entity1._te.metadata,
        sa.Column(colname1, primary_key1.type, ForeignKey(primary_key1)),
        sa.Column(colname2, primary_key2.type, ForeignKey(primary_key2))
    )
    
    if inverse:
        inverse.secondary = relation.secondary    


def _create_tablename(cls, shortnames=None):
    """
        Create a tablename.
    """
    
    if shortnames:
        return cls.__name__.lower()
    
    return cls._te.path.replace(".", "_")


def _has_undefined_references(cls):
    """
        Test if there's a relationship in the class, that references
        another class which has not yet been defined.
    """
    
    for rel in cls._te.relations.values():
        if rel.target_class is None:
            return True
    
    return False


def _relations_match(rel1, rel2):
    """
        Find out if related relations match (so that they
        can be each other's backrefs).
    """
    
    def _relation_types_match(rel1, rel2):
        """
            Find out if related relations' types match
            (so that they can be each other's backrefs).
        """
    
        assert isinstance(rel1, Relationship) and isinstance(rel2, Relationship)
    
        t1, t2 = type(rel1), type(rel2)
    
        if t1 is OneToOne or t1 is ManyToMany:
            return t1 is t2
        elif t1 is OneToMany:
            return t2 is ManyToOne
        elif t1 is ManyToOne:
            return t2 is OneToMany
    
        return False
    
    assert isinstance(rel1, Relationship) and isinstance(rel2, Relationship)
    
    if (rel1.target_class is not rel2.source_class) \
        or (rel2.target_class is not rel1.source_class) \
        or not _relation_types_match(rel1, rel2) \
        or rel1.backref and (rel1.backref != rel2.colname) \
        or rel2.backref and (rel2.backref != rel1.colname):
            return False
    else:
        return True


def _translate_order_by(entity, order_by):
    """
        Translates any given order_by-string into a list of
        columns, wrapped in a desc(), if appropriate.
    """
    
    if not order_by:
        return order_by
    
    if type(order_by) is str:
        order_by = order_by.split(",")
    elif type(order_by) is not list:
        order_by = [order_by]
    
    if len(order_by) == 0:
        return False
    
    te = entity._te
    
    cols, order_by = order_by, []
    for col in cols:
        if type(col) is str:
            col = col.strip()
            if col[0] == "-":
                col = sa.desc(te.properties[col[1:].strip()])
            else:
                col = te.properties[col]
        order_by.append(col)
    
    if len(order_by) == 1:
        return order_by[0]
    
    return order_by


def _find_name(key, keys):
    """
        If "key" ends with a number, count up the number until
        the resulting key is not in "keys". if it does not end
        with a number, simply add a "1".
    """
    
    if key not in keys:
        return key
    
    m = _RE_NAME_ENDS_WITH_NUMBER.match(key)
    if not m:
        key += "1"
    else:
        key = m.group(1) + str(int(m.group(2)) + 1)
    
    if key in keys:
        return _find_name(key, keys)
        
    return key


######
    ## names to export
    ##

__all__ = ["Entity", "Column", "OneToOne", "OneToMany", "ManyToOne",
           "ManyToMany", "create_all", "drop_all", "ForeignKey"] + sa.types.__all__

