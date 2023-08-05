import os,sys
from pysqlite2 import dbapi2 as sqlite 
import genTriggers

TESTDIR = './test/'
TESTDB = os.path.join(TESTDIR, 'mosixDataStore.db')
TESTLOG = os.path.join(TESTDIR, 'mosixDataStore.log')

class mosixDataStore:
	"""
	Wrapper for mosixChart db access.
	"""

	def __init__(self, dbname='./mosix.db'):
		"""
		Create the db if it doesn't exist.
		"""

		self.dbname = dbname

		if not os.path.exists(self.dbname):
			self._connectToDatabase()
			self._createNewDatabase()
		else:
			print 'LOG: Using existing database [%s]' %(self.dbname)
			self._connectToDatabase()
		

	def _connectToDatabase(self):
		self.con = sqlite.connect(self.dbname, isolation_level=None)
		self.cur = self.con.cursor()
	
	def _createNewDatabase(self):
		"""
		Exec the sql to create the tables.
		
		Notes:
		-       Wrapper for mosixChart db access. We wrap db access for a couple of reasons, the biggest being
		-       that the wrapper handles the Parent/Child 'id' issue. See relevant bits of code:
		-
		-               * dataStore methods: insertLog and insertData
		-               * create table last_inserted_master (master_id integer);
		-               * insert into last_inserted_master values(NULL);
		-               * create trigger master_id after insert on log
		-               * (SELECT master_id from last_inserted_master)
		-
		-
		-       Note: there are no doctests in either the __init__ or in the _dbInit method that __init__ calls.
		-       This is b/c they are failing for some reason. The logic for what get's executed when broke my
		-       brain. So I moved these tests into _testInit().
		+       Wrapper for mosixChart db access. Nuff said.
		"""

		list_of_mosix_databases = ["""
CREATE TABLE mosixlog(
id INTEGER PRIMARY KEY,
date DEFAULT CURRENT_TIMESTAMP,
md5sum TEXT,
filename TEXT);
""","""
CREATE TABLE mosix_entry (
id INTEGER PRIMARY KEY,
mosixlog_id INTEGER NOT NULL CONSTRAINT fk_mosixlog_id REFERENCES mosixlog(id) ON DELETE CASCADE, --[mosix_entry] 
node TEXT,
user TEXT,
cpu  FLOAT,
mem FLOAT);
""","""
create table last_inserted_master (master_id integer);
""","""
insert into last_inserted_master values(NULL);
""","""
create trigger master_id after insert on mosixlog
        begin
                update last_inserted_master set master_id = last_insert_rowid();
        end;
""","""
create trigger dupe_mosixlog_insert before insert on mosixlog
		for each row begin
			select case
				when((select md5sum from mosixlog where md5sum = NEW.md5sum) IS NOT NULL)
				then raise(ABORT, 'attempting to insert an existing mosixlog (md5sums are the same)')
			end;
		end;	
"""]
		#create mosix_entry base tables
		for table in list_of_mosix_databases:
			#print table
			sql = table
			sqlAndTriggers = "%s%s" %(sql,genTriggers.processConstraints(sql))
			self._execSql(sqlAndTriggers, True)

	def _testInit(self):
		"""	
		>>> import mosixDataStore as t
		>>> #create a test dir
		>>> if not os.path.exists(t.TESTDIR): os.makedirs(t.TESTDIR)
		>>> #remove existing db
		>>> if os.path.exists(t.TESTDB): os.remove(t.TESTDB)
		>>> #remove existing mosixlog
		>>> testDB = t.mosixDataStore(TESTDB)
		>>> testDB._execSql('SELECT * FROM mosix_entry')
		[]
		"""

	def _execSql(self, sql, script=False):
		"""
		expect this to succeed, so don't catch exceptions, let 'em bubble up.
		"""
		f = open(TESTLOG,'a')
		for line in sql.splitlines():
			if len(line)>0:
				if (not line.endswith(';')) and (script==False):line = "%s;"%line	
				f.write('%s\n'%line)
		f.close()
		retval = []
		if script:
			self.cur.executescript(sql)
		else:
			self.cur.execute(sql)
		self.con.commit()
		retval = self.cur.fetchall()
		return retval	
		

	def insertLog(self, mosixlogFile):
		"""
		Bubble the exception up if the mosixlog file has already been processed.

		#testcases
		>>> import mosixDataStore as t
		>>> #create a test dir
		>>> if not os.path.exists(t.TESTDIR): os.makedirs(t.TESTDIR)
		>>> #remove existing db
		>>> if os.path.exists(t.TESTDB): os.remove(t.TESTDB)
		>>> #remove existing mosixlog
		>>> testDB = t.mosixDataStore(TESTDB)
		>>> f = open(os.path.join(TESTDIR, 'foo.tmp'),'w')
		>>> f.write('abc')
		>>> f.close()
		>>> f = open(os.path.join(TESTDIR, 'bar.tmp'),'w')
		>>> f.write('abcdefg')
		>>> f.close()
		>>> testDB.insertLog(os.path.join(TESTDIR, 'foo.tmp'))
		>>> testDB.insertLog(os.path.join(TESTDIR,'bar.tmp'))
		>>> testDB.insertLog(os.path.join(TESTDIR, 'bar.tmp')) #doctest: +ELLIPSIS, +NORMALIZE_WHITESPACE
		Traceback (most recent call last):
		...
		OperationalError: attempting to insert an existing mosixlog (md5sums are the same)
		>>> os.remove(os.path.join(TESTDIR, 'foo.tmp'))
		>>> os.remove(os.path.join(TESTDIR, 'bar.tmp'))
		"""

		import md5
		f = open(mosixlogFile, 'r')
		digest = md5.new('\n'.join(f.readlines())).hexdigest()
		sql = "INSERT into mosixlog (md5sum, filename) values ('%s','%s')" % (digest, f.name)
		self._execSql(sql)	
			


			
	def insertData(self, node, user, cpu, mem):
		"""
		Wrapper handles referencing the mosixlog (id) field.	
		
		#testcases
		>>> import mosixDataStore as t
		>>> import pkg_resources
		>>> pkg_resources.require("genTriggers >= 0.1") #doctest: +ELLIPSIS,+NORMALIZE_WHITESPACE
		[genTriggers ...]
		>>> #create a test dir
		>>> if not os.path.exists(t.TESTDIR): os.makedirs(t.TESTDIR)
		>>> #remove existing db
		>>> if os.path.exists(t.TESTDB): os.remove(t.TESTDB)
		>>> #remove existing mosixlog
		>>> testDB = t.mosixDataStore(TESTDB)
		>>> f = open(os.path.join(TESTDIR, 'foo'),'w')
		>>> f.write('abc')
		>>> f.close()
		>>> testDB.insertLog(os.path.join(TESTDIR, 'foo'))
		>>> testDB._execSql('select * from mosixlog') #doctest: +ELLIPSIS,+NORMALIZE_WHITESPACE
		[(1, ..., u'900150983cd24fb0d6963f7d28e17f72', ...)]
		>>> testDB._execSql('select * from last_inserted_master') #doctest: +ELLIPSIS,+NORMALIZE_WHITESPACE
		[(1,)]
		>>> testDB._execSql('select master_id from last_inserted_master') #doctest: +ELLIPSIS,+NORMALIZE_WHITESPACE
		[(1,)]
		>>> testDB._execSql('select last_insert_rowid()') #doctest: +ELLIPSIS,+NORMALIZE_WHITESPACE
		[(1,)]
		>>> testDB.insertData('abc', 'user', 0.1, 0.2)
		>>> testDB._execSql('SELECT * FROM mosix_entry')
		[(1, 1, u'abc', u'user', 0.10000000000000001, 0.20000000000000001)]
		>>> testDB.insertData('abc', 'user', 0.1, 0.2)
		>>> testDB._execSql('SELECT * FROM mosix_entry')
		[(1, 1, u'abc', u'user', 0.10000000000000001, 0.20000000000000001), (2, 1, u'abc', u'user', 0.10000000000000001, 0.20000000000000001)]
		>>> testDB._execSql('SELECT filename, user, md5sum from mosixlog inner join mosix_entry on mosixlog.id = mosix_entry.mosixlog_id') #doctest: +ELLIPSIS,+NORMALIZE_WHITESPACE
		    [(u'./test/foo', u'user', u'900150983cd24fb0d6963f7d28e17f72'), (u'./test/foo', u'user', u'900150983cd24fb0d6963f7d28e17f72')]
		>>> os.remove(os.path.join(TESTDIR, 'foo'))
		"""

	
		sql = "INSERT into mosix_entry (mosixlog_id, node, user, cpu, mem) VALUES ((SELECT master_id from last_inserted_master), '%s', '%s', %s, %s)" %  (node, user, cpu, mem)
	
		self._execSql(sql)
	
	def _testQueryGroupBy(self):
		"""
		Demonstrates how to use the group by clause in pysqlite.
		
		#testcases
		>>> import mosixDataStore as t
		>>> #create a test dir
		>>> if not os.path.exists(t.TESTDIR): os.makedirs(t.TESTDIR)
		>>> #remove existing db
		>>> if os.path.exists(t.TESTDB): os.remove(t.TESTDB)
		>>> #remove existing mosixlog
		>>> testDB = t.mosixDataStore(TESTDB)
		>>> f = open(os.path.join(TESTDIR, 'foo'),'w')
		>>> f.write('abc')
		>>> f.close()
		>>> testDB.insertLog(os.path.join(TESTDIR,'foo'))
		>>> testDB.insertData('abc', 'user', 0.1, 0.2)
		>>> testDB.insertData('abc', 'user', 0.1, 0.2)
		>>> testDB.insertData('zzz', 'user', .99, 0.99)
		>>> testDB._execSql('SELECT d.node, SUM(d.cpu), COUNT(*) FROM mosix_entry d GROUP BY d.node')
		[(u'abc', 0.20000000000000001, 2), (u'zzz', 0.98999999999999999, 1)]
		>>> os.remove(os.path.join(TESTDIR, 'foo'))
		"""
		pass




def _test():
	import doctest
	return doctest.testmod()

if __name__ == "__main__":
	_test()

