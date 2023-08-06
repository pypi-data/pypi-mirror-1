#!/bin/env python
from sqlite import XRecordSqlite
from mysql import XRecordMySQL
from postgresql import XRecordPostgreSQL
from db import XRecordFK

import sys

class MyDatabase(XRecordMySQL):

    def Initialize(self):
        self.SQL2Value("customer", "name") ( lambda x,y: str.upper(x) )
        @self.CustomXSchema("customer")
        class customer:
            def initialize(self):
                self.rename_mtm ( "customer_ip_device", "devices" )
                                
db = MyDatabase ( name = "netcon", user = "netcon" )
#db.SQLLog ( sys.stdout )
db.XRecordRefCacheEnable ( "customer", "cos" )

print "XRecord Feature Test Suite"

try:
    cust1 = db.Manager.customer(id='testing/0001', name='Jan Kowalski', status='OK')
    print cust1, cust1.cos.ref
    cust1.insert()
except db.DatabaseError:
    cust1 = db.Manager.customer ( 'testing/0001' )

print "Fetched Customer: ", cust1, cust1.name, cust1._last_update 
print "COS=", cust1.cos.ref

cust1.cos = 1
cust1.email = 'test@test.pl'
cust1.code = '0000/0001'
cust1.save()

cos_users = cust1.cos.ref.customer_cos
print "Users:", len(cos_users)

print "Customer devices: "
for dev in cust1.devices:
    print dev

cust1.customer_ip_assignment_customer.clear()

ip1 = cust1.customer_ip_assignment_customer.new(blocked=0)
ip1.ip = 1
ip1.save()

print "Customer ip: "
for ip in cust1.customer_ip_assignment_customer:
    print ip

print "Removing devices..."
cust1.devices.clear()

some_devices = db.XArray ( "ip_device", "SELECT * FROM ip_device LIMIT 3" )

for device in some_devices:
    print "Adding", device, "to", cust1
    cust1.devices.add (device)

print "Checking device customers:"
for device in some_devices:
    print device.customer_ip_device

print "Deleting customer"
cust1.delete()




db.Close()
