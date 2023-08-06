"""
The module defines BreakHtmlPage class with some "private" and "public" help
functions.

DEF_EXCLUDE_TAGS is a list of tags names to always exclude (see BreakHtmlPage
documentation)

This module uses html5lib
http://code.google.com/p/html5lib/
"""

from cStringIO import StringIO
from xml.sax.saxutils import escape

from html5lib import HTMLParser
from html5lib.treebuilders.simpletree import Element

from utills import iter2tuple
from tag_tools import Tag, TagSet

# This is the default excluding tags (as strings),
# I don't think we will ever need to change them.
DEF_EXCLUDE_TAGS = "html", "head", "title", "script", "style", "body"

def _toxml(elm, stop_tag, parents):
	""" This is an override of the simpletree.Elemnt.toxml method.
	It take 'stop_tag" to stop the scan of the tree if we got to it, and
	'parents' a reference to a set that holds all the parent tags we already
	scanned
	"""
	if elm.type != 5: return elm.toxml()
	result = '<' + elm.name
	if elm.attributes:
		for name,value in elm.attributes.iteritems():
			result += u' %s="%s"' % (name, escape(value,{'"':'&quot;'}))
	if elm.childNodes:
		parents.add(elm)
		result += '>'
		for child in elm.childNodes:
			if child is stop_tag: break		# My Addition
			result += _toxml(child, stop_tag, parents)
		result += u'</%s>' % elm.name
	else:
		result += u'/>'
	return result

def _scan_tree(elm, func, stop_tag, parents):
	""" Similar to _toxml, scans the tree until 'func(elm) returns True. """
	if func(elm): return True
	if elm.childNodes:
		parents.add(elm)
		for child in elm.childNodes:
			if child is stop_tag: break
			if _scan_tree(child, func, stop_tag, parents): return True
	return False

def list2text(lst, stop_tag=None):
	""" Render the HTML test a list of HTML elements represent.
	It takes a second argument, stop_tag, which it will stop the rendering of
	the HTML if it finds this tag in one of the child tags, so the returned HTML
	section will not overlap, even if one of the tags in the list spans over the
	next list (which will start with the stop_tag).
	"""
	if not lst: return None
	# I need the HTML under all tags in this range, that has the same
	# parent as the first tag
	parents = set()
	return '\n'.join([_toxml(node, stop_tag, parents) for \
		node in lst if not node.parent in parents
	])

# Returns True if an elemnt is a not empty text element.
is_text_elm = lambda elm: elm.type == 4 and elm.value.strip()

def validate_list(elm_lst, stop_tag=None, good_elm_func=None):
	""" Scans the sub HTML Element list that in elm_lst, until it finds an
	element that good_elm_func returns True on it.

	elm_lst - A list of tags (html5lib.simpletree.Element).
	stop_tag An optional tag to stop the scan on (like in list2text).
	good_elm_func An optional function that take Element and return boolean.
	The default function checks if the element is none empty text.

	Returns True if found an element such as the above, or False.
	"""
	if not elm_lst: return False
	if not good_elm_func:
		good_elm_func = is_text_elm
	parents = set()
	for elm in elm_lst:
		if not elm.parent in parents and _scan_tree(
		elm, good_elm_func, stop_tag, parents):
			return True
	return False


class BreakHtmlPage(object):
	""" Implements the BreakHtmlPage class using html5lib.
	This class should be used with RepeatPattern in order to get a repetitive
	pattern in an HTML text.

	BreakHtmlPage has two "public" variables: include_tags and exclude_tags.
	These are TagSets, if they are not empty, the class will include-only/
	exclude the tags that in this sets.
	See TagSet documentation for more details.

	This class will not return an overlapping HTML sections.
	"""
	def __init__(self):
		self._html = None			# The HTML buffer
		self._orig_lst = None		# Original list of elements in the page
		self._index_lst = None		# List of indices in orig_lst of the tags we
									# 	work with
		self.include_tags = TagSet()
		self.exclude_tags = TagSet()
		self.exclude_tags += DEF_EXCLUDE_TAGS

	def feed(self, data):
		""" Add text to be parsed. """
		if not self._html:
			self._html = StringIO()
		self._html.write(data)

	def close(self):
		""" Should be called after all HTML text has been feed in. """
		doc = HTMLParser().parse(self._html)
		self._html.close()
		self._orig_lst = tuple(doc)

	def clear(self):
		""" Clear all old data """
		if self._html:
			self._html.close()
		self._html = StringIO()
		self._orig_lst = None
		self._index_lst = None

	@iter2tuple
	def get_tag_list(self):
		""" Return the list of tags in the HTML body. Each tag is a Tag instance
		It also builds a translation list between the indices in the tag-list it
		gives to RepeatPattern and the original HTML list.
		"""
		if not self._orig_lst: return
		self._index_lst = []
		for index, node in enumerate(self._orig_lst):
			if isinstance(node, Element):
				tag = Tag(node.name, node.attributes)
				if (not self.include_tags or tag in self.include_tags) and \
				(not self.exclude_tags or tag not in self.exclude_tags):
					self._index_lst.append(index)
					yield tag

	def get_text_list(self, lst):
		""" Return an iterator over lists of elements in an HTML page.
		This lists are the sections we may be interested in.
		The iterator item is two tuple (list, name). next is the first element
		in the next list (or None). It is used to stop the rendering of the HTML
		section (to avoid overlapping)
		"""
		if not self._orig_lst or not self._index_lst or not lst: return
		# Extract the HTML from the original tags list
		for index, entry in enumerate(lst):
			start = self._index_lst[entry[0]]
			end = self._index_lst[entry[1]] + 1	# "end" is the tag after the pattern
			if index < len(lst) - 1:	# The next start tag
				next = self._orig_lst[self._index_lst[lst[index+1][0]]]
			else:
				next = None
			yield (self._orig_lst[start:end], next)

	@classmethod
	def test(cls, verbose=False):
		""" Testing this class

		I'm not testing the HTML overlap prevention (yet).
		An example of it working is if processing the page:
		http://docs.python.org/dev/whatsnew/2.6.html
		commenting out the "...# My Addition" line in my_toxml, will break it.
		"""
		bhp = cls()
		f = open("test_google.html")
		for line in f.readlines():
			bhp.feed(line)
		bhp.close()

		if verbose:
			print "Test the exclusion feature, the inclusion hopefully works the same"
		bhp.exclude_tags += Tag("em"), Tag("a", {"class": "gb2"})
		tag_lst = bhp.get_tag_list()

		assert Tag("html", {"class": "bar"}) not in tag_lst
		assert Tag("a", {"class": "gb2"}) not in tag_lst

		if verbose:
			print "Manually find the 'known pattern' indices"
		start_lst = []
		end_lst = []
		start_tag = Tag("li", {"class": "g"})
		end_tag = Tag("span", {"class": "gl"})

		start_lst = [index for index, tag in enumerate(tag_lst) if tag == start_tag]
		end_lst = [index for index, tag in enumerate(tag_lst) if tag == end_tag]

		assert len(start_lst) == len(end_lst)
		lst = zip(start_lst, end_lst)

		if verbose:
			print "Make sure we are getting the appropriate HTML sections"
		for sub_lst, next in bhp.get_text_list(lst):
			html = list2text(sub_lst, next)
			#print html
			assert html.startswith('<li class="g">')
			assert html.endswith('</li>')
			assert html[14:].find('<li class="g">') == -1


if __name__ == '__main__':
	BreakHtmlPage.test(verbose=True)
	print "Test Passed"

