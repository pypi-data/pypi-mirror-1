'''Node logger.'''
import logging
defaultFormatter=logging.Formatter('%(module)-6s: %(name)-12s: %(levelname)-5s:'
		' %(message)s')
defaultHandler=logging.StreamHandler()
defaultHandler.setFormatter(defaultFormatter)
defaultHandler.setLevel(logging.INFO)
def enable():
	logging.getLogger('').addHandler(defaultHandler)
def filename(fname):
	fileHandler=logging.FileHandler(fname)
	fileHandler.setFormatter(defaultFormatter)
	fileHandler.setLevel(logging.DEBUG)
	logging.getLogger('').addHandler(fileHandler)
