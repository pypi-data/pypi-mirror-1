
import sys

sys.path.append ( "./xrecord/" )

from src.db import XRecordDatabase, Record
from src.sqlite import XRecordSqlite
from src.mysql import XRecordMySQL

db = XRecordSqlite ( name=":memory:" )
db.CommandQuery ( "CREATE TABLE a(i integer primary key,j,k,l)" )

XRecord = db.XRecordCurrentClass("a")
XSchema = db.XSchema("a").__class__

XSchema.__name__ = "XSchema"
XRecord.__name__ = "XRecord"

__all__ = ["XRecordDatabase", "XRecordSqlite", "XRecordMySQL", "XSchema", "Record", "XRecord"]
