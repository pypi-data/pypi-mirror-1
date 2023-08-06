"""
Implements the BreakHtmlPage class using BeautifulSoup.
This class should be used with RepeatPattern in order to get a repetitive
pattern in an HTML text.

This module uses BeautifulSoup
http://www.crummy.com/software/BeautifulSoup/
"""

from BeautifulSoup import BeautifulSoup, Tag
from Utils import ListToDict

class BreakHtmlPage:
	"""
	This class "breaks HTML page" using BeautifulSoup:
	It has two main functions:
		Get an HTML page text, and break it to a list of tags. A tag is a
		two-tuple (name, attrs), attrs is a set of two-tuples (name, value).

		Get a list of tags and return a list of all places in the HTML page these
		tags occur in a sequence (lookiong only on tags from the pattern_tags
		list). The result is a list of sub-string of the original HTML text.
	"""
	def __init__ (self):
		"""
		Build some tag and attributes lists.
		the parameters 'pattern_tags' and 'structural_attrs' are class tuples
		that can be changed.
			pattern_tags - a list of tag names to be included in the tag list.
			structural_attrs - a list of attribute names to be included in the
				tag attribute set.
		"""
		self.pattern_tags = 'div', 'ul', 'li', 'h1', 'h2', 'h3', 'h4', 'td', 'span', 'p'
		self.structural_attrs = 'class', 'style', 'type'

		self._tag_lst = []
		self._orig_lst = []
		self._index_lst = []
		self._html = ''
		self._soup = None

	def _PrepareTag (self, tag):
		"""
		Takes a BeautifulSoup tag and return a two tuple (name, attrs-set).
		attrs-set is by itself a set of two tuple (name, value), or None.
		"""
		if not tag.attrs: return tag.name, None
		attrs = set ()
		for key, val in tag.attrs:
			if key in self.structural_attrs:
				attrs.add ((key, val))
		if not attrs: return tag.name, None
		return tag.name, frozenset (attrs)

	def Feed (self, data):
		"""
		Add text to be parsed.
		"""
		self._html += data

	def Close (self):
		"""
		Should be called after all HTML text has been feed in.
		"""
		# Build the soup
		self._soup = BeautifulSoup (self._html)
		tag = self._soup.body
		index = 0
		# Build the tags list.
		while tag:
			self._orig_lst.append (tag)
			if isinstance (tag, Tag) and tag.name in self.pattern_tags:
				self._tag_lst.append (self._PrepareTag (tag))
				self._index_lst.append (index)
			index += 1
			tag = tag.next

	def GetTagList (self, fltr = None):
		"""
		Return a list of tags in the HTML text that are in the pattern_tags
		list. Each 'tag' is a two-tuple (name, attrs), attrs is a set of
		two-tuples (name, value) of the attributes in the structural_attrs list.

		fltr - Optional sequence of tags not to include in the list
		"""
		if fltr: return filter (lambda x: x not in fltr, self._tag_lst)
		else: return self._tag_lst

	def GetTextForTagList (self, lst):
		"""
		Return a list of sub-string of the original HTML text.
		lst is a list of two-tuples (start, end) where the pattern we need occur
		in self._tag_lst, and so it is also the indexes in self._index_lst
		"""
		if not lst: return []
		# Extract the HTML from the original tags list
		html_lst = []
		for start, end in lst:
			start = self._index_lst[start]
			end = self._index_lst[end-1]+1	# "end" is the tag after the pattern
			parents_lst = []
			sub_html = ''
			for tag in self._orig_lst[start:end]:
				if isinstance (tag, Tag):
					if tag.parent not in parents_lst:
						sub_html += str (tag)
					parents_lst.append (tag)
			html_lst.append (sub_html)
		return html_lst


if __name__ == '__main__':
	from RepeatPattern import RepeatPattern

	page = open ('tests/clean_google_10.html')
	bhp = BreakHtmlPage ()
	for text in page.readlines ():
		bhp.Feed (text)
	bhp.Close ()
	page.close ()

	rp = RepeatPattern (min_repeat = 5)
	rp.BuildSuffixTrie (bhp.GetTagList ())
	print rp.FindRepeatPattern ()
	lst = bhp.GetTextForTagList (rp.GetIndexesList ())

	print "number of results:", len (lst)
	for html in lst:
		print html
		print '================================================================'






