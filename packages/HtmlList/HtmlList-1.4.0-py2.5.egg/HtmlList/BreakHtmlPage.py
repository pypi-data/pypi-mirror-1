"""
Implements the BreakHtmlPage class.
This class should be used with RepeatPattern in order to get a repetitive
pattern in an HTML text.
* This class doesn't work with invalid HTML! Use BreakHtmlPageBS for those.
"""

from HTMLParser import HTMLParser, HTMLParseError
from Utils import StripScripts

class BreakHtmlPage (HTMLParser):
	"""
	This class extend the HTMLParser class. It does two things:

		Get an HTML page text, and break it to a list of tags. A tag is a
		two-tuple (name, attrs), attrs is a set of two-tuples (name, value).

		Get a list of tags and return a list of all places in the HTML page this
		tags occur in a sequence (it looks only on tag from the pattern_tags
		list). The result is a list of sub-string of the original HTML text.
	"""
	def __init__ (self):
		"""
		Init the HMTMLParser, and build some tag and attributes lists.
		the parameters 'pattern_tags' and 'structural_attrs' are class tuples
		that can be changed.
			pattern_tags - a list of tag names to be included in the tag list.
			structural_attrs - a list of attribute names to be included in the
				tag attribute set.
		"""
		HTMLParser.__init__ (self)

		self._start = False
		self.pattern_tags = 'div', 'ul', 'li', 'h1', 'h2', 'h3', 'h4', 'td', 'span', 'p'
		self.structural_attrs = 'class', 'style', 'type'

		self._tag_lst = []
		self._html_lst = []

	def feed (self, data):
		"""
		Overload the base class feed method.
		Add text to be parsed. It strip all <script> tags from the text, as
		HTMLParser has problems dealing with it.
		"""
		data = StripScripts (data)
		self._html_lst.extend (data.splitlines ())
		HTMLParser.feed (self, data)
	def Feed (self, data): self.feed (data)

	def close (self):
		"""
		Overload the base class method. Should be called after all HTML text
		has been feed in.
		"""
		HTMLParser.close (self)
	def Close (self): self.close ()

	def handle_starttag (self, tag, attrs):
		"""
		Overload the base class method.
		Inner method to deal with an HTML tag.
		"""
		if not self._start and tag == 'body':
			self._start = True
		if self._start and tag in self.pattern_tags:
			attrs = set ([(name, val) for name, val in attrs if \
				name in self.structural_attrs])
			self._tag_lst.append ((tag, attrs, self.getpos ()))

	def _GetAllSections (self, lst):
		"""
		Return a list of indexes of a pattern in the html_lst.
		lst is a list of two-tuples (start, end) where the pattern we need occur
		in self._tag_lst.
		"""
		return [(self._tag_lst[start][2], self._tag_lst[end][2]) for \
			start, end in lst]

	def _GetAllHtml (self, lst):
		"""
		Return a list of sub-string of the original HTML text, where the list
		of tags 'lst' occur.
		It looks only on tags that in the pattern_tags list.
		"""
		html_sec = []
		for itm in lst:
			start_ln = itm[0][0] - 1
			start_chr = itm[0][1]
			end_ln = itm[1][0] - 1
			end_chr = itm [1][1]
			if start_ln == end_ln:
				html = self._html_lst[start_ln][start_chr:end_chr]
			else:
				html = self._html_lst[start_ln][start_chr:]
				if start_ln + 1 < end_ln:
					html += '\n'.join (self._html_lst[start_ln + 1:end_ln])
				if end_chr > 0:
					html += '\n' + self._html_lst[end_ln][:end_chr]
			html_sec.append (html)
		return html_sec

	def GetTagList (self):
		"""
		Return a list of tags in the HTML text that are in the pattern_tags list.
		Each 'tag' is a two-tuple (name, attrs), attrs is a set of
		two-tuples (name, value) of the attributes in the structural_attrs list.
		"""
		return [(tag, attrs) for tag, attrs, pos in self._tag_lst]

	def GetTextForTagList (self, lst):
		"""
		Wrapper of _GetAllHtml apply on _GetAllSections.
		It return a list of sub-string of the original HTML text, where
		the list of tags 'lst' occur (only tags from the pattern_tags list).
		"""
		return self._GetAllHtml (self._GetAllSections (lst))



if __name__ == '__main__':
	from RepeatPattern import RepeatPattern

	page = open ('tests/weather_dmoz_20.html')
	bhp = BreakHtmlPage ()
	for text in page.readlines ():
		bhp.Feed (text)
	bhp.Close ()
	page.close ()

	rp = RepeatPattern ()
	rp.BuildSuffixTrie (bhp.GetTagList ())
	rp.FindRepeatPattern ()
	lst = bhp.GetTextForTagList (rp.GetIndexesList ())

	print "number of results:", len (lst)
	for html in lst:
		print html
		print '================================================================'






