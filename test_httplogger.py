import logging
from handler import PickleHttpHandler

def getLoger(file_name):
	log = logging.getLogger(file_name)
	log.setLevel( logging.DEBUG )
	log.addHandler( PickleHttpHandler( 'localhost:8000', 'log', method = 'POST' ) )
	return log

def test():
	logs = ["file1.log","file2.log", "file3.log"]

	work_cl = [ getLoger(i) for i in logs ]
	
	for cur_w in work_cl:
		cur_w.info( 'Mess: %s, %i'% ('str', 5))
	
	