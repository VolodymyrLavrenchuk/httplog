import logging
from handler import PickleHttpHandler
import os
from nose.tools import eq_, ok_,assert_not_equals

svc_path = os.path.join(os.path.dirname(__file__), 'httpservice.conf')


logs = ["file%i.log"%x for x in range(1,5) ]

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
	return lines

def wait_log_recors(logfile, num_recs, timeout):
	import time
	for i in range(0,timeout+1):
		if getLogRecCount(logfile) == num_recs:
			break
		time.sleep(1)
	return i

def setup():
	from server import HTTPLogServiceHelper
	from win32api import DeleteFile, FindFiles
	server = HTTPLogServiceHelper()
	server.Stop()
	import time
	time.sleep(1)
	files = FindFiles("*.log")
	for f in files:
		print "deleting " + f[8]
		DeleteFile(f[8])

	config_str = logs[0]
	for f in logs[1:]:
		config_str += ","  + f
	import ini
	ini.set(svc_path,"default", "lognames" ,config_str)
		
	server.Start()

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
	threads_number = 10
	messages_count = 10
	from threading import Thread
	for t in range(0,threads_number):
		threads.append(Thread(target = logger_client, kwargs = {"logger":cur_w, "record_count":messages_count,"thread_number":t}))
	
	for t in threads:
		t.start()
		
	for t in threads:
		t.join()
		
	timeout = 15
	yield assert_not_equals,timeout,wait_log_recors(log_file_name,threads_number*messages_count,timeout)



