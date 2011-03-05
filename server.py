import cherrypy
from cherrypy import expose
from Queue import Queue
from threading import Event
from cherrypy.process import plugins

g_event = Event()

def convert_http_none(entry, key):
	if entry[key] == u'None':
		entry[key] = None

def convert_http_float(entry, key):
	entry[key] = float(entry[key])

def process_http_log_entry(entry):
	entry['args'] = ()
	convert_http_float(entry,'created')
	convert_http_float(entry,'msecs')
	convert_http_none(entry, 'exc_text')
	convert_http_none(entry, 'exc_info')
	
def put(entry):
	from logging import makeLogRecord, Formatter
	name = entry['name']
	cache = cherrypy.engine.log_cache
	formatter = logging.Formatter("%(asctime)s [%(process)s:%(thread)s] ** %(levelname)s ** %(msg)s")
	process_http_log_entry(entry)
	rec =  makeLogRecord(entry)
	cache.put( {name:formatter.format(rec)}, True )
	
class Root:
	
	@expose
	def log(self,*args,**kwargs):
	
		put( kwargs )
		return 'Done'

class LogWriter(plugins.SimplePlugin):
	def __init__(self, bus):
		plugins.SimplePlugin.__init__(self, bus)
		
	def write(self):
		while cherrypy.engine.state != cherrypy.engine.states.STOPPED:
			g_event.wait()
			while not cherrypy.engine.log_cache.empty():
				logger.info( str( cherrypy.engine.log_cache.get(True) ) ) 
			g_event.clear()
	
	def start(self):
		from threading import Thread
		main_th = Thread(target=self.write)
		main_th.start()		

	def stop(self):
		g_event.set()

if __name__ == '__main__':
	
	import logging
	from logging.handlers import RotatingFileHandler

	logger = logging.getLogger('MyLogger')
	logger.setLevel(logging.INFO)
	handler = RotatingFileHandler('httplogger.txt', maxBytes=100 * 1024, backupCount=5)
	logger.addHandler(handler)

	def process_q():
		if not cherrypy.engine.log_cache.empty():
			g_event.set()
			
	lw = LogWriter(cherrypy.engine)
	lw.subscribe()
	
	pq = plugins.Monitor(cherrypy.engine,process_q,3)	
	pq.subscribe()	
	
	#cherrypy.engine.log_writer = plugins.Monitor(cherrypy.engine,write,2)	
	#cherrypy.engine.log_writer.subscribe()
	
	
	cherrypy.engine.log_cache = Queue()
	app = cherrypy.quickstart( Root(), config = "config.txt" )

	
	
