import cherrypy
from cherrypy import expose
from Queue import Queue, Empty

class Root:
	
	@expose
	def log(self,*args,**kwargs):
		rec = kwargs[ 'record' ]
		import pickle
		record = pickle.loads( str(rec) )
		cherrypy.engine.log_cache.put(record)
		return 'Done'

if __name__ == '__main__':
	
	from logging.handlers import RotatingFileHandler
	from logging import Formatter
	import sys
	h = {}
	formatter = Formatter("%(asctime)s [%(process)s:%(thread)s] ** %(levelname)s ** %(msg)s")
	for i in sys.argv[1:]:
		h[i] = RotatingFileHandler(i, maxBytes=100 * 1024, backupCount=5)
		h[i].formatter = formatter

	def write():
		
		while True:
			try:
				rec = cherrypy.engine.log_cache.get_nowait()
				h[rec.name].emit(rec)
			except Empty:
				return

	from cherrypy.process import plugins
	pq = plugins.Monitor(cherrypy.engine,write,3)	
	pq.subscribe()	
	
	
	cherrypy.engine.log_cache = Queue()
	app = cherrypy.quickstart( Root(), config = "config.txt" )

	
	
