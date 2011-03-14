import logging
from handler import PickleHttpHandler
import os
from nose.tools import eq_, ok_,assert_not_equals,assert_true

svc_path = os.path.join(os.path.dirname(__file__), 'httpservice.conf')

logs = ["file%i.log"%x for x in range(1,7) ]

def getLoger(file_name):
	log = logging.getLogger(file_name)
	log.setLevel( logging.DEBUG )
	log.addHandler( PickleHttpHandler( 'localhost:8000', 'log', method = 'POST' ) )
	return log

def getLogRecCount(filename):
	f = open(filename,"r")
	lines = 0
	for l in f:
		lines += 1
	f.close()
	return lines

def wait_log_recors(logfile, num_recs, timeout):
	import time
	for i in range(0,timeout+1):
		if getLogRecCount(logfile) == num_recs:
			break
		time.sleep(1)
	return i

def del_files(wild):
	from win32api import DeleteFile, FindFiles
	files = FindFiles(wild)
	for f in files:
		print "deleting " + f[8]
		DeleteFile(f[8])

def update_config():
	config_str = logs[0]
	for f in logs[1:]:
		config_str += ","  + f
	import ini
	ini.set(svc_path,"default", "lognames" ,config_str)
	ini.set(svc_path,"default", "rotation_bytes", 3000 )
	
def backup_config():
	from distutils import file_util
	file_util.copy_file("httpservice.conf", "httpservice.bak")

def setup():
	from server import HTTPLogServiceHelper
	server = HTTPLogServiceHelper()
	server.Stop()
	import time
	time.sleep(1)
	backup_config()
	del_files("*.log")
	del_files("*.1")
	update_config()
	server.Start()
	
def teardown():
	from distutils import file_util
	file_util.copy_file("httpservice.bak","httpservice.conf")
	
def testThreeLogFiles():
	work_cl = [ getLoger(i) for i in logs[:3] ]
	record_count = 5
	timeout = 6
	for cur_w in work_cl:
		for i in range(0,5):
			cur_w.info( 'Mess: %s, %i'% ('str', i))
		
	for f in logs[:3]:
		yield assert_not_equals,timeout,wait_log_recors(f,record_count,timeout)

def logger_client(*args, **kwargs):
	logger = kwargs["logger"]
	for i in range(0,kwargs['record_count']):
		logger.info('Thread: %i, threading mess %i'%(kwargs["thread_number"],i))
		
def testSeveralThreadsInOneFile():
	threads = []
	log_file_name = logs[3]
	cur_w = getLoger(log_file_name)
	threads_number = 5
	messages_count = 5
	from threading import Thread
	for t in range(0,threads_number):
		threads.append(Thread(target = logger_client, kwargs = {"logger":cur_w, "record_count":messages_count,"thread_number":t}))
	
	for t in threads:
		t.start()
		
	for t in threads:
		t.join()
		
	timeout = 15
	yield assert_not_equals,timeout,wait_log_recors(log_file_name,threads_number*messages_count,timeout)
	
def testCheckLogMessage():
	test_f = logs[4]
	log = getLoger(test_f)
	log.info("Test info message. Integer: %i, string: %s", 123,"test")
	log.debug("Test debug message. Integer: %i, string: %s", 234,"test")
	
	wait_log_recors(test_f,2,6)
	
	f = open(test_f,"r")
	info = f.readline()
	yield assert_true, info.find("** INFO ** Test info message. Integer: 123, string: test") > 0

	debug = f.readline()
	yield assert_true, debug.find("** DEBUG ** Test debug message. Integer: 234, string: test") > 0

def testCheckRotation():
	test_f = logs[5]
	log = getLoger(test_f)
	for i in range(0,50):
		log.info("Test rotation mess %i", i)
	
	wait_log_recors(test_f,50,20)
	from win32api import FindFiles
	yield assert_true, FindFiles(test_f).__len__() == 1
	yield assert_true, FindFiles(test_f+".1").__len__() == 1
	