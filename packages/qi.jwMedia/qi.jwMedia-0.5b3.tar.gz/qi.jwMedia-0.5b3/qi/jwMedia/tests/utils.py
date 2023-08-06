from os.path import dirname, join
from qi.jwMedia import tests 

def getFile(filename):
	""" return a file object from the test data folder """
	filename = join(dirname(tests.__file__), 'data', filename)
	return open(filename, 'r')

