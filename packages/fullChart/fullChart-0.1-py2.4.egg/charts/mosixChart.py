import sys,os
from pysqlite2 import dbapi2
import pkg_resources
import gdchart2A 
import mosixDataStore

"""
Convert a mosix logfile into a series of charts.

logfile format:

filter lines out of log file:


App structure:
- logParser()			: parse log files
- mosixDataStore()		: query/write data to db
- chartGen()			: generate charts

"""

class MosixChartError(Exception):pass

# configuration params
FILTERLIST = ['USER', 'LOGINS', 'tty', 'pts', 'load average', 'PST']
PREFIX = 'mos'

class chartGen:
	def __init__(self, db):
		self.db = db

	def makeMosixChartBar3D(self, Title, Data, Labels, xTitle, yTitle, chartname):
		"""
		Bar3D
		Data Format
		The .setData() method accepts simple lists of integers or floats. The following would plot a single set of data:
		x.setData([20, 100, 80, 30, 50])
		... and this would plot multiple sets of data:
		x.setData([20, 100, 80, 30, 50], [30, 60, 70, 20, 10], [80, 100, 10, 30, 40])
		"""

		chart = gdchart2A.Bar3D()
		chart.width = 500 
		chart.height = 500
		chart.xtitle = xTitle
		chart.ytitle = yTitle 
		chart.title = Title 
		chart.ext_color = [ "white", "yellow", "red", "blue", "green", "white", "yellow", "red", "blue", "green"]
		chart.setData(Data)
		chart.setLabels(Labels)
		chart.draw(chartname)

		print "Created the following chart: %s" % os.path.basename(chartname)

	def _formatQueryResultToGrapher(self, input,nth):
		"""
	    INPUT [(u'mos1', 0.10000000000000001), (u'mos12', 296.0), (u'mos13', 390.09999999999997), (u'mos14', 98.5), (u'mos16', 8.0), (u'mos17', 87.200000000000003), (u'mos2', 1.0), (u'mos3', 1634.5000000000002), (u'mos4', 96.0), (u'mos7', 98.900000000000006)]
		LABELS ['node', 'sum_cpu']

		"""
			
		"""	
		if len(input)<=0: raise MosixChartError("input empty, nothing to process")
		print input
		return
		retval = []
		count = 0
		keys = []
		#dummy loop
		for item in input:
			keys = item.keys()
			break

		#print keys
		for key in keys:
			newrow=[]
			for row in input:
				newrow.append(row[key])
			#print "NEWROW %s" % newrow
			retval.append(newrow)
			#print retval
		#print retval	
		labels = retval[0:1][0]
		data = retval[1:]
		"""
		data = []
		labels = []
		[data.append(i[1]) for i in input]
		[labels.append(k[0]) for k in input]
		#print 'INPUT %s'  % data
		#print 'LABELS %s' % labels
		return [data], labels 

	def getNode_TotalCPU(self):
		result = self.db._execSql('SELECT d.node, SUM(d.cpu), COUNT(*) FROM mosix_entry d GROUP BY d.node')
		return self._formatQueryResultToGrapher(result, ['node', 'sum_cpu'])

	def getNode_TotalMem(self):
		result = self.db._execSql('SELECT d.node, SUM(d.mem), COUNT(*) FROM mosix_entry d GROUP BY d.node')
		return self._formatQueryResultToGrapher(result, ['node', 'sum_mem'])

	def getNode_TotalCPUsimple(self):
		result = self.db._execSql('SELECT d.node, SUM(d.cpu) FROM mosix_entry d GROUP BY d.node')
		return self._formatQueryResultToGrapher(result, ['node', 'sum_cpu'])


class logParser:
	def __init__(self):
		pass

	def parse(self, db, mosix_log_file):
		db.insertLog(mosix_log_file)
		self.logFilteredDataToDB(db, self._scrapeMosixDump(mosix_log_file))

	def logFilteredDataToDB(self, db, data):
		[db.insertData(row['node'], row['user'], row['cpu'], row['mem']) for row in data]


	def _readMosixDumpFile(self, logfile):
		f = open(logfile, 'r')
		data = f.readlines()
		return data

	def _lineIsInFilterList(self, line, filterlist=FILTERLIST):
		"""
		If one of the filter items is in the filterlist, then
		return True. This means that this line is to be filtered out,
		e.g. removed, scrubbed, deleted, waxed.

		#test cases
		>>> from mosixChart import logParser
		>>> t = logParser()
		>>> t._lineIsInFilterList('tsnhnsth USER')
		True
		>>> t._lineIsInFilterList('tsnhnsth')
		False
		>>> t._lineIsInFilterList('nthnth LOGINS snthnsth')
		True
		>>> t._lineIsInFilterList('nthnth tty snthnsth')
		True
		>>> t._lineIsInFilterList('nthnth pts snthnsth')
		True
		>>> t._lineIsInFilterList('nthnth PST snthnsth')
		True
		>>> t._lineIsInFilterList('nthnth load av snthnsth')
		False
		>>> t._lineIsInFilterList('nthnth load average snthnsth')
		True

		"""
		for filter in filterlist:
			if line.find(filter) != -1 : return True

		return False

	def _parseMosixDump(self, brokenline):
		"""
		Parse the split line. The test cases below show the expected input and output structure:

		#testcases
		>>> from mosixChart import logParser
		>>> t = logParser()
		>>> t._parseMosixDump(['mos13.whozit:paul', '99.2', '1.9', '40968', '42324', '19', '/net/home/paul/bin/PHASE', '-n', '-T', '-p0', '-q0', '-X100', 'phase.inp', 'phase.out'])
		{'node': 'mos13', 'mem': '1.9', 'user': 'whozit:paul', 'cpu': '99.2'}
		>>> t._parseMosixDump(['mos14.whozit:paul', '0.0', '0.0', '384', '3580', '11', 'perl', '/net/home/paul/bin/hapmap_subset_wrapper_phase.pl', 'files', 'resultssummary'])
		{'node': 'mos14', 'mem': '0.0', 'user': 'whozit:paul', 'cpu': '0.0'}
		>>> t._parseMosixDump(['mos14.whozit:paul', '98.5', '3.2', '67920', '69640', '15', '/net/home/paul/bin/PHASE', '-n', '-T', '-p0', '-q0', '-X10', 'phase.inp', 'phase.out'])
		{'node': 'mos14', 'mem': '3.2', 'user': 'whozit:paul', 'cpu': '98.5'}
		>>> t._parseMosixDump(['mos16.whozit:bbuser', '8.0', '0.0', '1176', '2380', '5', '/bin/sh', '/usr/bb/bin/bb-local.sh'])
		{'node': 'mos16', 'mem': '0.0', 'user': 'whozit:bbuser', 'cpu': '8.0'}
		>>> t._parseMosixDump(['mos17.whozit:kitts', '0.0', '0.0', '1104', '2844', '9', 'tcsh', '-c', '/usr/lib/sftp-server'])
		{'node': 'mos17', 'mem': '0.0', 'user': 'whozit:kitts', 'cpu': '0.0'}
		>>> t._parseMosixDump(['mos17.whozit:kitts', '0.0', '0.0', '1112', '2848', '9', 'tcsh', '-c', '/usr/lib/sftp-server'])
		{'node': 'mos17', 'mem': '0.0', 'user': 'whozit:kitts', 'cpu': '0.0'}
		>>> t._parseMosixDump(['mos17.whozit:kitts', '0.0', '0.0', '1192', '3248', '9', '/usr/lib/sftp-server'])
		{'node': 'mos17', 'mem': '0.0', 'user': 'whozit:kitts', 'cpu': '0.0'}
		>>> t._parseMosixDump(['mos17.whozit:kitts', '0.0', '0.0', '1232', '3248', '9', '/usr/lib/sftp-server'])
		{'node': 'mos17', 'mem': '0.0', 'user': 'whozit:kitts', 'cpu': '0.0'}
		
		"""
		brokenline[0] = brokenline[0].replace(',','.')
		nodeuser = brokenline[0].split('.')
		#print brokenline[1:]
		node = nodeuser[0]
		user = nodeuser[1]
		cpu = brokenline[1]
		mem = brokenline[2]
		#print 'node [%s] user [%s] cpu [%s] mem [%s]' %(node,user,cpu,mem)
		d = {}
		d['node']=node
		d['user']=user
		d['cpu']=cpu
		d['mem']=mem
		#print "$$$RESULT:%s" %d
		return d
		
	def _scrapeMosixDump(self, logfile):
		"""
		Parse the mosix logfile:
		a) filter out garbage, like 'USER' and 'LOGINS', etc.
		b) translate the logfile into a form like:
		  node user cpu mem

		See the testcases in _lineIsInFilterList and _parseMosixDump for
		examples of the in/out format.
		"""
		data = self._readMosixDumpFile(logfile)
		retval = []
		for s in data:
			if self._lineIsInFilterList(s) : continue
			a = s.split()
			if a : 
				#print "###PARSE: %s" %a
				retval.append(self._parseMosixDump(a))
		return retval 

def _sortbymachineno(listA, machineprefix):
	"""
	This is the so-called [WWW] Schwartzian Transform, also known as DecorateSortUndecorate (DSU).
	Because we are sorting 'mos[0-9]' such that the item might be mos1 or mos12, we need
	a custom sorter.

	#testcases
	>>> import mosixChart as m
	>>> a = ['mos1', 'mos2', 'mos3', 'mos4', 'mos7', 'mos12', 'mos13', 'mos14', 'mos16', 'mos17']
	>>> a.sort()
	>>> a
	['mos1', 'mos12', 'mos13', 'mos14', 'mos16', 'mos17', 'mos2', 'mos3', 'mos4', 'mos7']
	>>> _sortbymachineno(a, 'mos')
	['mos1', 'mos2', 'mos3', 'mos4', 'mos7', 'mos12', 'mos13', 'mos14', 'mos16', 'mos17']
			   
	"""
	nlist = [(int(x.replace(machineprefix,'')), x) for x in listA]
	nlist.sort()
	return [ val for (key, val) in nlist]

def _sortbymachinenoTwoCol(listA, listB, machineprefix):
	"""
	I beleive this is the so-called [WWW] Schwartzian Transform, also known as DecorateSortUndecorate (DSU).
	Because we are sorting 'mos[0-9]' such that the item might be mos1 or mos12, we need
	a custom sorter.

	#testcases
	>>> import mosixChart as m
	>>> a = ['mos12','mos1', 'mos7']
	>>> b = ['twelve', 'one', 'seven']
	>>> _sortbymachinenoTwoCol(a, b, 'mos')
	(['mos1', 'mos7', 'mos12'], ['one', 'seven', 'twelve'])
			   
	"""
	listAB = zip(listA, listB)
	tupleAB = tuple(listAB)

	#for x in tupleAB:
		#print x, x[0], str(x[0]), str(x[0]).replace('mos', 'MOS')

	nlist = [(int(str(x[0]).replace(machineprefix,'')), x) for x in tupleAB]
	#print nlist
	nlist.sort()
	#print nlist
	sortedMachines = [val for (key, val) in nlist]
	#print sortedMachines
	retListA = [x[0] for x in sortedMachines]
	retListB = [x[1] for x in sortedMachines]
	#print retListA, retListB
	return retListA, retListB

def generateCharts(MOSIX_LOG_FILE, CHARTOUTPUT_DIR, MOSIX_DB_FILE):
	"""
	success case:
	>>> import mosixChart as m
	>>> import pkg_resources as pkg_resources
	>>> MOSIX_LOG_FILE = os.path.join('test', 'mosix-output-logfile.input')
	>>> CHARTOUTPUT_DIR = os.path.join('test', 'charts')
	>>> if not os.path.exists(CHARTOUTPUT_DIR): os.makedirs(CHARTOUTPUT_DIR)
	>>> MOSIX_DB_FILE = os.path.join('test', 'mosixCharts.db')
	>>> if os.path.exists(MOSIX_DB_FILE):os.remove(MOSIX_DB_FILE)
	>>> if not pkg_resources.resource_exists(__name__,MOSIX_LOG_FILE): raise MosixChartError('MOSIX_LOG_FILE does not exist: %s' % MOSIX_LOG_FILE)
	>>> f = open(os.path.join('test', 'temp_input'), 'w')
	>>> f.writelines(pkg_resources.resource_string(__name__,MOSIX_LOG_FILE))
	>>> f.close()
	>>> m.generateCharts(os.path.join('test', 'temp_input'), CHARTOUTPUT_DIR, MOSIX_DB_FILE)
	Created the following chart: mosix-cpu-simple.png
	Created the following chart: mosix-mem.png
	Created the following chart: mosix-cpu.png

	failure case:
	>>> m.generateCharts(os.path.join('test', 'temp_input'), CHARTOUTPUT_DIR, MOSIX_DB_FILE) #doctest: +ELLIPSIS, +NORMALIZE_WHITESPACE
	LOG: Using existing database [...mosixCharts.db]
	Log file already added to database (...mosixCharts.db), skipping processing of: ...temp_input
	Created the following chart: mosix-cpu-simple.png
	Created the following chart: mosix-mem.png
	Created the following chart: mosix-cpu.png

	"""
	#guard
	if not os.path.exists(MOSIX_LOG_FILE):
		raise MosixChartError("File/Path must exist %s"%MOSIX_LOG_FILE)
	if not os.path.exists(CHARTOUTPUT_DIR):
		raise MosixChartError("File/Path must exist %s"%CHARTOUTPUT_DIR)

	#format paths
	MOSIX_LOG_FILE = os.path.abspath(MOSIX_LOG_FILE)
	CHARTOUTPUT_DIR = os.path.abspath(CHARTOUTPUT_DIR)
	MOSIX_DB_FILE = os.path.abspath(MOSIX_DB_FILE)

	# ---------------------------------------------------------------
	# initialize the classes
	# ---------------------------------------------------------------

	db = mosixDataStore.mosixDataStore(MOSIX_DB_FILE)
	parser = logParser()
	try:
		parser.parse(db, MOSIX_LOG_FILE)
	except dbapi2.OperationalError:
		print 'Log file already added to database (%s), skipping processing of: %s'%(MOSIX_DB_FILE, MOSIX_LOG_FILE)

	chart = chartGen(db)
	
	# ---------------------------------------------------------------
	# create the charts
	# ---------------------------------------------------------------
	data, labels = chart.getNode_TotalCPUsimple()
	labels, data  = _sortbymachinenoTwoCol(labels,data[0],PREFIX) 
	#data could be multi-dimensional, so need to pack back into a list, TODO: re-code for this
	data = [data]

	chart.makeMosixChartBar3D(						\
		"Mosix Cluster",						\
		data,								\
		labels,								\
		"Nodes",							\
		"%CPU UTILIZATION (simple)",					\
		'%s/mosix-cpu-simple.png'%CHARTOUTPUT_DIR)	

	data, labels = chart.getNode_TotalMem()
	labels, data  = _sortbymachinenoTwoCol(labels,data[0],PREFIX)
	data = [data]

	chart.makeMosixChartBar3D(						\
		"Mosix Cluster",						\
		data,								\
		labels,								\
		"Nodes",							\
		"%MEM UTILIZATION",			\
		'%s/mosix-mem.png'%CHARTOUTPUT_DIR)	
	
	data, labels = chart.getNode_TotalCPU()
	labels, data  = _sortbymachinenoTwoCol(labels,data[0],PREFIX)
	data = [data]
	chart.makeMosixChartBar3D(						\
		"Mosix Cluster",						\
		data,								\
		labels,								\
		"Nodes",							\
		"%CPU UTILIZATION\n(not normalized by # cpu's",			\
		'%s/mosix-cpu.png'%CHARTOUTPUT_DIR)	

def _test():
	import doctest, mosixChart
	return doctest.testmod(mosixChart)
	
if __name__ == "__main__":
	
	# ---------------------------------------------------------------
	# precess command line
	# ---------------------------------------------------------------
	USAGE = """
	mosixChart [mosix log file] [chart ouput dir] [mosix db file]
	
	defaults:
		[mosix log file] 	: ./mosix.log
		[chart ouput dir] 	: .
		[mosix db file]		: ./mosix.db
	
	This will gen all the currently implemented charts.

	Sample usage:

	python mosixChart.py [mosix log file] [database to use]
	/test$ python ../mosixChart.py ../whozit-output.log . ./AAAAA.db
	
	Created the following chart:
       		file:///home/tgreenwo/data/working/charting/test/mosix-cpu-simple.png
	Created the following chart:
	        file:///home/tgreenwo/data/working/charting/test/mosix-mem.png
	Created the following chart:
	        file:///home/tgreenwo/data/working/charting/test/mosix-cpu.png

	or, to run internal self tests:

	python mosixChart.py -t [-v]

	"""

	l = len(sys.argv)
	#print l, sys.argv
	if l>=2: MOSIX_LOG_FILE = sys.argv[1]
	else: MOSIX_LOG_FILE = './mosix.log'
	if l>=3: CHARTOUTPUT_DIR = sys.argv[2]
	else: CHARTOUTPUT_DIR = '.'
	if l>=4: MOSIX_DB_FILE = sys.argv[3]
	else: MOSIX_DB_FILE = './mosix.db'
	if l < 2 or l >= 5:
		print USAGE
		sys.exit(-1)
	
	#run internal tests instead if specified
	if l>=2 and sys.argv[1]=='-t':
		# do unit tests
		_test()
	else:
		# do it
		generateCharts(MOSIX_LOG_FILE, CHARTOUTPUT_DIR, MOSIX_DB_FILE)
