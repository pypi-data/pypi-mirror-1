"""
Implements HtmlList class for "summary" pages - pages that has a list of
Link - Description.

You can use this file also as stand alone
usage: HtmlListSummary.py [-i[<N>]] <rul> <query> [<query>, ...]
	-i - Initialize the system using the first query, optional N is the number
		of expected results from this query. If -i is in use, you must enter
		more then one query.
	url - The base URL for the queries.
	query - One or more queries to test. That will follow a question mark in the
		URL. do not enter the question mark yourself.

In Order to see a demonstration of the system run:
HtmlListSummary.py -t [file_name]
If file name is not given it will run the scripts that in the "tests" file.
If file name is given, it will open it and run HtmlListSummary on it.

It will print the results to stdout.
"""

from HtmlListBase import HtmlListBase
from Utils import UnquoteHtml, StripTags, UrlOpen

import re

class HtmlListSummary (HtmlListBase):
	"""
	This class implements an HTML list for "summary" pages.
	It should work well with many pages that have a list of Link-Description.
	If it doesn't work, try to modify the class members under the "Tuning"
	section of __init__.
	This class generates a list of tuples (link, title, description)
	"""
	def __init__ (self):
		"""
		Tune the parameter of HtmlList
		Build some tag names lists we need.
		It also compiles some regular expressions.
		"""
		HtmlListBase.__init__ (self)

		## Start Tuning ##

		self.pattern_tags = 'div', 'ul', 'li', 'h3', 'h4', 'span', 'p' #, 'h1', 'h2', 'td'
		self.structural_attrs = []		# No attrs for Google, Yahoo NSM	# 'class', 'type', 'style'
		self.min_len = 1
		self.min_repeat = 5
		self.max_stdv_ptrn = 0.01		# need to be 0.05 for yahoo directories
		#self.max_stdv_indx = 0.001		# need for dmox.org

		## End Tuning ##

		# User Agent
		self.user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.8.1.9) Gecko/20071025 Firefox/2.0.0.9'
		# We don't want these tags in the result Title and Description
		self.remove_tags = 'br', 'link', 'nobr', 'em', 'table', 'tr', 'strong',\
			'cite', 'b', 'u', 'i', 'wbr'
		## Regex ##
		self._remove_tags_re = re.compile ('\s*</?\s*(%s)[^>]*>\s*' % '|'.join (self.remove_tags))
		self._text_re = re.compile ('>\s*([^<>]+)\s*<')
		self._link_re = re.compile ('<(a|area)\s+[^>]*?href\s*=\s*(\'.*?\'|".*?"|[^\s>]+)[^>]*?>')
		self._title_re = re.compile ('<(a|area)[^>]*>\s*(.*?)\s*</(a|area)>', re.S)


	def HandleSubHtml (self, sub_html):
		"""
		Breaks an HTML text to link, title and description.
		"""
		sub_html = self._remove_tags_re.sub (' ', sub_html)
		sub_html = sub_html.replace (' .', '.')
		# Title
		lst = [mtch for mtch in self._title_re.finditer (sub_html) if \
		 StripTags (mtch.group (2)).strip ()]
		if lst: title = UnquoteHtml (StripTags ( \
			lst[0].group (2).strip ('"\'\t\r\n ')))
		else: title = None
		# Link
		if lst:
			link = self._link_re.search (lst[0].group (0))
			if link: link = UnquoteHtml (link.group (2).strip ('"\'\t\r\n '))
		else: link = None
		# Description
		sub_html = self._title_re.sub ('', sub_html)
		lst = self._text_re.findall (sub_html)
		lst.sort (lambda x,y: cmp (len (y), len (x)))
		if lst: text = UnquoteHtml (lst[0]).strip ()
		else:	text = None
		return link, title, text

	def GetHtmlListUrl (self, url, validate = True):
		"""
		Call GetHtmlList with a text from an URL.
		If it cannot open the URL, it returns None.
		The method inserts the text of the page to self.text, so the user can
		access it.

		url can be a URL string or a Request object.

		This function creates a variable self.err_lst, in case of a URL-Error
		when opening the URL, err_lst will hold (code, msg, url)

		If "validate" is True (the default), it also validates the results list.
		If validation fails, it returns None
		"""
		self.err_lst = []
		self.text = UrlOpen (url, self.user_agent, err = self.err_lst)
		if not self.text: return None
		lst = self.GetHtmlList (self.text)
		if validate and not self._Validate (lst): return None
		return lst


	def Init (self, url = None, length = None, text = None):
		"""
		Overwrite base class Init. It tries to make sure the results list is
		valid.
		You have to use URL from the same website you are working with, and be
		certain it will return 'length' results.
		If "text" is not None, it will use this text for initialization and
		ignore the "url".
		"""
		if not text and url:
			text = UrlOpen (url, self.user_agent)
			if not text: return False
		lst = HtmlListBase.Init (self, text, length)
		if lst is False: return False
		if lst is None: return None
		if not self._Validate (lst): return False
		return lst

	def _Validate (self, lst):
		"""
		Validate the results list "lst".
		It test two things:
			1) there are no None values in the list.
			2) The description is longer the the title.
		"""
		for link, title, desc in lst:
			if not (link and title and desc): return False
			#if len (title) > len (desc): return False
		return True

	def _Test (self, test_name = None):
		""" Run some testing """
		from unittest import TextTestRunner
		if test_name:
			# Run specific test
			try:
				mod = __import__('Tests.' + test_name)
			except ImportError:
				exit ("Tests has no test: " + test_name)
			test = getattr(mod, test_name)
			TextTestRunner().run (test.Test())
		else:
			# Run all tests
			mod = __import__('Tests.tests')
			all_tests = getattr(mod, 'tests')
			for test in all_tests.tests:
				self._Test (test)



	def _PrintList (self, lst):
		""" Print results list """
		counter = 1
		for link, title, text in lst:
			print 'LINK:', counter, link
			print 'TITLE:', title
			print 'TEXT:', text
			print '------------------------------------------'
			counter += 1


if __name__ == '__main__':
	from sys import argv
	from datetime import datetime

	## Parse Arguments ##
	if len (argv) > 3 or (len (argv) > 2 and argv[1][0] != '-'):
		init = False
		init_len = None
		if argv[1].startswith ('-i'):
			init = True
			if len (argv[1]) > 2:
				init_len = int (argv[1][2:])
			url = argv[2]
			init_query = argv[3]
			index = 4
		else:
			url = argv[1]
			index = 2
		if len (argv) > index:
			queries = argv[index:]
		else:
			queries = []
	elif len (argv) > 1 and argv[1] == '-t':
		test_name = None
		if len (argv) > 2: test_name = argv[2]
		HtmlListSummary ()._Test (test_name)
		exit (0)
	else:
		exit (__doc__)

	hl = HtmlListSummary ()
	if init:
		init_url = url + '?' + init_query
		print "Initializing the system", init_url
	else:
		init_url = None
	if hl.Init (init_url, init_len) is False:
		print hl.GetPattern ()
		exit ("cannot initialize the system")

	for query in queries:
		start = datetime.now ()
		query_url = url + '?' + query
		print query_url + '\n'
		lst = hl.GetHtmlListUrl (query_url)
		if not lst: print 'ERROR for: %s' % query, hl.err_lst
		else:	hl._PrintList (lst)
		print 'Time:', datetime.now () - start
		print 'Pattern:', hl.GetPattern ()
		print '\n==========================================\n'




