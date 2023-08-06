# -*- coding: utf-8 -*-
from contextlib import contextmanager
import datetime
import re
import UserDict, UserList
from types import LongType

__all__ = ["Record", "XRecordDatabase", "XRecordFK" ]

class Record: 
    """
    Simple container object, for storing rows of database data in a serializable
    form. Objects of this class are returned by XXXObject, methods of XRecordDatabase. This is
    the simplest possible ORM - it takes whatever is returned by a query, looks at the signature
    and creates objects on the fly.

    XRecord.Serialized also returns an instance of this class, since it's easily processed
    by most common python serializers.

    Attributes (column values) may be accessed like attributes and dictionary items alike:
       >>> for r in db.ArrayObject ( "SELECT * FROM blog_entry" ):
       ...    print r.title, r.author
       ...    print r['title'], r['author']
       ...
       Article 1  1
       Article 1  1
       Article 2  1
       Article 2  1

    """
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)
            
    def __repr__(self):
        u = []
        for attr in dir(self):
            if not (attr.startswith("__") or attr in ["get", "_translate", "_feed"]):                    
                u.append (  attr + ': ' + `getattr(self, attr)` )                
        return u", ".join(u)
    
    def __iter__(self):
        for attr in dir(self):
            if not (attr.startswith("__") or attr in ["get", "_translate", "_feed"]):                    
                yield (attr, getattr(self, attr) )
                
    def __getitem__ (self, attr):  return getattr(self, attr)        
    def __setitem__ (self, attr, val): return setattr(self, attr, val)

    def _translate(self, dictionary):
        nr = Record()
        for ( an, av ) in self:
            setattr ( nr, dictionary.get (an, an), av )
        return nr
    
    def get(self, attr, default=None):
        try:
            return getattr(self, attr)
        except AttributeError:
            return default

class XRecordFK:
    def __init__(self, record, column):
        self.record = record
        self.column = column
        self._fk = self.record.SCHEMA.fk[self.column]
        self._reference = None
        self._value = None
        
    def nullify(self):
        self.value = None
        self.reference = None

    @property
    def null(self):
        return self.value is None

    def __cmp__(self, obj):
        if self.null: return False
        return self.value.__cmp__(obj)
    def __repr__(self):
        return repr(self.value)

    
    def _set_value(self, value):
        if isinstance(value, self.record.DB.XRecordClass) and value.Table == self._fk.REFERENCED_TABLE_NAME:
            new_value = value[self._fk.REFERENCED_COLUMN_NAME]
        else:
            new_value = value

        if new_value != self._value:
            self._value = new_value
            self._reference = None
            
        if self._value is None:
            self._reference = None
            
    def _get_value(self):
        return self._value
    value = property(_get_value, _set_value)

    def reload(self):
        if self.ref:
            self.ref.ReFetch()
        
    @property
    def ref(self):
        if self.null:
            return None
        elif self._reference:
            return self._reference
        
        cached = self.record.GET_REF_CACHE ( self.column, self.value )        
        if cached:
            self._reference = cache
        else:
            self._reference = self.record.DB.XRecord ( self._fk.REFERENCED_TABLE_NAME, self.value )

        return self._reference

class XRecordChildrenList(UserList.UserList):
    def __init__(self, record, reference_name):        
        self._record = record
        self._child_def = record.SCHEMA.get_child(reference_name)
        self._data = None

    def reload(self):
        self._data = None

    def nullify(self):
        self._data = None

    def new(self, **kwargs):
        kwargs[self._child_def.COLUMN_NAME] = self._record[self._child_def.REFERENCED_COLUMN_NAME]
        return self._record.DB.XRecord ( self._child_def.TABLE_NAME, **kwargs )

    @property
    def data(self):
        if self._data is None:
            self._data = self._record.DB.XArray (
                self._child_def.TABLE_NAME,
                """SELECT * FROM "{0}" WHERE "{1}" = '{2}'""".format ( self._child_def.TABLE_NAME, self._child_def.COLUMN_NAME,
                                                                   self._record.DB.Escape ( self._record[self._child_def.REFERENCED_COLUMN_NAME] ))
                )
        return self._data

class XRecordMTMList(UserList.UserList):
    def __init__(self, record, reference_name):        
        self._record = record
        self._mtm = record.SCHEMA.get_mtm(reference_name)
        self._data = None

    def reload(self):
        self._data = None

    def nullify(self):
        self._data = None

    def add(self, **kwargs):
        mtm = self._mtm
        if isinstance(value, self._record.DB.XRecordClass):
            fk = value[mtm['to_column']]
        else:
            fk = value
        via_record = self.DB.XRecord ( mtm["via"], ** { str(mtm['via_to_column']) : fk, str(mtm['via_my_column']) : self._record[mtm['my_column']] } )
        via_record.Insert()
        return via_record
    
    @property
    def data(self):
        if self._data is None:
            mtm = self._mtm
            self._data = self._record.DB.XArray (
                mtm["to"],
                """
                SELECT ref.* FROM "{0}" ref INNER JOIN "{1}" via ON ref."{2}" = via."{3}" WHERE via."{4}" = '{5}'
                """.format ( mtm['to'], mtm['via'], mtm['to_column'], mtm['via_to_column'], mtm['via_my_column'], self._record[mtm['my_column']] )
                )
            

        return self._data
    
#class XRecordReferences(UserDict):
#    pass

class XRecordDatabase:
    """This class represents a database.        
    """
    Backend = None
    _singleton = None
    _last_init_args = ([], {})
    
    connection_defaults = {}

    class Error(Exception): pass
    class NotFound(Error): pass
    class Warning(Error): pass
    class InterfaceError(Error): pass
    class DatabaseError(Error): pass
    class DataError(Error): pass
    class IntegrityError(Error): pass
    class OperationalError(Error): pass
    class InternalError(Error): pass
    class ProgrammingError(Error): pass
    class NotSupportedError(Error): pass
    
    def Record(self, *args, **kwargs):
        return Record(*args, **kwargs)    
    
    def __init__(self, *args, **kwargs):
        from UserList import UserList
        db_instance = self
        
        self._information_schema_ = {}
        self._schema_class_ = {}
        
        self._custom_xrecord_ = {}
        self._base_xrecord_ = {}

        self._all_primary_keys_ = {}
        self._all_foreign_keys_ = {}
        
        self._sql_output_stream = None
        self._sql_query_count = 0

        self._class_manager_ = {}
        
        class XRecord:
            """
            Base class for all XRecords (active records).

            There numerous ways to instantiate an XRecord::
               
               >>> e1 = db.XRecord("blog_entry", 1)
               >>> e2 = db.Manager.blog_entry(1)
               >>> assert e1 == e2
               >>> e3 = db.XSingle("blog_entry", "SELECT * FROM blog_entry WHERE id=1" )
               >>> e4 = db.XSingle("blog_entry", "SELECT *, CONCAT('<h1>', title, '</h1>') as html_title FROM blog_entry WHERE id=1")
               >>> assert e3 == e4
               >>> print e4.html_title
               <h1>Article 1</h1>

            """
            REF_CACHE = {}            
            __db__ = db_instance            
            
            def __init__(self, table, *args, **kwargs):
                class Meta: pass
                M = Meta()
                setattr (M, 'table', table )
                setattr (M, 'schema', db_instance.GetSchema(table))
                setattr (M, 'DB', db_instance )
                setattr (M, 'references', {})
                setattr (M, 'children', {})
                setattr (M, 'changes', set() )
                setattr (M, 'original', {} )
                setattr (M, 'active', {} )
                setattr (M, 'ref_cache', {})            
                setattr (M, 'mtm', {})
                setattr (M, 'extra_data', {})
                self.__dict__['___META___'] = M

                is_sql_result = kwargs.get ( "sql_result", False )
                
                for column in self.SCHEMA.columns():                    
                    if is_sql_result:
                        v = self.TRANSLATE_FROM_SQL ( column.COLUMN_NAME, kwargs.get ( column.COLUMN_NAME ) )                    
                    else:
                        v = kwargs.get (column.COLUMN_NAME)
                    setattr ( self, column.COLUMN_NAME, v )

                if is_sql_result:
                    self.META.original = kwargs
                    for arg in kwargs:
                        if not self.SCHEMA.has_column(arg):
                            self.META.extra_data[arg] = self.TRANSLATE_FROM_SQL(arg, kwargs[arg])
                    
                self.META.changes.clear()
                
                if len(args) > 0: self.Fetch (*args)

            @classmethod
            def SET_REF_CACHE(cls, key_column, indexed_xarray={}):            
                cls.REF_CACHE[key_column] = indexed_xarray
                

            @classmethod
            def DEL_REF_CACHE(cls, key_column):
                try:
                    del cls.REF_CACHE[key_column]
                except KeyError:
                    pass
                
            @classmethod
            def GET_REF_CACHE(cls, key_column, index_value):
                try:
                    return cls.REF_CACHE[key_column][index_value]
                except KeyError:
                    return None                            

            @classmethod
            def UPDATE_REF_CACHE(cls, key_column, index_value, xrecord):
                try:
                    cls.REF_CACHE[key_column][index_value] = xrecord
                except KeyError:
                    pass
            
            def SET_FROM_RECORD(self, record):
                """Set XRecord fields from a Record instance data"""
                for (c,v) in record:
                    if self.SCHEMA.has_column(c):
                        self[c] = v
                self.META.changes.clear()
                self.META.references.clear()
                self.META.children.clear()
            
            def __eq__(self, other):
                if isinstance(other, XRecord):
                    return self.TABLE == other.TABLE and self.PK == other.PK
                return False

            def __repr__(self):
                return "<xrecord:{0.TABLE}({1})>".format (self, ",".join(map(str, self.PK)))

            def __getitem__(self, key):
                if self.META.schema.has_column(key):
                    return getattr(self, key)
                else:
                    return None
            
            def __setitem__(self, key, value):
                if self.SCHEMA.has_column(key):
                    setattr(self, key, value)
                else:
                    raise IndexError(key)            
            
            def __setattr__(self, key, value):                
                if self.META.schema.has_column (key):
                    if key in self.SCHEMA.fk:
                        if key not in self.META.references:
                            self.META.references[key] = XRecordFK(self, key)
                        self.META.references[key].value = value
                    else:
                        self.__dict__[key] = value
                    self.META.changes.add ( key )
                elif key.startswith("extra_data_"):
                    self.META.extra_data[key[11:]] = value
                elif key.upper().startswith("ADD_") and self.SCHEMA.has_mtm ( key[4:] ):
                    raise DeprecationWarning ( "Using 'add_{0}' is no longer supported, use '{0}.add(referenced_row[_id])' instead.".format ( key[4:] ) )
                else:
                    raise AttributeError(key)

            def __getattr__ (self, key):            
                if key.upper().startswith('REF_') and self.SCHEMA.has_column (key[4:]):
                    raise DeprecationWarning ( "Using 'ref_{0}' is no longer supported, use '{0}.ref' instead.".format ( key[4:] ) )
                elif key in self.SCHEMA.fk:
                    if key not in self.META.references:
                        self.META.references[key] = XRecordFK(self, key)
                    return self.META.references[key]
                elif self.SCHEMA.has_child (key):
                    if key not in self.META.children:
                        self.META.children[key] = XRecordChildrenList(self, key)
                    return self.META.children[key]
                elif self.SCHEMA.has_mtm (key):
                    if key not in self.META.mtm:
                        self.META.mtm[key] = XRecordMTMList(self, key)
                    return self.META.mtm[key]
                elif key in self.META.extra_data:
                    return self.META.extra_data[key]
                raise AttributeError(key)

            def __delattr__(self, key):
                if self.SCHEMA.has_mtm (key):
                    if key in self.META.mtm:
                        self.META.mtm.pop(key)
                elif key in self.SCHEMA.fk:
                    if key in self.META.references:
                        del self.META.references[key]

            def TRANSLATE_FROM_SQL(self, column_name, sql_returned_value):
                try:
                    method = getattr(self, 'TRANSLATE_' + column_name.upper() + '_FROM_SQL')     
                    return method(sql_returned_value)
                except AttributeError:
                    return sql_returned_value

            def TRANSLATE_TO_SQL(self, column_name, pythonic_value):
                try:
                    method = getattr(self, 'TRANSLATE_' + column_name.upper() + '_TO_SQL')
                    v = method(pythonic_value)
                    return v
                except AttributeError:
                    return pythonic_value                        
            

            def Delete(self):
                """
                Remove this row from the database. The row must be Fetched or otherwise
                initialized prior to this.

                :returns: number of affected rows, should be 1 or 0 (if row was already deleted)
                """
                where = {}
                for (c,v) in zip (self.SCHEMA.pk, self.PK):
                    where[str(c)] = v                
                old_values = self.Serialized(0)
                self.SCHEMA.pre_delete(self, where)
                ret = self.DB.CommandQuery ( self.DB.BuildDeleteSQL(self.TABLE, **where ) )
                self.SCHEMA.post_delete(self, old_values)
                self.Nullify()
                return ret
            
            @property
            def SQL_COLUMNS(self):
                for c in self.SCHEMA.column_list():
                    yield c

            @property
            def SQL_VALUES(self):
                for c in self.SCHEMA.column_list():
                    if self[c] is None:
                        yield "NULL"
                    else:
                        yield "'" + self.DB.Escape (str(self.TRANSLATE_TO_SQL(c, self[c]))) + "'"

            def GET_REFERENCED_RECORD(self, key_column, clear=False):
                if self[key_column] is None:
                    return None
                
                cached = self.GET_REF_CACHE(key_column, self[key_column])
                if cached:
                    return cached
                elif key_column in self.META.references and not clear:
                    return self.META.references[key_column]
                elif key_column in self.META.references:
                    try:
                        self.META.references[key_column].FETCH ( self[key_column] )
                    except self.NotFound, e:
                        raise self.DB.ReferenceNotFound ( '{0}({1}={2}) -> {3}({4})'.format(self.TABLE, key_column, self[key_column],
                                                                                            self.SCHEMA.fk[ref].REFERENCED_TABLE_NAME,
                                                                                            self.SCHEMA.fk[ref].REFERENCED_COLUMN_NAME))
                else:
                    self.META.references[key_column] = self.DB.XRecord ( self.SCHEMA.fk[key_column].REFERENCED_TABLE_NAME, self[key_column] )
                    if key_column in self.REF_CACHE:
                        self.UPDATE_REF_CACHE ( key_column, self[key_column], self.META.references[key_column] )
                    
                return self.META.references.get(key_column)
                    
                    

            def Nullify(self):
                """
                Make this record NULL (containing no data).
                """
                for column in self.SCHEMA.columns():
                    setattr ( self, column.COLUMN_NAME, None)                    
                self.META.changes.clear()
                self.META.children.clear()
                for fk in self.META.references.values(): fk.nullify()
                self.META.mtm.clear()
                self.META.extra_data.clear()
            
            def Fetch(self, *args, **kwargs):
                """
                Fetch a row of data to this record. May raise XRecordDatabase.NotFound. ::

                   >>> e = db.XRecord("blog_entry")
                   >>> e.Fetch(1)
                   >>> print e
                   <xrecord::blog_entry(1)>
                
                :param *args: primary key value of the row, as unnamed arguments
                :returns: nothing
                """
                if len(args) == 0: args = self.PK
                where = {}
                for (c,v) in zip(self.SCHEMA.pk, args): where[str(c)] = self.DB.Escape(v)
                
                rec = self.DB.SingleObject ( self.DB.BuildSelectSQL ( self.TABLE, 1, * self.SCHEMA.column_list(), ** where ) )
                self.Nullify()
                if rec:
                    self.META.active = True
                    self.META.original = rec
                    for (c,v) in rec:
                        self[c] = self.TRANSLATE_FROM_SQL(c, v)
                else:                
                    self.META.references.clear()
                    raise self.DB.NotFound (self.TABLE + `args`)

            def ReFetch(self):
                """
                Fetch this record's data again, losing all changes made since last Save/Fetch.
                
                :returns: nothing
                """
                self.Fetch ( * self.ORIGINAL_PK )
                
            def Save(self):
                """
                UPDATE the database with this record's data, or INSERT if the primary key is empty.
                
                :returns: number of affected rows, should by 1 or 0
                """
                pk_exists = False
                for pk in self.ORIGINAL_PK:
                    if pk is not None: pk_exists = True
                if not pk_exists: return self.Insert()
                
                where = {}
                for (c,v) in zip (self.SCHEMA.pk, self.ORIGINAL_PK):
                    where[str(c)] = v
                updates = {}
                for (c,v) in zip (self.SQL_COLUMNS, self.SQL_VALUES):
                    updates[str(c)] = v

                self.SCHEMA.pre_update(self, where, updates)
                changes = self.DB.CommandQuery ( self.DB.BuildUpdateSQL ( self.TABLE, where, ** updates ) )
                self.Fetch()
                self.SCHEMA.post_update(self)
                return changes

            def Insert(self):
                """
                INSERT a new row into the database.
                """
                insert = {}

                for (c, v) in zip (self.SQL_COLUMNS, self.SQL_VALUES):
                    if self.SCHEMA.auto_index and c in self.SCHEMA.pk:
                        pass
                    elif v:
                        insert[str(c)] = v
                        
                self.SCHEMA.pre_insert (self, insert)
                retval = self.DB.InsertQuery ( self.DB.BuildInsertSQL ( self.TABLE, **insert) )
                if self.SCHEMA.auto_index:
                    self[self.SCHEMA.pk[0]] = retval

                self.Fetch()
                self.SCHEMA.post_insert (self)
            

            @property
            def META(self):
                return self.___META___
            
            @property
            def PK(self):
                """A tuple containing this records primary key value."""
                return tuple( map(lambda c: self[c], self.SCHEMA.pk) )

            @property
            def ORIGINAL_PK(self):
                return tuple( map(lambda c: self.TRANSLATE_FROM_SQL(c, self.META.original.get(c)), self.SCHEMA.pk) )
                
            @property
            def SCHEMA(self):
                """
                The XSchema object this record was derived from.
                """
                return self.META.schema

            @property
            def TABLE(self):
                """
                Name of the table this record belongs to
                """
                return self.META.table
            Table = TABLE

            @property
            def DB(self):
                return self.META.DB

            @property
            def Modified(self):
                return len(self.META.changes) > 0
            

            def Serialized(self, depth=1):
                """
                Generate a simple Record object with this records data, following foreign keys,
                children references and mtm references up to the given depth.

                The references must be fetched prior to the call to this function.

                :param depth: the maximum recursion depth 
                :returns: a serializable representation of `self`
                :rtype: Record
                """
                ret = Record()
                for column in self.SCHEMA.column_list():
                    if column in self.SCHEMA.fk and depth > 0:
                        referenced = getattr(self, "ref_" + column)
                        if referenced:
                            setattr(ret, column, referenced.SERIALIZED(depth-1))
                        else:
                            setattr(ret, column, None)
                    else:
                        setattr(ret, column, self[column])
                if depth > 0:
                    for ref in self.META.children:
                        children = self.META.children[ref]
                        setattr(ret, ref, map (lambda r: r.SERIALIZED(depth-1), children))
                    for ref in self.META.mtm:
                        related = self.META.mtm[ref]
                        setattr(ret, ref, map (lambda r: r.SERIALIZED(depth-1), related))
                return ret
            
        def XRecordSubclass(table_name):
            """Return an XRecord subclassed, so that it's bound to one table"""
            class _XRecordSubclass(XRecord):
                
                def __init__(self, *args, **kwargs):
                    XRecord.__init__(self, table_name, *args, **kwargs)

            _XRecordSubclass.__doc__ = XRecord.__doc__

            return _XRecordSubclass

        self.XRecordSubclass = XRecordSubclass
        self.XRecordClass = XRecord
        
        class XSchemaClass:
            def __init__(self, table, *args, **kwargs):
                #_table_info, _columns, _primary_key, _foreign_key, _unique, _children, _mtm = db_instance.TableInfo (table)
                info = db_instance.TableInfo (table)                
                
                self._columns = info["columns"]
                self.info = info["table"]
                self.pk = info["primary_key"]
                self.fk = info["foreign_keys"]
                self.mtm = info["mtm"]
                self.children = {}
                for c in info["children"]:
                    self.children[c.TABLE_NAME + '_' + c.COLUMN_NAME] = c                
                self.unique = info["unique"]
                self.initialize()
                
            def initialize(self):
                pass

            def rename_child_reference(self, old_name, new_name):
                if old_name in self.children:
                    child = self.children.pop(old_name)
                    self.children[new_name] = child
                else:
                    raise Exception("No such child reference: " + old_name)
                
            def rename_mtm(self, old_name, new_name):
                if old_name in self.mtm:
                    mtm = self.mtm.pop (old_name)
                    self.mtm[new_name] = mtm               
                else:
                    raise Exception("No such foreign key: " + old_name )
                
            def table_info(self):
                pass
            
            def has_child(self, key):
                return key in self.children
            
            def get_child(self, key):
                return self.children.get (key)

            def has_mtm(self, via_table):
                return via_table in self.mtm

            def get_mtm(self, via_table):
                return self.mtm.get (via_table, None)
            
            def column_list(self):
                for c in self._columns:                    
                    yield c

            def columns(self):
                for c in self._columns.values():
                    yield c

            def has_column(self, column_name):
                return column_name in self._columns

            def null(self, column_name):
                return self._columns[column_name].IS_NULLABLE == "YES"

            def default(self, column_name):
                return self._columns[column_name].COLUMN_DEFAULT

            def pre_update(self, xrec, where_condition_dict, update_values_dict):
                pass
            def post_update(self, xrec):
                pass
            def pre_insert(self, xrec, insert_values_dict):
                pass
            def post_insert(self, xrec):
                pass
            def pre_delete(self, xrec, where_condition_dict):
                pass
            def post_delete(self, xrec, old_record):
                pass

            @property
            def verbose_info(self):
                import StringIO
                of = StringIO.StringIO()
                print >>of, "Table `{0}`."
                print >>of, "Columns:"
                print >>of, "\n".join ( map ( lambda x: "- {0.COLUMN_NAME} <{0.COLUMN_TYPE}>".format(x), self.columns() ) )
                if len(self.fk) > 0:
                    print >>of, "References:"
                    print >>of, "\n". join ( map (lambda x: "- {1.COLUMN_NAME} -> {1.REFERENCED_TABLE_NAME} ({1.REFERENCED_COLUMN_NAME})".format(*x), self.fk.items()) )
                if len(self.children) > 0:
                    print >>of, "Referenced by:"
                    print >>of, "\n". join ( map (lambda x: "- {1.REFERENCED_COLUMN_NAME} <- {1.TABLE_NAME} ({1.COLUMN_NAME})".format(*x), self.children.items()) )
                if len(self.mtm) > 0:
                    print >>of, "Many-To-Many"
                    print >>of, "\n".join ( map (lambda x: "- `{0}` to {to} ({to_column}) via {via}".format(x[0], **x[1]), self.mtm.items() ))
                return of.getvalue()

            @property
            def auto_index(self):
                return self.info.AUTO_INCREMENT 

            def __repr__(self):
                return "<Schema for {0} : ({1})>".format (self.info.TABLE_NAME, ",".join(self.column_list()))

        def XSchemaSubclass(table_name):

            class _XSchemaSubclass(XSchemaClass):

                def __init__(self, *args, **kwargs):
                    XSchemaClass.__init__(self,table_name, *args, **kwargs)
                    
            return _XSchemaSubclass
        
            
        self.XSchemaClass = XSchemaClass
        self.XSchemaSubclass = XSchemaSubclass
        

        class Manager:
            def __getattr__(self, name):
                return db_instance.XRecordCurrentClass (name)        

        self.Manager = Manager()
        self._base_schema_class_ = {}
        self._custom_schema_class_ = {}
        self._schema_instance_ = {}
        
        self.Initialize()
        
    def CustomXRecord(self, tablename):
        """A decorator used to decorate classes that provide extra functionality
        for XRecords of specified tables"""
        def _decorator(cls):
            _super = self.XRecordSubclass(tablename)
            
            class _subclassed(cls, _super):
                def __init__(self, *args, **kwargs):
                    _super.__init__(self, *args, **kwargs)
                                
            _subclassed.__name__ = "XRecord_" + tablename
            _subclassed.__doc__ = _super.__doc__
            self._custom_xrecord_[tablename] = _subclassed
            return _subclassed
        return _decorator
            
    def XRecord(self, tablename, *args, **kwargs):
        """
        Create a new instance of XRecord subclass for the given table.
        If there are any unnamed arguments, they are treated as primary key
        value, and a Fetch is performed on the record after initialization.

        The keyword arguments are used as default values for attributes, but only
        if they appear in the table schema as columns.

        :param tablename: name of the table
        :param *args: primary key value
        :param **kwargs: default attribute values
        :returns: new record
        :rtype: XRecord
        """
        return self.XRecordCurrentClass (tablename) (*args, **kwargs)

    def XRecordCurrentClass(self, tablename):
        """Get the XRecord subclass for XRecords of a specified table"""
        if tablename in self._custom_xrecord_:
            return self._custom_xrecord_ [tablename]
        else:
            if tablename not in self._base_xrecord_:
                self._base_xrecord_[tablename] = self.XRecordSubclass(tablename)
            return self._base_xrecord_[tablename]

        
    def XRecordRefCacheEnable(self, tablename, key_column, cache={}):
        """Enable reference cache for a Foreign Key (key_column) in table 'tablename'
        The optional 'cache' argument may be initialized to a dictionary like object
        containing pairs of (pk : XRecord)"""
        self.XRecordCurrentClass(tablename).SET_REF_CACHE ( key_column, cache )
    
    def XRecordRefCacheDisable(self, tablename, key_column, cache={}):
        self.XRecordCurrentClass(tablename).DEL_REF_CACHE ( key_column )
                
    def CustomXSchema(self, tablename):
        def _decorator(cls):
            _super = self.XSchemaSubclass(tablename)
            class _custom(cls, _super):
                def __init__(self, *args, **kwargs):
                    _super.__init__(self, *args, **kwargs)
            _custom.__name__ = "XSchema_" + tablename
            self._custom_schema_class_[tablename] = _custom
            return _custom
        return _decorator

    def XSchema(self, tablename, *args, **kwargs):
        if tablename not in self._schema_instance_:
            if tablename in self._custom_schema_class_:
                cls = self._custom_schema_class_[tablename]
            else:
                if tablename not in self._base_schema_class_:
                    self._base_schema_class_[tablename] = self.XSchemaSubclass ( tablename )
                cls = self._base_schema_class_[tablename]
            self._schema_instance_[tablename] = cls(*args, **kwargs)
        return self._schema_instance_[tablename]

    def ClearMetaData(self):
        """
        Forget all cached meta data. This may be used after database schema changed, and for
        some reason the application cannot be restarted.

        This is NOT recommended.
        """
        self._schema_instance_.clear()
    
    def SQLLog(self, stream):
        """
        Set the output stream object, to which all SQL queries run by this database instance are logged.
        
        :param stream: file object or None      
        """
        self._sql_output_stream = stream    
        
    def __enter__(self):
        return self
    
    def __exit__(self, type, value, traceback):                
        self.Close()

    def __del__(self):
        self.Close()
                
    @classmethod
    def getInstance(cls,*args, **kwargs):
        """
        This class method should be used to retrieve an instance of this class, or instantiate 
        a new object if it does not exist. Using this method ensures that only one connection
        is used throughout the whole process.

        If you want a new instance, call the constructor directly.
        
        **multithreading/multiprocessing**:
        NOTE: As most backend drivers are not thread safe, each new thread should have its own
        instance, or protect the access to its methods. **YOU HAVE BEEN WARNED**.
        """
        if len(args) == 0 and len(kwargs) == 0:
            args, kwargs = cls._last_init_args
        cls._last_init_args = (args, kwargs)

        if cls._singleton is None: 
            cls._singleton = cls(*args, **kwargs)

        if not cls._singleton.Test():
            try:
                cls._singleton = cls._singleton.Reconnect()
            except Exception, e:
                raise cls.ErrorTranslation (e)
            
        return cls._singleton

    def CheckConnection(self):
        """
        Check if the connection to the backend is alive, and reconnect if necessary.
        """
        if not self.Test():
            self.Reconnect()

    @classmethod
    def ErrorTranslation(self, orig_exception):
        return self.Error(orig_exception)
    
    GetSchema = XSchema
                    
    def Initialize(self):
        """Called after the contructor is finished, may be overloaded to define
        custom XRecord and XSchema classes"""
        pass
    
    def TableInfo(self, table_name):
        return self._info.GetForTable(table_name)

    @property
    def Connection(self):
        """
        Return the backend driver's connection object.

        :rtype: instance
        """
        return self._conn
    
    def Close(self):
        """Close the backend connection"""
        pass

    def GetDatabaseName(self):
        return None
    
    def Test(self):
        """Check if the connection is still active
        
        :rtype: boolean
        :returns: True if connection is alive, False otherwise
        """
        return True
    
    def Reconnect(self):
        """Reconnect to the back-end, using last known parameters"""
        return self
            
    def Escape(self, value):
        """Escape the value so it's fit to use in an SQL statement"""
        return value

    def LastError(self):
        """Last back-end error"""
        pass

    def BuildDeleteSQL(self, table, limit=1, **where):
        where_clause = " AND ".join ( map (lambda x: """"{0}" = '{1}'""".format (x[0], x[1]), where.items()) )
        return """DELETE FROM "{0}" WHERE {1}""".format ( table, where_clause, limit )
            
    def BuildSelectSQL(self, table, limit, *select, **where):
        where_clause = " AND ".join ( map (lambda x: """"{0}" = '{1}'""".format (x[0], x[1]), where.items()) )
        return """SELECT {0} FROM "{1}" WHERE {2} LIMIT {3}""".format ( ",".join(select), table, where_clause,  limit )
    
    def BuildInsertSQL(self, table, **kwargs):
        columns = ",".join(kwargs.keys())
        values = ",".join (map(lambda x: "{0}".format(x), kwargs.values()))
        return """INSERT INTO "{0}" ({1}) VALUES ({2})""".format (table, columns, values)

    def BuildUpdateSQL(self, table, where, **values):
        updates = ",".join ( map( lambda x: """"{0}" = {1}""".format(x[0], x[1]), values.items()) )
        where = " AND ".join ( map( lambda x: """"{0}" = '{1}'""".format(x[0], x[1]), where.items()) )
        return "UPDATE \"{0}\" SET {1} WHERE {2}".format (table, updates, where)
        
    def DoSQL(self, sql, *args):
        pass

    def CleanupSQL(self, resource):
        pass
    
    @contextmanager
    def Query(self, sql, *args):
        """Direct usage of Query is not recommended"""
        try:
            if self._sql_output_stream:
                self._sql_output_stream.write ( "SQL >> " + sql + "\n" )
            self._sql_query_count += 1
            res = self.DoSQL(sql, *args)
            yield res
            self.CleanupSQL(res)            
        except Exception, e:
            raise self.ErrorTranslation(e)
        finally:
            pass
            
    def SanitizeSQL (self, query, **kwargs):
        for k in kwargs:
            kwargs[k] = self.Escape (kwargs[k])
        return query % kwargs

    def FetchResultValue(self, result, row, column):
        pass
    
    def FetchRow(self, result, row):
        pass

    def FetchNextRow(self, result):
        pass

    def FetchNextRowObject(self, result, **kwargs):
        pass

    def FetchNextRowAssoc(self, result, **kwargs):
        pass
    
    def FetchRowObject(self, result, row, **kwargs):
        pass
    
    def FetchRowAssoc(self, result, row, **kwargs):
        pass
    
    def FetchResults(self, result):
        pass
    
    def FetchResultsObject(self, result, **kwargs):
        pass
    
    def FetchResultsAssoc(self, result, **kwargs):
        pass

    def AffectedRows(self, result = None):
        pass

    def InsertId(self, result):
        pass
    
    def CommandQuery(self, sql, *args):
        """
        Run an SQL query, returning the number of affected rows.

        Best used for UPDATE and DELETE queries.
        """
        with self.Query(sql, *args) as result:
            return self.AffectedRows(result)
    commandQuery = CommandQuery
    
    def InsertQuery(self,sql,*args):
        """
        Run an SQL query. If it succeeds, return the id of the `last inserted row`, otherwise
        return the number of affected rows.
        """
        with self.Query(sql,*args) as result:        
            insert_id = self.InsertId(result)
            if result: return insert_id
            return self.AffectedRows(result)
    insertQuery = InsertQuery
    
    def SingleValue(self, sql, *args):     
        """
        Run the query, and return the value of the first column in the first row of the returned result set.
        """
        with self.Query(sql, *args) as result:        
            return self.FetchResultValue(result, 0, 0)
    singleValue = SingleValue
    
    def SingleObject(self, sql, *args, **kwargs):
        """
        Run the query, and return the first row of the returned result set as a :class:`Record` object.
        """
        with self.Query(sql, *args) as result:        
            return self.FetchRowObject(result, 0, **kwargs)
    singleObject = SingleObject
    
    def SingleAssoc(self, sql, *args, **kwargs):
        """
        Run the query, and return the first row of the returned result set as a dictionary.
        """
        with self.Query(sql) as result:        
            return self.FetchRowAssoc(result, 0, **kwargs)
    singleAssoc = SingleAssoc
    
    def ArrayObject(self, sql, *args, **kwargs):
        """
        Run the query, and return the result set as an array of :class:`Record` objects.
        """
        with self.Query(sql) as result:
            return self.FetchResultsObject(result, **kwargs)

    def LazyArrayObject(self, sql, *args, **kwargs):
        with self.Query(sql) as result:
            while True:
                next_result = self.FetchNextRowObject(result)
                if next_result: yield next_result
                else: raise StopIteration
    
    def ExtendObject(self, obj, sql, *args):
        """
        Run the query, and set the corresponding attributes of the given object to the values from the first
        row of the returned result set.
        
        Will not work on new-style class objects.
        """
        with self.Query(sql, *args) as result:        
            if result:
                for column_name in result:
                    setattr (obj, column_name, result[column_name] )
            return obj
    extendObject = ExtendObject
    
    def ArrayObjectIndexed(self, sql, index_column, *args, **kwargs):
        """
        Run the query, and return the result set as dictionary with the key set to
        the value of the `index_column` of each row of the returned result set, and
        the value set to the corresponding :class:`Record` object.

        If values of `index_column` are not unique, each subsequent record overwrites
        the previous key-value mapping for the given key.

        :rtype: dict
        """
        with self.Query(sql, *args) as result:        
            retval = {}
            for row in self.FetchResultsObject(result, **kwargs):
                retval[ getattr(row, index_column) ] = row

            return retval
    ObjectArrayIndexed = ArrayObjectIndexed
    indexedArrayOfObjects = ArrayObjectIndexed
    
    def ArrayObjectIndexedList (self, sql, index_column, *args, **kwargs):
        """
        Run the query, and return the result set as dictionary with the key set to
        the value of the `index_column` of each row of the returned result set, and
        the value set to a list of the corresponding :class:`Record`objects.

        If values of `index_column` are unique, this function returns a key=>value
        mapping where all values are lists of length 1.

        :rtype: dict
        """
        with self.Query(sql, *args) as result:
            retval = {}
            for row in self.FetchResultsObject(result, **kwargs):
                idx = getattr (row, index_column)
                retval[ idx ] = retval.get ( idx, [] )
                retval[ idx ].append (row)
            return retval
    
    def ArrayAssoc(self, sql, *args):
        """
        Same as `ArrayObject`, but returns dicts instead of :class:`Record` objects;
        """
        with self.Query(sql, *args) as result:        
            return self.FetchResultsAssoc(result)

    def LazyArrayAssoc(self, sql, *args, **kwargs):
        with self.Query(sql) as result:
            while True:
                next_result = self.FetchNextRowAssoc(result)
                if next_result: yield next_result
                else: raise StopIteration
    
    def ArrayAssocIndexed (self, sql, index_column, *args, **kwargs):
        """
        Same as `ArrayObjectIndexed`, but returns dicts instead of :class:`Record` objects;
        """
        with self.Query(sql, *args) as result:
            retval = {}
            for row in self.FetchResultsAssoc(result, **kwargs):
                retval[row[index_column]] = row
            return retval
    
    def ArrayAssocIndexedList (self, sql, index_column, *args, **kwargs):
        """
        Same as `ArrayObjectIndexedList`, but returns dicts instead of :class:`Record` objects;
        """
        with self.Query(sql, *args) as result:
            retval = {}
            for row in self.FetchResultsAssoc(result, **kwargs):
                idx = row[index_column]
                retval[ idx ] = retval.get ( idx, [] )
                retval[ idx ].append (row)
            return retval
    
    def XArray(self, table, sql=None, *args, **kwargs):
        """
        Same as `ArrayObject`, but returns :class:`XRecord` objects for the given `table` 
        instead of :class:`Record` objects.

        If `sql` is None (default) returns all records in the table.
        """
        if sql:
            array = self.ArrayAssoc ( self.SanitizeSQL(sql, **kwargs), *args )
        else:
            array = self.ArrayAssoc ( "SELECT * FROM {0}".format(table) )
        return map ( lambda a : self.XRecord(table, sql_result=True, **a), array )

    def LazyXArray(self, table, sql=None, *args, **kwargs):
        """
        Same as `ArrayObject`, but returns :class:`XRecord` objects for the given `table` 
        instead of :class:`Record` objects.

        If `sql` is None (default) returns all records in the table.
        """
        if sql:
            generator = self.LazyArrayAssoc ( self.SanitizeSQL(sql, **kwargs), *args )
        else:
            generator = self.LazyArrayAssoc ( """SELECT * FROM "{0}" """.format(table) )
        for assoc in generator:
            yield self.XRecord(table, sql_result=True, **assoc)

    def XArrayIndexed (self, table, index_column, sql=None, *args, **kwargs):
        """
        Same as `ArrayObjectIndexed`, but returns :class:`XRecord` objects for the given `table` 
        instead of :class:`Record` objects.

        If `sql` is None (default) returns all records in the table.
        """
        array = self.XArray ( table, sql, *args, **kwargs)
        indexed = {}
        for r in array:
            indexed[r[index_column]] = r
        return indexed
    
    def XArrayIndexedList (self, table, index_column, sql=None, *args, **kwargs):
        """
        Same as `ArrayObjectIndexedList`, but returns :class:`XRecord` objects for the given `table` 
        instead of :class:`Record` objects.

        If `sql` is None (default) returns all records in the table.
        """
        array = self.XArray ( table, sql, *args, **kwargs)
        indexed = {}
        for r in array:
            indexed[r[index_column]] = indexed.get ( r[index_column], [] )
            indexed[r[index_column]].append (r)
        return indexed
    
    def XSingle(self, table, sql=None, *args):
        """
        Same as `SingleObject`, but returns :class:`XRecord` objects for the given `table` 
        instead of :class:`Record` objects.

        If `sql` is None returns the object with its primary key value equal to the
        unnamed arguments.
        """
        if sql:
            return self.XRecord(table, sql_result=True, ** (self.SingleAssoc (sql)) )
        else:
            return self.XRecord(table, *args )
    
