#
#  Licensed Materials - Property of IBM
#
#  (c) Copyright IBM Corp. 2007
#

import unittest, sys
import ibm_db
import config
from testfunctions import IbmDbTestFunctions

class IbmDbTestCase(unittest.TestCase):
  def test_263(self):
    obj = IbmDbTestFunctions()
    obj.assert_expect(self.run_test_263)

  def run_test_263(self):
    conn = ibm_db.connect(config.database, config.user, config.password)

    if conn:
      serverinfo = ibm_db.server_info(conn)
      server = serverinfo.DBMS_NAME[0:3]

      try:
        result = ibm_db.exec_immediate(conn, "drop table typetest")
      except:
        pass

      if (server == 'IDS'):
        create = "create table typetest (col1 smallint, col2 integer, \
                 col3 integer, col4 int8, col5 real, col6 double precision, \
                 col7 float, col8 decimal(5, 2), col9 numeric(5, 2), \
                 col10 smallfloat, col11 money(5,2))"
      else:
        create = "create table typetest (col1 smallint, col2 int, col3 integer, \
                 col4 bigint, col5 real, col6 double, col7 float, \
                 col8 dec(5, 2), col9 numeric(5, 2), col10 num(5, 2), \
                 col11 decimal(5,2))"

      result = ibm_db.exec_immediate(conn, create);
      insert = "insert into typetest values(1, 1, 1, 1, 1.0, 1.0, 1.0, 1.0, \
                  1.0, 1.0, 1.0)"
      result = ibm_db.exec_immediate(conn, insert);

      insert = "insert into typetest values(0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)"
      result = ibm_db.exec_immediate(conn, insert);

      insert = "insert into typetest values(-500, -500, -500, -500, -500.23, \
                  -500.23, -500.23, -500.23, -500.23, -500.23, -500.23)"
      result = ibm_db.exec_immediate(conn, insert);

      insert = "insert into typetest values(Null, Null, Null, Null, Null, Null, \
                  Null, Null, Null, Null, Null)"
      result = ibm_db.exec_immediate(conn, insert);

      sql = 'select * from typetest'
      stmt = ibm_db.prepare(conn, sql)
      ibm_db.execute(stmt)
      data = ibm_db.fetch_tuple(stmt)
      while (data):
        print str(data)
        data = ibm_db.fetch_tuple( stmt)

    else:
      print "Connection failed."

#__END__
#__LUW_EXPECTED__
#(1, 1L, 1L, '1', 1.0, 1.0, 1.0, '1.00', '1.00', '1.00', '1.00')
#(0, 0L, 0L, '0', 0.0, 0.0, 0.0, '0.00', '0.00', '0.00', '0.00')
#(-500, -500L, -500L, '-500', -500.23001098632812, -500.23000000000002, -500.23000000000002, '-500.23', '-500.23', '-500.23', '-500.23')
#(None, None, None, None, None, None, None, None, None, None, None)
#__ZOS_EXPECTED__
#(1, 1L, 1L, '1', 1.0, 1.0, 1.0, '1.00', '1.00', '1.00', '1.00')
#(0, 0L, 0L, '0', 0.0, 0.0, 0.0, '0.00', '0.00', '0.00', '0.00')
#(-500, -500L, -500L, '-500', -500.23001098632812, -500.23000000000002, -500.23000000000002, '-500.23', '-500.23', '-500.23', '-500.23')
#(None, None, None, None, None, None, None, None, None, None, None)
#__SYSTEMI_EXPECTED__
#(1, 1L, 1L, '1', 1.0, 1.0, 1.0, '1.00', '1.00', '1.00', '1.00')
#(0, 0L, 0L, '0', 0.0, 0.0, 0.0, '0.00', '0.00', '0.00', '0.00')
#(-500, -500L, -500L, '-500', -500.23001098632812, -500.23000000000002, -500.23000000000002, '-500.23', '-500.23', '-500.23', '-500.23')
#(None, None, None, None, None, None, None, None, None, None, None)
#__IDS_EXPECTED__
#(1, 1L, 1L, '1', 1.0, 1.0, 1.0, '1.00', '1.00', 1.0, '1.00')
#(0, 0L, 0L, '0', 0.0, 0.0, 0.0, '0.00', '0.00', 0.0, '0.00')
#(-500, -500L, -500L, '-500', -500.23001098632812, -500.23000000000002, -500.23000000000002, '-500.23', '-500.23', -500.23001098632812, '-500.23')
#(None, None, None, None, None, None, None, None, None, None, None)
