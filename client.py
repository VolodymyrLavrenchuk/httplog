import logging
import logging.handlers

log = logging.getLogger('SPAgent')
log.setLevel( logging.INFO )

log.addHandler( logging.handlers.HTTPHandler( 'localhost:8000', 'log' ) )


log.info( '5' )