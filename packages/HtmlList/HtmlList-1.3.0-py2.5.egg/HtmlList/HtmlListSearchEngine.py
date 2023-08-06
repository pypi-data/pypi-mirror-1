"""
Implements HtmlList class for search engines.

If running this module as stand along you should give it a search engine name
from: google | yahoo | msn, and a list of terms.
OR
'url' <url to parse>

It will print the results to stdout.
"""

from HtmlListBase import HtmlListBase
from Utils import UnquoteHtml, StripTags, UrlOpen

import re

class HtmlListSearchEngine (HtmlListBase):
	"""
	This class implements an HTML list for search engines results.
	It should work well with most search engines (and maybe other types of pages)
	If it doesn't work try modify the start_tags and ignore_tags lists*.
	It returns a list of tupels (link, title, description)

	* The max_stdv_gap class member is also important and sensitive number,
	after trial and error I set it to 0.02 You can play with this number as well.
	"""
	def __init__ (self):
		"""
		Build some tag names lists we need.
		It also compiles some regular expressions.
		"""
		HtmlListBase.__init__ (self)
		self.ignore_tags = 'br', 'link', 'nobr', 'em', 'table', 'tr', 'strong',\
			'cite', 'b', 'u', 'i', 'wbr', 'a'
		self.start_tags = 'div', 'ul', 'li', 'h1', 'h2', 'h3', 'h4', 'td', 'span',\
			'p'
		self.structural_attrs = 'class', 'style', 'type'
		self.remove_tags = list (self.ignore_tags)
		self.remove_tags.remove ('a')
		self.filter_func = lambda lst: lst[0] in self.start_tags
		self.min_len = 2
		self.min_repeat = 2
		self.max_stdv_gap = 0.02
		self.user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.8.1.9) Gecko/20071025 Firefox/2.0.0.9'

		## Regex ##
		self._ignore_tags_re = re.compile ('\s*</?\s*(%s)[^>]*>\s*' % '|'.join (self.remove_tags))
		self._text_re = re.compile ('>\s*([^<>]+)\s*<')
		self._link_re = re.compile ('<(a|area)\s+[^>]*?href\s*=\s*(\'.*?\'|".*?"|[^\s>]+)[^>]*?>')
		self._title_re = re.compile ('<(a|area)[^>]*>\s*(.*?)\s*</(a|area)>', re.S)


	def HandleSubHtml (self, sub_html):
		"""
		Breaks an HTML text to link, title and description.
		"""
		#orig = sub_html
		sub_html = self._ignore_tags_re.sub (' ', sub_html)
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
		if lst: text = UnquoteHtml (lst[0])
		else:	text = None
		return link, title, text #, orig

	def GetHtmlListUrl (self, url, validate = True):
		"""
		Call GetHtmlList with a text from an URL.
		If it cannot open the URL, it returns None.
		The method insert the text of the page to self.text, so the user can
		access it.

		url can be a URL string or a Request object.

		This function creates a variable self.err_lst, in case of a URL-Error
		in opening the URL, err_lst will hold (code, msg, url)

		If "validate" is True (the default), it also validate the results list.
		If validation fails, it returns None
		"""
		self.err_lst = []
		self.text = UrlOpen (url, self.user_agent, err = self.err_lst)
		if not self.text: return None
		lst = self.GetHtmlList (self.text)
		if validate and not self._Validate (lst): return None
		return lst


	def Init (self, url = None, length = None):
		"""
		Overwrite base class Init. It tries to make sure the results list is
		valid.
		You have to use URL from the same search engine, and be certain it will
		return 'length' results.
		"""
		text = None
		if url:
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


if __name__ == '__main__':
	from sys import argv
	from datetime import datetime

	if len (argv) < 2 or argv[1] not in ('google', 'yahoo', 'msn', 'url'):
		print """usage:
python HtmlListSearchEngine.py [google|yahoo|msn] <term> [<term> ...]
OR
python HtmlListSearchEngine.py url <url to parse>
"""
		exit (0)

	hl = HtmlListSearchEngine ()
	if argv[1] == 'google':
		url = 'http://www.google.com/search?num=10&q=python+site:python.org'
		base_url = 'http://www.google.com/search?num=100&q='
	elif argv[1] == 'yahoo':
		url = 'http://search.yahoo.com/search?n=10&p=python+site:python.org'
		base_url = 'http://search.yahoo.com/search?p='
	elif argv[1] == 'msn':
		url = 'http://search.msn.com/results.aspx?q=python+site:python.org'
		base_url = 'http://search.msn.com/results.aspx?q='
	else:
		url = None
		base_url = ''
	if hl.Init (url, 10) is False:
		print hl.GetPattern ()
		exit ('cannot init the system')

	for term in argv[2:]:
		start = datetime.now ()
		print base_url + term
		lst = hl.GetHtmlListUrl (base_url + term)
		if not lst: print 'ERROR for: %s' % term, hl.err_lst
		else:
			counter = 1
			for link, title, text in lst:
				print 'LINK:', link, counter
				print 'TITLE:', title
				print 'TEXT:', text
				print '------------------------------------------'
				counter += 1
		print datetime.now () - start
		print hl.GetPattern ()
		print '=========================================='




