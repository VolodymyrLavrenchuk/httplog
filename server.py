import cherrypy
from cherrypy import expose
from Queue import Queue, Empty
import sys

class Root:
	
	@expose
	def log(self,*args,**kwargs):
		rec = kwargs[ 'record' ]
		import pickle
		record = pickle.loads( rec )
		cherrypy.engine.log_cache.put(record)
		return 'Done'
import ini
import os
svc_path = os.path.join(os.path.dirname(__file__), 'httpservice.conf')

def getIntConfigValue(name):
	return int(getConfigValue(name))

def getConfigValue(name):
	return ini.read( svc_path, 'default',name)

def Register():
	from logging.handlers import RotatingFileHandler
	from logging import Formatter
	
	h = {}
	formatter = Formatter("%(asctime)s [%(process)s:%(thread)s] ** %(levelname)s ** %(message)s")
	logsnames = getConfigValue('lognames')
	qsize = getIntConfigValue('qsize')
	rotation_bytes = getIntConfigValue('rotation_bytes')
	rotation_count = getIntConfigValue('rotation_count')

	for i in logsnames.split(","):
		h[i] = RotatingFileHandler(os.path.join(os.path.dirname(__file__), i), maxBytes=rotation_bytes, backupCount=rotation_count)
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
	
	cherrypy.engine.log_cache = Queue(maxsize = qsize)
	conf_path = os.path.join(os.path.dirname(__file__), "config.txt")
	cherrypy.config.update(conf_path)
	app = cherrypy.quickstart( Root() )

from ServiceBase import ServiceLauncher
class HTTPLogService(ServiceLauncher):
	_svc_name_ = _svc_display_name_ = ini.read( svc_path, 'default','name' )
	_svc_description_ = ini.read( svc_path, 'default', 'description' )
	def __init__(self, args):
		ServiceLauncher.__init__(self, args, Register)

from ServiceBase import ServiceHelperBase
class HTTPLogServiceHelper(ServiceHelperBase):
	Class = HTTPLogService
	File = __file__	

def InstallAsService():
	service = HTTPLogServiceHelper()
	service.Stop()
	service.Remove()
	service.Install()
	service.Start()
	
if __name__ == '__main__':
	if sys.argv.__len__() > 1 and sys.argv[1] == "installservice":
		InstallAsService()
	else:
		Register()
	


	
	
