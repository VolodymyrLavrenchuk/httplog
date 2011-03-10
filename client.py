import logging
from handler import PickleHttpHandler

def getLoger(name):
	log = logging.getLogger(name)
	log.setLevel( logging.DEBUG )
	log.addHandler( PickleHttpHandler( 'localhost:8000', 'log', method = 'POST' ) )
	return log

	
getLoger("WebReports.log").info( 'Mess: %s, %i','str', 5)
getLoger("SpBrowserBroker.log").debug( 'Mess: %s, %i','str', 5)

