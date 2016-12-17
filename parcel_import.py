import csv
import MySQLdb

mydb = MySQLdb.connect(	host='vhostdb.ucr.edu',
						user='inspect1',
						passwd='TIMwPyDHSPbb',
						db='inspect1')
						
cursor = mydb.cursor()
csv_data = csv.reader(file('resparcels.csv'))
for row in csv_data:
	if len(row) == 3:
		try:
			cursor.execute("INSERT INTO property_reserves_apn VALUES('',6,%s,%s,%s)",row)
		except MySQLdb.Error, e:
			print "employee_rooms.csv: MySQL Error [%d]: %s" % (e.args[0], e.args[1])
	else:
		print "Invalid row! (%s)" % ','.join(row)
		
mydb.commit()
cursor.close()