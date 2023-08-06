# -*- coding: utf-8 -*-
from contextlib import contextmanager
import datetime
import re
from db import XRecordDatabase, Record

__all__ = ["XRecordSqlite"]

try:
    import sqlite3
except ImportError:
    from sys import stderr
    print >>stderr, "Unable to import the Sqlite3 module. Please check if this extension is installed within your PYTHONPATH:"
    print >>stderr, "\n".join(sys.path)
    
class XRecordSqlite(XRecordDatabase):
    Backend = "SQLITE"

    class ResultWrapper:
        def __init__ (self, cursor):
            self.close = cursor.close
            self.next = cursor.next
            self.description = cursor.description
            self.lastrowid = cursor.lastrowid
            self._data = None
            self.cursor = cursor

        @property
        def data(self):
            if self._data is None:
                self._data = self.cursor.fetchall()
            return self._data
        
        @property
        def rowcount(self):
             return len(self.data)

        def __getitem__(self, key):
            return self.data[key]

        
    def __init__(self, **kwargs):
        XRecordDatabase.__init__(self, **kwargs)        
        self._dbname = kwargs.get ( 'name', self.connection_defaults.get ('name') )
        self.Reconnect()
    
    def Reconnect(self):
        try:
            self._conn.close()
        except AttributeError:
            pass
        
        self._conn = sqlite3.connect ( self._dbname )
        self._conn.row_factory = sqlite3.Row
        self._conn.isolation_level = None
        return self

    @classmethod
    def ErrorTranslation(self, orig):
        try:
            raise orig
        except sqlite3.OperationalError, e:
            return self.OperationalError (e)
        except sqlite3.Warning, e:
            return self.Warning (e)
        except sqlite3.InterfaceError, e:
            return self.InterfaceError (e)
        except sqlite3.DatabaseError, e:
            return self.DatabaseError (e)
        except sqlite3.DataError, e:
            return self.DataError (e)
        except sqlite3.OperationalError, e:
            return self.OperationalError (e)
        except sqlite3.IntegrityError, e:
            return self.IntegrityError (e)
        except sqlite3.InternalError, e:
            return self.InternalError (e)
        except sqlite3.ProgrammingError, e:
            return self.ProgrammingError (e)        

        return self.Error(orig)
    
    def Test(self):
        try:
            c = self._conn.cursor()
        except:
            return False
        return True

    def TableInfo(self, table):
        
        if not hasattr(self, "_meta_data_") or table not in self._meta_data_:
            tables = self.ArrayAssocIndexed ( "SELECT * FROM sqlite_master WHERE type='table'", "name" )
            for tbl in tables:
                tables[tbl]['children'] = []
                tables[tbl]['mtm'] = []
                
            for tbl in tables:
                tables[tbl]['columns'] = self.ArrayObjectIndexed ( "PRAGMA table_info ({0})".format (tbl), "name" )
                tables[tbl]['fk'] = self.ArrayObjectIndexed ( "PRAGMA foreign_key_list ({0})".format (tbl), "from" )
                tables[tbl]['pk'] = tuple(map( lambda x: x.name, filter ( lambda x: x.pk == 1, tables[tbl]['columns'].values() )))
                for fk in tables[tbl]['fk'].values():
                   tables[fk.table]['children'].append ( fk )

            translated = {}
            for tbl in tables:
                translated_tbl = {}
                tinfo = Record()
                tinfo['TABLE_SCHEMA'] = self._dbname
                tinfo['TABLE_NAME'] = tbl
                tinfo['TABLE_TYPE'] = "BASE TABLE"
                tinfo['AUTO_INCREMENT'] = "autoincrement" in tables[tbl]['sql']
                translated_tbl['info'] = tinfo
                translated_tbl['columns'] = {}
                for op, (column, c) in enumerate(tables[tbl]['columns'].items()):
                    t_column = Record()
                    t_column['ORDINAL_POSITION'] = op
                    t_column['TABLE_SCHEMA'] = self._dbname
                    t_column['TABLE_NAME'] = tbl
                    t_column['COLUMN_NAME'] = column
                    t_column['COLUMN_TYPE'] = c.type
                    t_column['DATA_TYPE'] = c.type
                    t_column['COLUMN_DEFAULT'] = c.dflt_value
                    translated_tbl['columns'][column] = t_column
                translated_tbl['fk'] = {}
                for op, (column, fk) in enumerate(tables[tbl]['fk'].items()):
                    t_fk = Record()
                    t_fk['ORDINAL_POSITION'] = op
                    t_fk['CONSTRAINT_SCHEMA'] = self._dbname
                    t_fk['CONSTRAINT_NAME'] = self._dbname + '_' + tbl + '_' + column + '_' + fk.table + '_' + hex(id(fk))
                    t_fk['TABLE_NAME'] = tbl
                    t_fk['TABLE_SCHEMA'] = self._dbname
                    t_fk['CONSTRAINT_TYPE'] = "FOREIGN KEY"
                    t_fk['COLUMN_NAME'] = column
                    t_fk['REFERENCED_TABLE_SCHEMA'] = self._dbname
                    t_fk['REFERENCED_TABLE_NAME'] = fk.table
                    t_fk['REFERENCED_COLUMN_NAME'] = fk.to
                    translated_tbl['fk'][column] = t_fk
                translated_tbl['children'] = []
                translated_tbl['mtm'] = {}
                translated_tbl['pk'] = tables[tbl]['pk']
                translated[tbl] = translated_tbl

            for tbl, t in translated.items():
                for (column, fk) in t['fk'].items():
                    translated[fk.REFERENCED_TABLE_NAME]['children'].append (fk)

            for tbl, t in translated.items():
                for f1 in t['children']:
                    f2 = translated[f1.TABLE_NAME]['fk']
                    pk2 = translated[f1.TABLE_NAME]['pk']
                    for fk_column, f2x in f2.items():
                        if f2x.CONSTRAINT_NAME == f1.CONSTRAINT_NAME: continue
                        if (f1.COLUMN_NAME, f2x.COLUMN_NAME) == pk2 or (f2x.COLUMN_NAME, f1.COLUMN_NAME) == pk2:
                            t['mtm'][f1.TABLE_NAME] = {
                                'to' : f2x.REFERENCED_TABLE_NAME,
                                'via' : f1.TABLE_NAME,
                                'via_to_column' : f2x.COLUMN_NAME,
                                'to_column' : f2x.REFERENCED_COLUMN_NAME,                        
                                'via_my_column' : f1.COLUMN_NAME,
                                'my_column' : f1.REFERENCED_COLUMN_NAME
                                }                
                        pass
                    pass
                pass
            self._meta_data_ = translated
        md = self._meta_data_[table]
        return ( md['info'], md['columns'], md['pk'], md['fk'], [], md['children'], md['mtm'] )

    def BuildDeleteSQL(self, table, limit=1, **where):
        where_clause = " AND ".join ( map (lambda x: "{0} = '{1}'".format (x[0], x[1]), where.items()) )
        return "DELETE FROM {0} WHERE {1}".format ( table, where_clause, limit )
            
    def BuildSelectSQL(self, table, limit, *select, **where):
        where_clause = " AND ".join ( map (lambda x: "{0} = '{1}'".format (x[0], x[1]), where.items()) )
        return "SELECT {0} FROM {1} WHERE {2} LIMIT {3}".format ( ",".join(select), table, where_clause,  limit )
    
    def BuildInsertSQL(self, table, **kwargs):
        columns = ",".join(kwargs.keys())
        values = ",".join (map(lambda x: "{0}".format(x), kwargs.values()))
        return "INSERT INTO {0} ({1}) VALUES ({2})".format (table, columns, values)

    def BuildUpdateSQL(self, table, where, limit=1, **values):
        updates = ",".join ( map( lambda x: "{0} = {1}".format(x[0], x[1]), values.items()) )
        where = " AND ".join ( map( lambda x: "{0} = '{1}'".format(x[0], x[1]), where.items()) )
        return "UPDATE {0} SET {1} WHERE {2}".format (table, updates, where, limit)
    
    def DoSQL(self, sql, *args):
        c = self._conn.cursor()
        c.execute ( sql, args )
        return self.ResultWrapper(c)

    def CleanupSQL(self, result):
        result.close()
    
    def Close(self):        
        self._conn.close()
        
    def AffectedRows(self, result = None):
        return 0
    
    def InsertId(self, result):
        return result.lastrowid
    
    def FetchResultValue (self, result, row, col):
        if result.rowcount > row:
            row_data = result[row]
        else:
            return None
        if len(result.description) > col:
            return row_data[col]
        return None
    
    def FetchRow(self, result, row):
        if result.rowcount > row:
             return result[row]
        return None

    def FetchRows(self, result):            
        while True:
            yield self.FetchNextRow(result)

    def FetchNextRow(self, result):
        return result.next()
    
    def _RowToObject ( self, description, row_data):
        if row_data is None: return None
        obj = self.Record()
        for (column_name, column_value) in zip(map(lambda x: x[0], description),row_data):            
            setattr (obj, column_name, column_value)
        return obj
    
    def _RowToAssoc ( self, description, row_data):
        if row_data is None: return None
        obj = {}
        for (column_name, column_value) in zip(map(lambda x: x[0], description),row_data):            
            obj[column_name] = column_value
        return obj


    def FetchRowObject(self, result, row):
        return self._RowToObject(result.description, self.FetchRow(result, row))    
    
    def FetchNextRowObject(self, result):        
        return self._RowToObject(result.description, self.FetchNextRow(result))    
    
    def FetchRowAssoc(self, result, row):
        return self._RowToAssoc(result.description, self.FetchRow(result, row))    
    
    def FetchResultsObject(self, result):                
        return [ self._RowToObject ( result.description, row) for row in self.FetchRows(result) ]
        
    def FetchResultsAssoc(self, result):
        return [ self._RowToAssoc ( result.description, row) for row in self.FetchRows(result) ]

        

    
