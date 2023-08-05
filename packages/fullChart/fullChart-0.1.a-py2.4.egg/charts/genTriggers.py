import os, sys, traceback, re
from pysqlite2 import dbapi2 as sqlite

TESTDIR = './test/'
TESTLOG = os.path.join(TESTDIR, 'genTriggers.log')

"""
quick and dirty.
give me this format as a single line in your sql, and i'll create the triggers:

	foo_id INTEGER NOT NULL CONSTRAINT fk_foo_id REFERENCES foo(id) ON DELETE CASCADE --[bar]
	childcolname ---------------------[constraintname]----[parenttable (parentcolname)]--[childtable]
	
"""

class GenTriggersError(Exception):pass

class constraint:
	def __init__(self,child_table_name,	  
				child_col_name,	
				child_constraint_name,
				parent_table_name,
				parent_col_name,
				on_delete_cascade):	  	
		self.child_table_name		= child_table_name	
		self.child_col_name			= child_col_name	
		self.child_constraint_name	= child_constraint_name	
		self.parent_table_name 		= parent_table_name 	
		self.parent_col_name		= parent_col_name
		self.on_delete_cascade		= on_delete_cascade
	
	def __repr__(self):
		return "%s %s %s %s %s" %(self.child_table_name,	  
										  self.child_col_name,	
										  self.child_constraint_name,
										  self.parent_table_name,
										  self.parent_col_name)

def _readsql(sqlfile):
	import pkg_resources as pkg_resources
	if not pkg_resources.resource_exists(__name__,sqlfile): raise GenTriggersError('readsql file does not exist: %s' % sqlfile)
	data  = pkg_resources.resource_string(__name__, sqlfile)

	#if not os.path.exists(sqlfile): raise GenTriggersError("Inputfile does not exist : %s" % sqlfile)
	#f = open(sqlfile)
	#strip comments
	retval = []
	for line in data.splitlines():
		if not line.startswith('--'):
			retval.append(line.rstrip())	
	return '\n'.join(retval)
	
	

def _substring(s, l, r):
	"""
	return substring FROM s between l (left) and r (right).
	>>> import genTriggers as g
	>>> g._substring('abc', 'a', 'c')
	'b'
	>>> g._substring('   create table foo (', 'create table', '(')
	'foo'
	>>> g._substring(' XX CREATE tAble AAA	   (', 'create table', '(')
	'aaa'

	"""
	s=s.lower()
	l=l.lower()
	r=r.lower()
	
	lindex = s.find(l) + len(l)
	rindex = s.find(r)
	if lindex < rindex and lindex < len(s) and rindex <= len(s):
		return s[lindex:rindex].lstrip().rstrip()
	raise GenTriggersError('Indexing error: %s, %s, %s' %(s,l,r))

def _stripwhitespace(s):
	"""
	>>> import genTriggers as g
	>>> import re
	>>> print "[%s]" % g._stripwhitespace('the quick  brown fox  ')
	[the quick brown fox]
	>>> print "[%s]" % g._stripwhitespace(' the(quick)  brown  (fox)jumped  ')
	[the(quick) brown (fox)jumped]

	"""
	s2 = re.sub('[\s]\s*', ' ', s)
	s2 = s2.lstrip().rstrip()
	return  s2
	

def processConstraints(sql):
	"""
	import genTriggers as g
	out = g.processConstraints(g._readsql(os.path.join('test', 'genTriggers_testdata.sql')))
	print "[%s]" % _stripwhitespace(out)
	"""
	retval = []
	for line in sql.splitlines():
		retval.append(_genTriggers(line, _filterConstraint(line)))
	return '\n'.join(retval)

def _filterConstraint(sql):
	"""
	>>> import genTriggers as g
	>>> g._filterConstraint('foo_id INTEGER NOT NULL CONSTRAINT fk_foo_id REFERENCES foo(id) ON DELETE CASCADE --[bar]')
	bar foo_id fk_foo_id foo id
		
	"""
	sql = sql.lower()
	
	BEG = '^'
	INT = 'INTEGER NOT NULL'
	CON = 'CONSTRAINT'
	REF = 'REFERENCES'
	OND = 'ON DELETE CASCADE'
	TBL = '--['
	TB2 = ']'

	
	if not (sql.find(INT.lower()) >= 0 and
		sql.find(CON.lower()) >= 0 and
		sql.find(REF.lower()) >= 0 and
		sql.find(TBL.lower()) >= 0 and
		sql.find(TB2.lower()) >=0): return
	class temp:
		pass
	c = temp()
	if sql.find(OND.lower()) > 0: c.on_delete_cascade = True
	else: c.on_delete_cascade = False
	#we have a foreign key constraint
	c.child_table_name		= _substring(sql, TBL, TB2)
	c.child_col_name		= _substring(sql, BEG,INT)
	c.child_constraint_name		= _substring(sql, CON, REF)
	c.parent_table_name 		= _substring(sql, REF, '(')
	c.parent_col_name		= _substring(sql, '(', ')')
	const = constraint(c.child_table_name,
						   c.child_col_name,	
						   c.child_constraint_name,
						   c.parent_table_name,
						   c.parent_col_name,
			   c.on_delete_cascade)	


	return const

def _genTriggers(sql, c):
	"""
	>>> #TestCase: ON DELETE CASCADE
	>>> import genTriggers as g
	>>> testsql = "foo_id INTEGER NOT NULL CONSTRAINT fk_foo_id REFERENCES foo(id) ON DELETE CASCADE --[bar]"
	>>> out=''
	>>> out = g._genTriggers(testsql, constraint('childtable', 'childcol', 'childcon', 'parenttable', 'parentcol',True))
	>>> print "[%s]" % out #doctest:+NORMALIZE_WHITESPACE
	[
	CREATE TRIGGER fki_childtable_childcol
		BEFORE INSERT ON childtable
		FOR EACH ROW BEGIN 
		  SELECT CASE
			 WHEN ((SELECT parentcol FROM parenttable WHERE parentcol = NEW.childcol) IS NULL)
			 THEN RAISE(ABORT, 'INSERT on table "childtable" violates foreign key constraint "childcon"')
		  END;
		END;
	<BLANKLINE>
		CREATE TRIGGER fku_childtable_parenttable_childcol
		BEFORE UPDATE ON childtable
		FOR EACH ROW BEGIN 
		   SELECT CASE
			 WHEN ((SELECT parentcol FROM parenttable WHERE parentcol = new.childcol) IS NULL)
			 THEN RAISE(ABORT, 'update on table "childtable" violates foreign key constraint "childcon"')
		  END;
		END;
	<BLANKLINE>
		CREATE TRIGGER fku_parenttable_childtable_parentcol
		BEFORE UPDATE ON parenttable
		FOR EACH ROW BEGIN 
		   SELECT CASE
			 WHEN ((SELECT childcol FROM childtable WHERE childcol = new.parentcol) IS NULL)
			 THEN RAISE(ABORT, 'update on table "parenttable" violates foreign key constraint "childcon"')
		  END;
		END;
	<BLANKLINE>
		CREATE TRIGGER fkdCascade_parentcol_childtable_parentcol
		BEFORE DELETE ON parenttable
		FOR EACH ROW BEGIN 
			DELETE FROM childtable WHERE childcol = OLD.parentcol;
		END;
	]

	>>> #TestCase: No ON DELETE CASCADE
	>>> testsql = "foo_id INTEGER NOT NULL CONSTRAINT fk_foo_id REFERENCES foo(id) --[bar]"
	>>> out=''
	>>> print g._genTriggers(testsql, constraint('childtable', 'childcol', 'childcon', 'parenttable', 'parentcol', False)) #doctest:+IGNORE_EXCEPTION_DETAIL,+NORMALIZE_WHITESPACE,+ELLIPSIS
		CREATE TRIGGER fki_childtable_childcol
		BEFORE INSERT ON childtable
		FOR EACH ROW BEGIN
		  SELECT CASE
				 WHEN ((SELECT parentcol FROM parenttable WHERE parentcol = NEW.childcol) IS NULL)
				 THEN RAISE(ABORT, 'INSERT on table "childtable" violates foreign key constraint "childcon"')
		  END;
		END;
		CREATE TRIGGER fku_childtable_parenttable_childcol
		BEFORE UPDATE ON childtable
		FOR EACH ROW BEGIN
		   SELECT CASE
				 WHEN ((SELECT parentcol FROM parenttable WHERE parentcol = new.childcol) IS NULL)
				 THEN RAISE(ABORT, 'update on table "childtable" violates foreign key constraint "childcon"')
		  END;
		END;
		CREATE TRIGGER fku_parenttable_childtable_parentcol
		BEFORE UPDATE ON parenttable
		FOR EACH ROW BEGIN
		   SELECT CASE
				 WHEN ((SELECT childcol FROM childtable WHERE childcol = new.parentcol) IS NULL)
				 THEN RAISE(ABORT, 'update on table "parenttable" violates foreign key constraint "childcon"')
		  END;
		END;
		CREATE TRIGGER fkd_parenttable_childtable_parentcol
		BEFORE DELETE ON parenttable
		FOR EACH ROW BEGIN
		  SELECT CASE
				WHEN ((SELECT childcol FROM childtable WHERE childcol = OLD.parentcol) IS NOT NULL)
				THEN RAISE(ABORT, 'DELETE on table "parenttable" violates foreign key constraint "childcon"')
		  END;
		END;


	"""
	#guard
	if not c: return ''
	
	retval = []
	retval.append(_genInsertTrigger(c))
	retval.append(_genUpdateChildTrigger(c))
	retval.append(_genUpdateParentTrigger(c))
	#either this or the cascade DELETE trigger should be used, but not both
	if c.on_delete_cascade == True: retval.append(_genCascadeDeleteTrigger(c))
	else:retval.append(_genDeleteTrigger(c)) 
	
	return '\n'.join(retval)
	
def _genericReplace(sql, c):
	sql = sql.replace('[CHILD_TABLE_NAME]', c.child_table_name)
	sql = sql.replace('[PARENT_COL_NAME]',c.parent_col_name)
	sql = sql.replace('[PARENT_TABLE_NAME]', c.parent_table_name)
	sql = sql.replace('[CHILD_CONSTRAINT_NAME]', c.child_constraint_name)
	sql = sql.replace('[CHILD_COL_NAME]', c.child_col_name)
	return sql

def _genInsertTrigger(c):
	"""
	>>> import genTriggers as g
	>>> out = g._genInsertTrigger(constraint('childtable', 'childcol', 'childcon', 'parenttable', 'parentcol', True))
	>>> print "[%s]" % out #doctest:+NORMALIZE_WHITESPACE
	[
		CREATE TRIGGER fki_childtable_childcol
		BEFORE INSERT ON childtable
		FOR EACH ROW BEGIN 
		  SELECT CASE
			 WHEN ((SELECT parentcol FROM parenttable WHERE parentcol = NEW.childcol) IS NULL)
			 THEN RAISE(ABORT, 'INSERT on table "childtable" violates foreign key constraint "childcon"')
		  END;
		END;
		]


	"""
	sql = """
	CREATE TRIGGER fki_[CHILD_TABLE_NAME]_[CHILD_COL_NAME]
	BEFORE INSERT ON [CHILD_TABLE_NAME]
	FOR EACH ROW BEGIN 
	  SELECT CASE
		 WHEN ((SELECT [PARENT_COL_NAME] FROM [PARENT_TABLE_NAME] WHERE [PARENT_COL_NAME] = NEW.[CHILD_COL_NAME]) IS NULL)
		 THEN RAISE(ABORT, 'INSERT on table "[CHILD_TABLE_NAME]" violates foreign key constraint "[CHILD_CONSTRAINT_NAME]"')
	  END;
	END;
	"""
	return _genericReplace(sql,c)


def _genUpdateParentTrigger(c):
	"""
	>>> import genTriggers as g
	>>> out = g._genUpdateParentTrigger(constraint('childtable', 'childcol', 'childcon', 'parenttable', 'parentcol', True))
	>>> print "[%s]" % out #doctest:+NORMALIZE_WHITESPACE
	[
		CREATE TRIGGER fku_parenttable_childtable_parentcol
		BEFORE UPDATE ON parenttable
		FOR EACH ROW BEGIN 
		   SELECT CASE
			 WHEN ((SELECT childcol FROM childtable WHERE childcol = new.parentcol) IS NULL)
			 THEN RAISE(ABORT, 'update on table "parenttable" violates foreign key constraint "childcon"')
		  END;
		END;
		]


	"""
	
	sql = """
	CREATE TRIGGER fku_[PARENT_TABLE_NAME]_[CHILD_TABLE_NAME]_[PARENT_COL_NAME]
	BEFORE UPDATE ON [PARENT_TABLE_NAME]
	FOR EACH ROW BEGIN 
	   SELECT CASE
		 WHEN ((SELECT [CHILD_COL_NAME] FROM [CHILD_TABLE_NAME] WHERE [CHILD_COL_NAME] = new.[PARENT_COL_NAME]) IS NULL)
		 THEN RAISE(ABORT, 'update on table "[PARENT_TABLE_NAME]" violates foreign key constraint "[CHILD_CONSTRAINT_NAME]"')
	  END;
	END;
	"""
	return _genericReplace(sql,c)
	
def _genUpdateChildTrigger(c):
	"""
	>>> import genTriggers as g
	>>> out = g._genUpdateChildTrigger(constraint('childtable', 'childcol', 'childcon', 'parenttable', 'parentcol', True))
	>>> print "[%s]" % out #doctest:+NORMALIZE_WHITESPACE
	[
		CREATE TRIGGER fku_childtable_parenttable_childcol
		BEFORE UPDATE ON childtable
		FOR EACH ROW BEGIN 
		   SELECT CASE
			 WHEN ((SELECT parentcol FROM parenttable WHERE parentcol = new.childcol) IS NULL)
			 THEN RAISE(ABORT, 'update on table "childtable" violates foreign key constraint "childcon"')
		  END;
		END;
		]


	"""
	
	sql = """
	CREATE TRIGGER fku_[CHILD_TABLE_NAME]_[PARENT_TABLE_NAME]_[CHILD_COL_NAME]
	BEFORE UPDATE ON [CHILD_TABLE_NAME]
	FOR EACH ROW BEGIN 
	   SELECT CASE
		 WHEN ((SELECT [PARENT_COL_NAME] FROM [PARENT_TABLE_NAME] WHERE [PARENT_COL_NAME] = new.[CHILD_COL_NAME]) IS NULL)
		 THEN RAISE(ABORT, 'update on table "[CHILD_TABLE_NAME]" violates foreign key constraint "[CHILD_CONSTRAINT_NAME]"')
	  END;
	END;
	"""
	return _genericReplace(sql,c)

def _genDeleteTrigger(c):
	"""
	>>> import genTriggers as g
	>>> out = g._genDeleteTrigger(constraint('childtable', 'childcol', 'childcon', 'parenttable', 'parentcol', True))
	>>> print "[%s]" % out #doctest:+NORMALIZE_WHITESPACE
	[
		CREATE TRIGGER fkd_parenttable_childtable_parentcol
		BEFORE DELETE ON parenttable
		FOR EACH ROW BEGIN 
		  SELECT CASE
			WHEN ((SELECT childcol FROM childtable WHERE childcol = OLD.parentcol) IS NOT NULL)
			THEN RAISE(ABORT, 'DELETE on table "parenttable" violates foreign key constraint "childcon"')
		  END;
		END;
		]

	
	"""
	
	sql = """
	CREATE TRIGGER fkd_[PARENT_TABLE_NAME]_[CHILD_TABLE_NAME]_[PARENT_COL_NAME]
	BEFORE DELETE ON [PARENT_TABLE_NAME]
	FOR EACH ROW BEGIN 
	  SELECT CASE
		WHEN ((SELECT [CHILD_COL_NAME] FROM [CHILD_TABLE_NAME] WHERE [CHILD_COL_NAME] = OLD.[PARENT_COL_NAME]) IS NOT NULL)
		THEN RAISE(ABORT, 'DELETE on table "[PARENT_TABLE_NAME]" violates foreign key constraint "[CHILD_CONSTRAINT_NAME]"')
	  END;
	END;
	"""
	return _genericReplace(sql,c)

def _genCascadeDeleteTrigger(c):
	"""
	>>> import genTriggers as g
	>>> out = g._genCascadeDeleteTrigger(constraint('childtable', 'childcol', 'childcon', 'parenttable', 'parentcol',True))
	>>> print "[%s]" % out #doctest:+NORMALIZE_WHITESPACE
	[
		CREATE TRIGGER fkdCascade_parentcol_childtable_parentcol
		BEFORE DELETE ON parenttable
		FOR EACH ROW BEGIN 
			DELETE FROM childtable WHERE childcol = OLD.parentcol;
		END;
		]


	"""

	sql = """
	CREATE TRIGGER fkdCascade_[PARENT_COL_NAME]_[CHILD_TABLE_NAME]_[PARENT_COL_NAME]
	BEFORE DELETE ON [PARENT_TABLE_NAME]
	FOR EACH ROW BEGIN 
		DELETE FROM [CHILD_TABLE_NAME] WHERE [CHILD_COL_NAME] = OLD.[PARENT_COL_NAME];
	END;
	"""
	return _genericReplace(sql,c)

def _fileToText(f):
	import pkg_resources as pkg_resources
	if not pkg_resources.resource_exists(__name__,f): raise GenTriggersError('fileToText file does not exist: %s' % f)
	return pkg_resources.resource_string(__name__, f)
	
def _testStandardTwoTableSql():
	"""
	#-------------------------------------------------
	# TESTS
	#-------------------------------------------------
	a) create testtriggers.db FROM genTriggers_testdataComplex.sql
	b) process constraints in genTriggers_testdata.sql
	c) verify results of constraints processing
	#-------------------------------------------------
	# SETUP
	#-------------------------------------------------
	>>> import genTriggers as g
	>>> testdata = os.path.join('test', 'genTriggers_testdataComplex.sql')
	>>> print g._readsql(testdata) #doctest: +NORMALIZE_WHITESPACE
	CREATE TABLE log(
	id INTEGER PRIMARY KEY,
	date DEFAULT CURRENT_TIMESTAMP,
	md5sum TEXT);
	<BLANKLINE>
	CREATE TABLE data (
	id INTEGER PRIMARY KEY,
	log_id INTEGER NOT NULL CONSTRAINT fk_log_id REFERENCES log(id) ON DELETE CASCADE, --[data]
	node TEXT,
	username TEXT,
	cpu  FLOAT,
	mem FLOAT);
	<BLANKLINE>
	create table last_inserted_master (master_id integer);
	insert into last_inserted_master values(NULL);
	<BLANKLINE>
	create trigger master_id after insert on log
		begin
				update last_inserted_master set master_id = last_insert_rowid();
		end;

	>>> print g.processConstraints(g._readsql(testdata))  #doctest: +NORMALIZE_WHITESPACE
	CREATE TRIGGER fki_data_log_id
		BEFORE INSERT ON data
		FOR EACH ROW BEGIN
		  SELECT CASE
				 WHEN ((SELECT id FROM log WHERE id = NEW.log_id) IS NULL)
				 THEN RAISE(ABORT, 'INSERT on table "data" violates foreign key constraint "fk_log_id"')
		  END;
		END;
	<BLANKLINE>
		CREATE TRIGGER fku_data_log_log_id
		BEFORE UPDATE ON data
		FOR EACH ROW BEGIN
		   SELECT CASE
				 WHEN ((SELECT id FROM log WHERE id = new.log_id) IS NULL)
				 THEN RAISE(ABORT, 'update on table "data" violates foreign key constraint "fk_log_id"')
		  END;
		END;
	<BLANKLINE>
		CREATE TRIGGER fku_log_data_id
		BEFORE UPDATE ON log
		FOR EACH ROW BEGIN
		   SELECT CASE
				 WHEN ((SELECT log_id FROM data WHERE log_id = new.id) IS NULL)
				 THEN RAISE(ABORT, 'update on table "log" violates foreign key constraint "fk_log_id"')
		  END;
		END;
	<BLANKLINE>
		CREATE TRIGGER fkdCascade_id_data_id
		BEFORE DELETE ON log
		FOR EACH ROW BEGIN
				DELETE FROM data WHERE log_id = OLD.id;
		END;

	"""
def _testDBInsertWithCASCADEDELETE():
	"""
	#-------------------------------------------------
	# TESTS
	#-------------------------------------------------
	a) create testtriggers.db FROM genTriggers_testdata.sql
	b) process constraints in genTriggers_testdata.sql
	c) apply constraints to genTriggers_testdata.sql
	d) run some inserts/updates/deletes that suceed, some that fail
	e) try a cascading DELETE (success/fail cases)
	#-------------------------------------------------
	# SETUP
	#-------------------------------------------------
	>>> import genTriggers as g
	>>> testdata = os.path.join('test', 'genTriggers_testdata.sql')
	>>> testdb = './test/testtriggers.db.temp'
	>>> if not os.path.exists(TESTDIR):os.makedirs(TESTDIR)
	>>> if os.path.exists(testdb):os.remove(testdb)
	>>> g._execSql(testdb, g._readsql(testdata),True)
	[]
	>>> g._execSql(testdb, g.processConstraints(g._readsql(testdata)),True) 
	[]
	
	-------------------------------------------------
	# INIT DB
	#-------------------------------------------------
	>>> print _execSql(testdb, 'INSERT INTO foo(id) values (1)' )
	[]
	>>> print _execSql(testdb, 'SELECT * FROM foo')
	[(1,)]
	>>> print _execSql(testdb, 'INSERT INTO bar(id, foo_id) values (1,1)')
	[]
	>>> print _execSql(testdb, 'SELECT * FROM foo, bar')
	[(1, 1, 1)]

	#-------------------------------------------------
	# INSERTS THAT BREAK FK INTEGRITY 
	#-------------------------------------------------
	
	# 1) Insert INTO child WHERE parent key does not exist
	
	>>> print _execSql(testdb, 'INSERT INTO bar(id, foo_id) values (1,2)')
	Traceback (most recent call last):
	...
	OperationalError: INSERT on table "bar" violates foreign key constraint "fk_foo_id"
	
	>>> print _execSql(testdb, 'SELECT * FROM foo, bar WHERE bar.foo_id = foo.id')
	[(1, 1, 1)]
	
	# 2) Update parent row pkid to WHERE parent pkid does not exist in child table
	
	>>> print _execSql(testdb, 'update foo set id=100 WHERE id=1')
	Traceback (most recent call last):
	...
	OperationalError: update on table "foo" violates foreign key constraint "fk_foo_id"


	# 3) Update child fkid to a pkid in parent that does not exist
	
	>>> print _execSql(testdb, 'update bar set foo_id=111 WHERE id=1')
	Traceback (most recent call last):
	...
	OperationalError: update on table "bar" violates foreign key constraint "fk_foo_id"

	#-------------------------------------------------
	# VERIFY CASCADE DELETE 
	#-------------------------------------------------
	
	# 4) Insert some more data
	
	>>> _execSql(testdb, 'INSERT INTO foo(id) values (2)' )
	[]
	>>> _execSql(testdb, 'SELECT * FROM foo' )
	[(1,), (2,)]
	>>> _execSql(testdb, 'INSERT INTO bar(id, foo_id) values (10,1)')
	[]
	>>> _execSql(testdb, 'INSERT INTO bar(id, foo_id) values (11,1)')
	[]
	>>> _execSql(testdb, 'INSERT INTO bar(id, foo_id) values (12,1)')
	[]
	>>> _execSql(testdb, 'INSERT INTO bar(id, foo_id) values (20,2)')
	[]
	>>> _execSql(testdb, 'INSERT INTO bar(id, foo_id) values (30,2)')
	[]
	>>> _execSql(testdb, 'INSERT INTO bar(id, foo_id) values (40,2)')
	[]
	>>> print _execSql(testdb, 'SELECT foo.id, bar.id FROM foo, bar WHERE (foo.id = bar.foo_id)')
	[(1, 1), (1, 10), (1, 11), (1, 12), (2, 20), (2, 30), (2, 40)]

	# 5) Perform a cascading delete
	
	>>> _execSql(testdb, 'DELETE FROM foo WHERE id = 1')
	[]

	# 6) Verify cascading DELETE was performed
	
	>>> print _execSql(testdb, 'SELECT bar.id, bar.foo_id FROM bar')
	[(20, 2), (30, 2), (40, 2)]
	>>> print _execSql(testdb, 'SELECT * FROM foo')
	[(2,)]

	#-------------------------------------------------
	# VERIFY INTEGRITY CONSTRAINT DOESNT REMEMBER PREV PKID 
	#-------------------------------------------------
	
	# 7) Insert INTO bar with deleted pkids
	
	>>> _execSql(testdb, 'INSERT INTO bar(id, foo_id) values (10,1)') #doctest:+IGNORE_EXCEPTION_DETAIL,+NORMALIZE_WHITESPACE,+ELLIPSIS
	Traceback (most recent call last):
	...
	OperationalError: INSERT on table "bar" violates foreign key constraint "fk_foo_id"

	>>> if os.path.exists(testdb):os.remove(testdb)
	"""
	

def _testDBInsertNO_CASCADEDELETE():
	"""
	#-------------------------------------------------
	# TESTS
	#-------------------------------------------------
	a) create testtriggers.db FROM testdata.sql
	b) process constraints in testdata.sql
	c) apply constraints to testdata.sql
	d) run some inserts/updates/deletes that suceed, some that fail
	e) try a cascading DELETE (success/fail cases)
	#-------------------------------------------------
	# SETUP
	#-------------------------------------------------
	>>> import genTriggers as g
	>>> testdata = os.path.join('test', 'genTriggers_testdataNOCASCADE.sql')
	>>> testdb = os.path.join('test', 'genTriggers_testtriggersNOCASCADE.db')
	>>> if not os.path.exists(TESTDIR):os.makedirs(TESTDIR)
	>>> if os.path.exists(testdb):os.remove(testdb)
	>>> g._execSql(testdb, g._fileToText(testdata),True)
	[]
	>>> g._execSql(testdb, g.processConstraints(g._readsql(testdata)),True)
	[]
	>>> print g.processConstraints(g._readsql(testdata)) #doctest:+IGNORE_EXCEPTION_DETAIL,+NORMALIZE_WHITESPACE,+ELLIPSIS
		CREATE TRIGGER fki_bar_foo_id
		BEFORE INSERT ON bar
		FOR EACH ROW BEGIN
		  SELECT CASE
				 WHEN ((SELECT id FROM foo WHERE id = NEW.foo_id) IS NULL)
				 THEN RAISE(ABORT, 'INSERT on table "bar" violates foreign key constraint "fk_foo_id"')
		  END;
		END;
		CREATE TRIGGER fku_bar_foo_foo_id
		BEFORE UPDATE ON bar
		FOR EACH ROW BEGIN
		   SELECT CASE
				 WHEN ((SELECT id FROM foo WHERE id = new.foo_id) IS NULL)
				 THEN RAISE(ABORT, 'update on table "bar" violates foreign key constraint "fk_foo_id"')
		  END;
		END;
		CREATE TRIGGER fku_foo_bar_id
		BEFORE UPDATE ON foo
		FOR EACH ROW BEGIN
		   SELECT CASE
				 WHEN ((SELECT foo_id FROM bar WHERE foo_id = new.id) IS NULL)
				 THEN RAISE(ABORT, 'update on table "foo" violates foreign key constraint "fk_foo_id"')
		  END;
		END;
		CREATE TRIGGER fkd_foo_bar_id
		BEFORE DELETE ON foo
		FOR EACH ROW BEGIN
		  SELECT CASE
				WHEN ((SELECT foo_id FROM bar WHERE foo_id = OLD.id) IS NOT NULL)
				THEN RAISE(ABORT, 'DELETE on table "foo" violates foreign key constraint "fk_foo_id"')
		  END;
		END;

	#-------------------------------------------------
	# INIT DB
	#-------------------------------------------------
	>>> print _execSql(testdb, 'INSERT INTO foo(id) values (1)' )
	[]
	>>> print _execSql(testdb, 'SELECT * FROM foo')
	[(1,)]
	>>> print _execSql(testdb, 'INSERT INTO bar(id, foo_id) values (1,1)')
	[]
	>>> print _execSql(testdb, 'SELECT * FROM foo, bar')
	[(1, 1, 1)]

	#-------------------------------------------------
	# INSERTS THAT BREAK FK INTEGRITY 
	#-------------------------------------------------
	
	# 1) Insert INTO child WHERE parent key does not exist
	
	>>> print _execSql(testdb, 'INSERT INTO bar(id, foo_id) values (1,2)') #doctest:+IGNORE_EXCEPTION_DETAIL,+NORMALIZE_WHITESPACE,+ELLIPSIS
	Traceback (most recent call last):
	...
	OperationalError: INSERT on table "bar" violates foreign key constraint "fk_foo_id"
	
	>>> print _execSql(testdb, 'SELECT * FROM foo, bar WHERE bar.foo_id = foo.id')
	[(1, 1, 1)]
	
	# 2) Update parent row pkid to WHERE parent pkid does not exist in child table
	
	>>> print _execSql(testdb, 'update foo set id=100 WHERE id=1') #doctest:+IGNORE_EXCEPTION_DETAIL,+NORMALIZE_WHITESPACE,+ELLIPSIS
	Traceback (most recent call last): 
	...
	OperationalError: update on table "foo" violates foreign key constraint "fk_foo_id"

	# 3) Update child fkid to a pkid in parent that does not exist
	
	>>> print _execSql(testdb, 'update bar set foo_id=111 WHERE id=1')#doctest:+IGNORE_EXCEPTION_DETAIL,+NORMALIZE_WHITESPACE,+ELLIPSIS
	Traceback (most recent call last): 
	...
	OperationalError: update on table "bar" violates foreign key constraint "fk_foo_id"


	#-------------------------------------------------
	# VERIFY CASCADE DELETE NOT PRESENT
	#-------------------------------------------------
	
	# 4) Insert some more data
	
	>>> _execSql(testdb, 'INSERT INTO foo(id) values (2)' )
	[]
	>>> _execSql(testdb, 'INSERT INTO bar(id, foo_id) values (10,1)')
	[]
	>>> _execSql(testdb, 'INSERT INTO bar(id, foo_id) values (11,1)')
	[]
	>>> _execSql(testdb, 'INSERT INTO bar(id, foo_id) values (12,1)')
	[]
	>>> _execSql(testdb, 'INSERT INTO bar(id, foo_id) values (20,2)')
	[]
	>>> _execSql(testdb, 'INSERT INTO bar(id, foo_id) values (30,2)')
	[]
	>>> _execSql(testdb, 'INSERT INTO bar(id, foo_id) values (40,2)')
	[]
	>>> print _execSql(testdb, 'SELECT foo.id, bar.id FROM foo, bar WHERE (foo.id = bar.foo_id)')
	[(1, 1), (1, 10), (1, 11), (1, 12), (2, 20), (2, 30), (2, 40)]

	# 5) Try a cascading delete, expect constraint error
	
	>>> _execSql(testdb, 'DELETE FROM foo WHERE id = 1') #doctest:+IGNORE_EXCEPTION_DETAIL,+NORMALIZE_WHITESPACE,+ELLIPSIS
	Traceback (most recent call last):
	...
	OperationalError: DELETE on table "foo" violates foreign key constraint "fk_foo_id"


	# 6) Verify cascading DELETE was not performed
	
	>>> print _execSql(testdb, 'SELECT foo.id, bar.id FROM foo, bar WHERE (foo.id = bar.foo_id)')
	[(1, 1), (1, 10), (1, 11), (1, 12), (2, 20), (2, 30), (2, 40)]
	
	>>> if os.path.exists(testdb):os.remove(testdb)
	"""

def _testMultipleTablesWithRefIntegrity():
	"""
	#-------------------------------------------------
	# TESTS
	#-------------------------------------------------
	a) create testtriggers.db FROM genTriggers_testdata.sql
	b) process constraints in genTriggers_testdata.sql
	c) apply constraints to genTriggers_testdata.sql
	d) run some inserts/updates/deletes that suceed, some that fail
	e) try a cascading DELETE (success/fail cases)
	#-------------------------------------------------
	# SETUP
	#-------------------------------------------------
	>>> import genTriggers as g
	>>> testdata = os.path.join('test', 'genTriggers_testdataComplex.sql')
	>>> testdb = os.path.join('test', 'genTriggers_testtriggersComplex.db')
	>>> if not os.path.exists(TESTDIR):os.makedirs(TESTDIR)
	>>> if os.path.exists(testdb):os.remove(testdb)
	>>> if os.path.exists(TESTLOG):os.remove(TESTLOG)
	>>> g._execSql(testdb, g._fileToText(testdata),True)
	[]
	
	#>>> g._execSql(testdb, g.processConstraints(g._readsql(testdata)),True)
	#[]
	#
	#-------------------------------------------------
	# Verify tables were created
	#-------------------------------------------------
	>>> print _execSql(testdb, 'SELECT * FROM log')
	[]
	>>> print _execSql(testdb, 'SELECT * FROM data')
	[]
	>>> print _execSql(testdb, "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
	[(u'data',), (u'last_inserted_master',), (u'log',)]
	
	#-------------------------------------------------
	# Insert linked data via 'last_insert_rowid()' 
	#-------------------------------------------------
	>>> _execSql(testdb, "INSERT INTO log(date, md5sum) values ('fakedate', 'abc')" )
	[]
	>>> _execSql(testdb, "SELECT * FROM log") #docutils: +ELLIPSIS, +NORMALIZE_WHITESPACE
	[(1, u'fakedate', u'abc')]
	
	#>>> _execSql(testdb, "SELECT * FROM log WHERE log.id = (last_insert_rowid())")
	#[(1, u'fakedate', u'abc')]
	>>> _execSql(testdb, "INSERT INTO data(log_id, node, username, cpu, mem) values ((SELECT last_insert_rowid()), 'node', 'username', 100.00, 50.00)")
	[]
	>>> _execSql(testdb, "SELECT * FROM data")
	[(1, 0, u'node', u'username', 100.0, 50.0)]
	
	#-------------------------------------------------
	# Insert linked more data via 'last_insert_rowid()' 
	#-------------------------------------------------
	>>> _execSql(testdb, "INSERT INTO log(date, md5sum) values ('fakedate', 'abc100')" )
	[]
	>>> _execSql(testdb, "INSERT INTO data(log_id, node, username, cpu, mem) values ((SELECT last_insert_rowid()), 'node100', 'username100', 100.00, 50.00)")
	[]
	>>> _execSql(testdb, "SELECT * FROM log WHERE md5sum == 'abc100'")
	[(2, u'fakedate', u'abc100')]
	>>> _execSql(testdb, "DELETE FROM log WHERE md5sum == 'abc100'")
	[]
	>>> _execSql(testdb, "SELECT * FROM log WHERE md5sum == 'abc100'")
	[]

	#-------------------------------------------------
	# Insert multiple child records for a given parent 
	#-------------------------------------------------
	>>> _execSql(testdb, "INSERT INTO log(date, md5sum) values ('fakedate', 'abc2000')" )
	[]
	>>> _execSql(testdb, "INSERT INTO data(log_id, node, username, cpu, mem) values ((SELECT master_id from last_inserted_master), 'node100', 'username100', 100.00, 50.00)")
	[]
	>>> _execSql(testdb, "INSERT INTO data(log_id, node, username, cpu, mem) values ((SELECT master_id from last_inserted_master), 'node100', 'username100', 100.00, 50.00)")
	[]
	>>> _execSql(testdb, "SELECT * FROM log,data WHERE md5sum == 'abc2000'") #docutils: +NORMALIZE_WHITESPACE
	[(2, u'fakedate', u'abc2000', 1, 0, u'node', u'username', 100.0, 50.0), (2, u'fakedate', u'abc2000', 2, 0, u'node100', u'username100', 100.0, 50.0), (2, u'fakedate', u'abc2000', 3, 2, u'node100', u'username100', 100.0, 50.0), (2, u'fakedate', u'abc2000', 4, 2, u'node100', u'username100', 100.0, 50.0)]

	>>> if os.path.exists(testdb):os.remove(testdb)
	"""



def _execSql(db, sql,script=False):
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
	con = sqlite.connect(db, isolation_level=None)
	cur = con.cursor()
	if script:
		cur.executescript(sql)
	else:
		cur.execute(sql)
	retval = cur.fetchall()
	con.commit()
	con.close()
	
	return retval	

	
def _test():
	import doctest
	return doctest.testmod()

if __name__ == "__main__":
	useage = """
	USEAGE (python 2.4): 
	
	python genTriggers.py [sql input file] > [trigger output file]
	
	To run doctest test suite, use the '-t' option:
	python genTriggers.py -t 

	Same, but verbose:
	python genTriggers.py -t -v

	try:
		if sys.argv[1] == '-t':
			_test()
		else:
			print processConstraints(_readsql(sys.argv[1]))
		
	except:	
		print sys.argv
		print useage
	"""
	
	
	if sys.argv[1] == '-t':
		_test()
	else:
		print processConstraints(_readsql(sys.argv[1]))

