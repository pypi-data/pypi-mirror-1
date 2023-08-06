from drizzle import libdrizzle
def process_args():
    from optparse import OptionParser
    parser = OptionParser()
    parser.add_option("-a", "--add", action="store_true", dest="add",
                      help="Add a name to my database.")
    parser.add_option("-n", "--name", action="store", dest="name",
                      help="Name to add to my database.")
    return parser.parse_args()

process_args()
d=libdrizzle.Drizzle()
c=d.create_client_connection()
c.set_tcp("localhost",9306)
c.set_auth("root",None)
c.set_db("test")
c.connect()
r=c.query("SELECT id, k, c  FROM sbtest")


while True:
  column=r.column_read()
  if column is None:
    break
  print """
Field:   catalog=%s
              db=%s
           table=%s
       org_table=%s
            name=%s
        org_name=%s
         charset=%d
          length=%d
            type=%d
           flags=%d""" % (column.catalog(), column.db(),
         column.table(), column.orig_table(),
         column.name(), column.orig_name(),
         column.charset(), column.size(),
         column.type(), column.flags())

print """
Result:     row_count=%d
            insert_id=%d
        warning_count=%d
          column_count=%d
	    error_code=%d
""" % ( r.row_count(),
        r.insert_id(),
        r.warning_count(),
        r.column_count(),
        r.error_code())


while True:
  row=r.row_read()
  if row == 0:
    break
  print "Row: %d" % (row)
  for x in range(0,r.column_count()):
    f=r.field_buffer()
    print "\t(%d) %s" % (len(f),f)
    r.field_free(f)
  print

print r.row_count()
