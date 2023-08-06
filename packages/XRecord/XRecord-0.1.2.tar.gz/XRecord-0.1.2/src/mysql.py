# -*- coding: utf8 -*-
from contextlib import contextmanager
import datetime
import re
from db import XRecordDatabase

__all__ = [ "XRecordMySQL" ]

try:
    import _mysql
    import MySQLdb
except ImportError:
    from sys import stderr
    print >>stderr, "Unable to import the MySQLdb module. Please check if this extension is installed within your PYTHONPATH."
    
    
class XRecordMySQL(XRecordDatabase):
    Backend = "MYSQL"
    
    def __init__(self, **kwargs):
        XRecordDatabase.__init__(self, **kwargs)
        from MySQLdb.constants import FIELD_TYPE as FT
        from MySQLdb.converters import conversions
        
        self._host = kwargs.get ( 'host', self.connection_defaults.get ('host', 'localhost') )
        self._port = kwargs.get ( 'port', self.connection_defaults.get ('port', 3306) )
        self._dbname = kwargs.get ( 'name', self.connection_defaults.get ('name') )
        self._user = kwargs.get ( 'user', self.connection_defaults.get ('user') ) 
        self._pass = kwargs.get ( 'password', self.connection_defaults.get ('password', '') ) 

        self.escape_function = _mysql.escape_string        
        self._conversion = conversions
        self._conversion[FT.VARCHAR] = unicode        
        
        self.Reconnect()

    def Escape(self, v):
        return self.escape_function(str(v))
    
    def Reconnect(self):
        from _mysql_exceptions import ProgrammingError
        try:
            self._conn.close()
        except AttributeError:
            pass
        except ProgrammingError:
            pass
        
        self._conn = _mysql.connect ( host = self._host, user = self._user,
                                      passwd = self._pass, db = self._dbname, port = self._port )
        self._conn.set_character_set ( "UTF8" )        
        self._conn.select_db ( self._dbname )
        return self
    
    def Test(self):
        import _mysql_exceptions 
        try:
            self._conn.ping()
        except _mysql_exceptions.Error:
            return False        
        except InterfaceError:
            return False
        
        return True

    @classmethod
    def ErrorTranslation(self, orig):
        import _mysql_exceptions as my
        try:
            raise orig
        except my.OperationalError, e:
            return self.OperationalError (e)
        except my.Warning, e:
            return self.Warning (e)
        except my.InterfaceError, e:
            return self.InterfaceError (e)
        except my.DatabaseError, e:
            return self.DatabaseError (e)
        except my.DataError, e:
            return self.DataError (e)
        except my.OperationalError, e:
            return self.OperationalError (e)
        except my.IntegrityError, e:
            return self.IntegrityError (e)
        except my.InternalError, e:
            return self.InternalError (e)
        except my.ProgrammingError, e:
            return self.ProgrammingError (e)        

        return self.Error(orig)

    def TableInfo(self, table):
        #print "TableInfo", table
        if table not in self._all_primary_keys_:
            pks = self.ArrayObjectIndexedList (
                """
                SELECT C.TABLE_NAME, K.COLUMN_NAME FROM INFORMATION_SCHEMA.TABLE_CONSTRAINTS C INNER JOIN INFORMATION_SCHEMA.KEY_COLUMN_USAGE K
                ON C.CONSTRAINT_NAME = K.CONSTRAINT_NAME AND C.TABLE_SCHEMA = K.TABLE_SCHEMA AND K.TABLE_NAME = C.TABLE_NAME
                WHERE
                C.TABLE_SCHEMA = '{0}' AND C.CONSTRAINT_TYPE = 'PRIMARY KEY'                
                """.format (self._dbname), "TABLE_NAME" )            
            for (t, pk) in pks.items():
                self._all_primary_keys_ [t] = tuple(map ( lambda x: x.COLUMN_NAME, pk ))

            fks = self.ArrayObjectIndexedList (
                """
                SELECT * FROM INFORMATION_SCHEMA.TABLE_CONSTRAINTS C INNER JOIN INFORMATION_SCHEMA.KEY_COLUMN_USAGE K
                ON C.CONSTRAINT_NAME = K.CONSTRAINT_NAME AND C.TABLE_SCHEMA = K.TABLE_SCHEMA AND K.TABLE_NAME = C.TABLE_NAME
                WHERE
                C.TABLE_SCHEMA = '{0}' AND C.CONSTRAINT_TYPE = 'FOREIGN KEY'                
                """.format (self._dbname), "TABLE_NAME" )
            self._all_foreign_keys_ = fks
            #print map(lambda t : (t[0], t[1]), pks.items() )
            
        table_info = self.SingleObject (
            """
            SELECT * FROM INFORMATION_SCHEMA.TABLES
            WHERE TABLE_SCHEMA = '{0._dbname}' AND TABLE_NAME = '{1}'
            """.format(self, table))
        columns = self.ArrayObjectIndexed (
            """
            SELECT * FROM INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_SCHEMA = '{0._dbname}' AND TABLE_NAME = '{1}' ORDER BY ORDINAL_POSITION
            """.format(self,table), "COLUMN_NAME")
        #All table constraints - primary, foreign and unique keys
        constraints = self.ArrayObject (
            """
            SELECT * FROM INFORMATION_SCHEMA.TABLE_CONSTRAINTS
            WHERE TABLE_SCHEMA = '{0._dbname}' AND TABLE_NAME = '{1}'
            """.format(self,table))
        #Children - other tables' foreign keys pointing to this table
        children = self.ArrayObject ( 
            """
            SELECT * FROM INFORMATION_SCHEMA.TABLE_CONSTRAINTS C 
            INNER JOIN INFORMATION_SCHEMA.KEY_COLUMN_USAGE K ON K.CONSTRAINT_NAME = C.CONSTRAINT_NAME
            WHERE 
            C.CONSTRAINT_SCHEMA = '{0}' AND
            K.CONSTRAINT_SCHEMA = '{0}' AND
            C.CONSTRAINT_TYPE = 'FOREIGN KEY' AND 
            K.REFERENCED_TABLE_NAME = '{1}'
            """.format ( self._dbname, table ))
        
        primary_key = None
        foreign_keys = {}
        unique = []
        for c in constraints:
            key_columns = self.ArrayObject (
                """
                SELECT * FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE
                WHERE CONSTRAINT_NAME = '{0.CONSTRAINT_NAME}' AND TABLE_NAME = '{1}'
                """.format(c,table))
            if c.CONSTRAINT_TYPE == "PRIMARY KEY":
                primary_key = map(lambda x: x.COLUMN_NAME, key_columns)
            elif c.CONSTRAINT_TYPE == "FOREIGN KEY":
                kc = key_columns[0]
                foreign_keys[kc.COLUMN_NAME] = kc                
            elif c.CONSTRAINT_TYPE == "UNIQUE":
                unique.append ( key_columns )

        #Many-to-many relationships detection, through tables that:
        # 1. Have a foreign key to this table (f1)
        # 2. Have a foreign key to one other table (f2)
        # 3. Have (f1,f2) or (f2,f1) as their primary key

        #We already have f1 (children):
        mtm = {}
        for f1 in children:
            #Get other Foreign Keys (from cache)
            f2 = self._all_foreign_keys_[f1.TABLE_NAME]
            for f2x in f2:
                if f2x.CONSTRAINT_NAME == f1.CONSTRAINT_NAME: continue
                #For each foreign key, other than the one pointing to this table, check if primary key matches:
                if (f1.COLUMN_NAME, f2x.COLUMN_NAME) == self._all_primary_keys_[f1.TABLE_NAME] or (f2x.COLUMN_NAME, f1.COLUMN_NAME) == self._all_primary_keys_[f1.TABLE_NAME]:
                    mtm[f1.TABLE_NAME] = {
                        'to' : f2x.REFERENCED_TABLE_NAME,
                        'via' : f1.TABLE_NAME,
                        'via_to_column' : f2x.COLUMN_NAME,
                        'to_column' : f2x.REFERENCED_COLUMN_NAME,                        
                        'via_my_column' : f1.COLUMN_NAME,
                        'my_column' : f1.REFERENCED_COLUMN_NAME
                        }                
        return (table_info, columns, primary_key, foreign_keys, unique, children, mtm)

    def DoSQL(self, sql):
        self._conn.query ( sql )
        return self._conn.store_result()                

    def Close(self):        
        from _mysql_exceptions import ProgrammingError
        try:
            self._conn.close()
        except ProgrammingError:
            pass        
        
    def AffectedRows(self, result = None):
        return self._conn.affected_rows()

    def InsertId(self, result):
        return self._conn.insert_id()
    
    def FetchResultValue (self, result, row, col):
        if result.num_rows() > row:
            result.data_seek (row)
        else:
            return None
        row_data = result.fetch_row()
        if len(row_data) > 0:
            if result.num_fields() > 0:
                return row_data[0][col]
        return None
    
    def FetchRow(self, result, row):
        if result.num_rows() > row:
            result.data_seek (row)
            return result.fetch_row()[0]
        return None

    def FetchRows(self, result):            
        while True:            
            row = self.FetchNextRow(result)
            if row:
                yield row
            else:
                raise StopIteration

    def FetchNextRow(self, result):
        try:
            return result.fetch_row()[0]
        except IndexError:
            return None
    
    def FetchNextRowObject(self, result):
        pass

    def _RowToObject ( self, description, row_data):
        if row_data is None: return None
        obj = self.Record()
        for (idx, column_value) in enumerate(row_data):            
            cname, value = self._ParseValue (description[idx], column_value)
            setattr (obj, cname, value)
        return obj
    
    def _RowToAssoc ( self, description, row_data):
        if row_data is None: return None
        obj = {}
        for (idx, column_value) in enumerate(row_data):
            cname, value = self._ParseValue (description[idx], column_value)            
            obj[cname] = value            
        return obj

    def _ParseValue(self, description, value):        
        cname, ctype, cmax, clength, _, cdec, cnull = description                
        
        if value is None: return cname, value
        conv = self._conversion[ctype] 
        if isinstance(conv, list):
            _, conv = conv[0]
        
        return cname, conv(value)
    
    def FetchRowObject(self, result, row):
        return self._RowToObject(result.describe(), self.FetchRow(result, row))    
    
    def FetchNextRowObject(self, result):        
        return self._RowToObject(result.describe(), self.FetchNextRow(result))    
    
    def FetchRowAssoc(self, result, row):
        return self._RowToAssoc(result.describe(), self.FetchRow(result, row))    
    
    def FetchResultsObject(self, result):                
        return [ self._RowToObject ( result.describe(), row) for row in self.FetchRows(result) ]
        
    def FetchResultsAssoc(self, result):
        return [ self._RowToAssoc ( result.describe(), row) for row in self.FetchRows(result) ]

        

    
