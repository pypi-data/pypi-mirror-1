#!python
"""
Implements HtmlList class for "summary" pages - pages that has a list of
Link - Description.

You can use this file also as stand alone
usage: HtmlListSummary.py <rul>
It will print the results to stdout.
"""

import re

from htmllist_base import HtmlList
from utills import unquote_html, strip_tags, url_open

class HtmlListSummary(HtmlList):
	"""
	This class implements an HTML list for "summary" pages.
	It should work well with many pages that have a list of Link-Description.
	If it doesn't work, try to modify the class members under the "Tuning"
	section of __init__.
	This class generates a list of tuples (link, title, description)
	"""
	def __init__(self):
		""" Build some tag names lists we need.
		It also compiles some regular expressions.
		"""
		HtmlList.__init__(self)

		# User Agent
		self.user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.8.1.9) Gecko/20071025 Firefox/2.0.0.9'
		# We don't want these tags in the result Title and Description
		self.remove_tags = 'br', 'link', 'nobr', 'em', 'table', 'tr', 'strong',\
			'cite', 'b', 'u', 'i', 'wbr'
		## Regex ##
		self._remove_tags_re = re.compile('\s*</?\s*(%s)[^>]*>\s*' % '|'.join(
			self.remove_tags))
		self._text_re = re.compile('>\s*([^<>]+)\s*<')
		self._link_re = re.compile(
			'<(a|area)\s+[^>]*?href\s*=\s*(\'.*?\'|".*?"|[^\s>]+)[^>]*?>')
		self._title_re = re.compile('<(a|area)[^>]*>\s*(.*?)\s*</(a|area)>', re.S)


	def handle_sub_html(self, lst, next):
		""" Breaks an HTML text to link, title and description.
		"""
		sub_html = HtmlList.handle_sub_html(self, lst, next)
		sub_html = self._remove_tags_re.sub(' ', sub_html)
		sub_html = sub_html.replace(' .', '.')
		# Title
		lst = [mtch for mtch in self._title_re.finditer(sub_html) if \
		 strip_tags(mtch.group(2)).strip()]
		if lst: title = unquote_html(strip_tags( \
			lst[0].group(2).strip('"\'\t\r\n ')))
		else: title = None
		# Link
		if lst:
			link = self._link_re.search(lst[0].group (0))
			if link: link = unquote_html(link.group(2).strip('"\'\t\r\n '))
		else: link = None
		# Description
		sub_html = self._title_re.sub('', sub_html)
		lst = self._text_re.findall(sub_html)
		lst.sort(lambda x,y: cmp(len(y), len(x)))
		if lst: text = unquote_html(lst[0]).strip()
		else:	text = None
		return link, title, text

	def get_html_list_url(self, url, validate = True):
		""" Call get_html_list with a text from an URL.
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
		self.text = url_open(url, self.user_agent, err=self.err_lst)
		if not self.text: return None
		lst = self.get_html_list(self.text)
		if validate and not self._validate(lst): return None
		return lst

	def _validate(self, lst):
		""" Validate the results list "lst".
		It test two things:
			1) there are no None values in the list.
			2) The description is longer the the title.
		"""
		for link, title, desc in lst:
			if not (link and title and desc): return False
			#if len (title) > len (desc): return False
		return True

	def _print_list(self, lst):
		""" Print results list """
		counter = 1
		for link, title, text in lst:
			print 'LINK:', counter, link
			print 'TITLE:', title
			print 'TEXT:', text.encode('utf_8')
			print '------------------------------------------'
			counter += 1


if __name__ == '__main__':
	from sys import argv
	from time import time

	if len(argv) < 2: exit(__doc__)

	hl = HtmlListSummary()
	start = time()
	lst = hl.get_html_list_url(argv[1], False)
	if not lst: print 'ERROR:', hl.err_lst
	else: hl._print_list(lst)
	print 'Duration:', time() - start
	print 'Pattern:', hl.output_lst, hl.repeats




