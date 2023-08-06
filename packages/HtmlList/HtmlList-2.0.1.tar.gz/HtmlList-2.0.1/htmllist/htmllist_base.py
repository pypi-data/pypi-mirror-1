"""
Base class for HtmlList classes
"""

from break_html_page import BreakHtmlPage, list2text
from repeat_pattern import RepeatPattern
from utills import not_empty_iter

class HtmlList(object):
	""" This class breaks an HTML page that has some kind of list in it, to the
	list's elements. It has one method you use and one method you can overwrite.
	This class wrap the "pubilc" input and "public" output attributes of
	RepeatPattern and BreakHtmlPage
	"""
	def __init__(self, pattern_cls=None, break_cls=None):
		""" Optional Parameters:
		pattern_cls A RepeatPattern class. The default is the class from the
			repeat_pattern model, which implements the new algorithm.
		break_cls A BreakHtmlPage class. The default is the class from the
			break_html_page module. There is no good reason to replace it, and
			currently there is no other option.
			* BUT, break_cls can be also a BreakHtmlPage instance, then it will
			just use it (w/o creating a new object). This is useful if we want
			to use different algorithm on an already "broken" page.
		"""
		if not pattern_cls:
			pattern_cls = RepeatPattern
		if not break_cls:
			break_cls = BreakHtmlPage

		self._rp = pattern_cls()
		if isinstance(break_cls, BreakHtmlPage):
			self._bhp = break_cls
		else:
			self._bhp = break_cls()

	def __setattr__(self, name, value):
		""" Wrapper for RepeatPattern/BreakHtmlPage input attributes """
		if name in ("min_len", "min_repeat", "max_repeat", "max_stdv",
			"debug_level"):
			setattr(self._rp, name, value)
		elif name in ("element_good", ):
			setattr(self._bhp, name, value)
		else:
			self.__dict__[name] = value

	def __getattr__(self, name):
		""" Wrapper for RepeatPattern/BreakHtmlPage output attributes """
		if name in ("best_factor", "output_lst", "indices_lst", "repeats",
		"relevant_items"):
			return getattr(self._rp, name)
		elif name in ("exclude_tags", "include_tags"):
			return getattr(self._bhp, name)
		else:
			raise AttributeError("HtmlList has not attribute", name)

	@property
	def break_cls(self):
		""" The inner BreakHtmlPage instance,
		so we can pass it to a new HtmlListXXX class if we want to use different
		algorithm on the same text.
		"""
		return self._bhp

	def set_text(self, text):
		""" Break the HTML text and store it in the BreakHtmlPage object. """
		self._bhp.clear()
		self._bhp.feed(text)
		self._bhp.close()

	@not_empty_iter
	def get_html_list(self, lazy=False):
		""" Return a list of items from handle_sub_html.
		This method breaks the HTML text that was feed with set_text, to sub
		sections according to the inner structure of the page.
		Then it pass each HTML section to handle_sub_html and yield the result
		if it is not None.

		If lazy is True, RepeatPattern will work in "lazy" mode.

		The returned iterator will not be empty, it will return None if there
		are no sub HTML sections to return.
		"""
		tags = self._bhp.get_tag_list()
		if not tags: return
		indexes = self._rp.process(tags, lazy)
		if not indexes: return
		html_lst = self._bhp.get_text_list(indexes)
		for lst, next in html_lst:
			section = self.handle_sub_html(lst, next)
			if not section is None:
				yield section

	def handle_sub_html(self, lst, next):
		""" This method render the sub HTML of each section.
		You can extend it or overwrite it.

		lst is a list of HTML elements (html5lib.simpletree).
		next is the first element in the next section (or None)

		It can return None for the section to be ignored.
		"""
		return list2text(lst, next)

