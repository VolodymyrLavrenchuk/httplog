import logging.handlers

class PickleHttpHandler(logging.handlers.HTTPHandler):
	def mapLogRecord(self, record):
		import pickle
		return {'record':pickle.dumps(record)}
