from drizzle import libdrizzle

d=libdrizzle.Drizzle()
c=d.add_tcp("localhost",3306,"root",None,"test", libdrizzle.DRIZZLE_CON_MYSQL)
r=c.query("select * from sbtest")

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

print r.row_count()
x=0
while True:
  x+=1
  row=r.row_buffer()
  if row is None:
    break
  print "Row: %d" % x
  for y in range(0,len(row)-1):
    print "\t(%d) %s" % (len(row[y]),row[y])
  print
  r.row_free(row)
