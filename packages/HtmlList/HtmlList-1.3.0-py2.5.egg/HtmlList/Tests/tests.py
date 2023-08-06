
# Define here all the tests in the Tests package.
# I could not do it using __init__
tests = [
	'google',
	'yahoo',
	'msn',
	'dmoz',
	'yahoo_dir',
	'bp_links',
	'bp_resources'
]

from unittest import TestCase
from HtmlListSummary import HtmlListSummary

class MyBaseTest (TestCase):
	"""
	Defines methods I need in all the tests
	"""
	def Init (self, test_file, init_file = None, args = {}):
		"""
		Returns a list of results from HtmlListsummary
			test_file - Name of file to test
			init_file - Optional name of file to initialize on
			args - Optional arguments dictionary to pass to HtmllistSummary
		"""
		hl = HtmlListSummary ()
		## Set HtmlList arguments if any ##
		hl.__dict__.update (args)
		## Initialize ##
		init_text = None
		init_len = 0
		if init_file:
			init_text = open('Tests/' + init_file).read ()
			init_len = self.GetResultsNum (init_file)
		self.failIfEqual (hl.Init (length = init_len, text = init_text), False, \
			"Initialization")

		text = open('Tests/' + test_file).read ()
		lst = hl.GetHtmlList (text)
		print test_file, '>>', hl.GetPattern ()	# Good for debug
		fltr = hl.FindFilter ()
		if fltr: print "Optional Filter", fltr
		self.failUnlessEqual (len (lst), self.GetResultsNum (test_file))
		return lst

	def GetResultsNum(self, file_name):
		"""
		file_name is XXX_YYY.html
			XXX can be anything w/o a dot
			YYY is a number
		The function returns the number YYY
		"""
		str1 = file_name.split ('.')[0]
		str2 = str1[str1.rfind ('_')+1:]
		return int (str2)
