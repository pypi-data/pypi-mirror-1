"""Fix silly lack-of-API problems in logging module

Adds constants to the log objects.
Adds getException(err) to log objects to retrieve 
formatted exception or err if traceback not available.
"""
try:
	from cStringIO import StringIO
except ImportError, err:
	from StringIO import StringIO
import traceback, logging

getLog = logging.getLogger

ENABLE_ERROR_LOGGING = True

def getException(error):
	"""Get formatted traceback from exception"""
	exception = str(error)
	file = StringIO()
	try:
		traceback.print_exc( limit=10, file = file )
		exception = file.getvalue()
	finally:
		file.close()
	return exception
logging.Logger.getException = staticmethod( getException )
logging.Logger.err = logging.Logger.error
logging.Logger.DEBUG = logging.DEBUG 
logging.Logger.WARN = logging.WARN 
logging.Logger.INFO = logging.INFO 
logging.Logger.ERR = logging.Logger.ERROR = logging.ERROR

def logOnFail( function, log ):
	"""Produce a function that does what function does, but with on-fail logging"""
	if ENABLE_ERROR_LOGGING:
		def loggedFunction( *args, **named ):
			try:
				return function( *args, **named )
			except Exception, err:
				log.warn(
					"""Failure on %s: %s""", function.__name__, log.getException( err )
				)
				raise
		loggedFunction.__name__ = function.__name__
		loggedFunction.__doc__ = function.__doc__
		loggedFunction.__dict__.update( function.__dict__ )
		return loggedFunction
	else:
		return function

