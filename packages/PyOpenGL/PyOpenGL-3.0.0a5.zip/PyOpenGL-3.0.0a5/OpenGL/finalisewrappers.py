"""Function to finalise all wrappers in a given namespace (dictionary)

Wrapper objects provide finalise calls, these allow for late(r) lookup of
argument names in the function, allowing for more dynamism in setting
up wrappers (multiple levels of operation can mutate a wrapper.

We need to call finalise on the contents of each "simple" module 
and each root module and extension module.
"""
def finalise( dictionary ):
	# ick, this is just horrifically ugly, need to figure out a better approach
	raise RuntimeError( """Shouldn't be using this!""" )
	from OpenGL import converters
	for key,value in dictionary.iteritems():
		if (
			(not isinstance( value, converters.Converter)) and 
			hasattr( value, 'finalise' ) and 
			value.finalise is not finalise
		):
			if callable( value.finalise ):
				try:
					value.finalise()
				except Exception, err:
					err.args += ( 'For name: %s'%(key), )
					raise
