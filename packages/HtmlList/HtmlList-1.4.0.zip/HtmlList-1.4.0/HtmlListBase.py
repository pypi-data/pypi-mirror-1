"""
Base class for HtmlList classes
"""

from BreakHtmlPageBS import BreakHtmlPage
from RepeatPattern import RepeatPattern

class HtmlListBase:
	"""
	This class breaks an HTML page that has some kind of list in it, to the list
	elements. It has one method you use and one method you need to overwrite.
	"""
	def __init__ (self):
		"""
		Set 'pattern_tags', 'structural_attrs' 'min_repeat', 'min_len',
		max_stdv_ptrn, max_stdv_indx and 'filter_func' to None.
		So BreakHtmlPage and RepeatPattern will use their default values.
		You can assign a values to these class members before calling Init.
			pattern_tags - A list of tag names to include in the pattern.
			structural_attrs - A list of attribute names not to ignore in the
				pattern.
			min_repeat - Minimum number of repeats of the pattern.
			min_len - Minimum number of tags in the pattern.
			max_stdv_ptrn - Maximum normalized standard deviation for distances
				between the patterns (see RepeatPattern).
			max_std_indx - Maximum normalized standard deviation of the
				distances between the returned indexes (see RepeatPattern).
			min_der2_factor - Complicate - see RepeatPattern.
			filter_func - A function that get a list and returns True if this
				list should be considered for a possible pattern.
				This function should test the *beginning* of the list for the
				pattern.
		"""
		self.pattern_tags = None
		self.structural_attrs = None
		self.min_repeat = None
		self.min_len = None
		self.max_stdv_ptrn = None
		self.max_stdv_indx = None
		self.min_der2_factor = None
		self.filter_func = None
		self._rp = RepeatPattern ()

	def Init (self, text = None, length = None):
		"""
		Initialize the RepeatPattern class. You have to call this function If
		you set one of the class members list in __init__.

		If 'text' is an HTML text, the class will process this text, and return
		the result list. If 'length' is given, it will return False if the \
		length of the list is not 'length'. If text is not given, the method
		will return None.

		Use this feature to initialize the RepeatPattern object by processing
		some text you know is "good". Then all calls to GetHtmlList will break
		the HTML by the same pattern.

		You may overwrite this method. it should call the base method and
		then run further test on the returned list (if not none), to make sure
		it is valid. It should return False on failure, None if no
		initialization data was given or the results list.

		The user need to make sure the returned value from this method is not
		False (but may be None). If so the initialization didn't work, and need
		to be done again with different data. In addition the user has to be
		certain the data she use for initialization is in the exact same format
		as the data she is going to parse.
		"""
		if self.min_repeat:
			self._rp.min_repeat = self.min_repeat
		if self.min_len:
			self._rp.min_len = self.min_len
		if self.max_stdv_ptrn:
			self._rp.max_stdv_ptrn = self.max_stdv_ptrn
		if self.max_stdv_indx:
			self._rp.max_stdv_indx = self.max_stdv_indx
		if self.min_der2_factor:
			self._rp.min_der2_factor = self.min_der2_factor
		if self.filter_func:
			self._rp.filter_func = self.filter_func
		## Try init page and test it ##
		if text:
			lst = self.GetHtmlList (text, lazy = False)
			if length and len (lst) != length: return False
			return lst



	def GetHtmlList (self, text, lazy = True, filter_algo = None):
		"""
		Get an HTML text and return a list of items from HandleSubHtml.
		This method breaks the HTML text to sub sections according to the inner
		structure of the page. Then it feed each HTML section to HandleSubHtml
		and add the result to a list. It returns this list.

		The lazy and filter_algo parameters, if given, is passed to
		RepeatPattern.DoAllAtOnce
		"""
		bhp = BreakHtmlPage ()
		if not self.pattern_tags is None:
			bhp.pattern_tags = self.pattern_tags
		if not self.structural_attrs is None:
			bhp.structural_attrs = self.structural_attrs
		bhp.Feed (text)
		bhp.Close ()

		#for tag in bhp.GetTagList ():
		#	print tag

		indexes = self._rp.DoAllAtOnce (bhp.GetTagList (), lazy, filter_algo)
		html_lst = bhp.GetTextForTagList (indexes)

		lst = []
		for sub_html in html_lst:
			lst.append (self.HandleSubHtml (sub_html))

		return lst

	def HandleSubHtml (self, sub_html):
		"""
		This method need to be overwrite. It raises NotImplemented exception.
		The method takes an HTML section and extract whatever information you
		need from it. You will get this information as a list from GetHtmlList.
		"""
		raise NotImplemented

	## Wrapper for RepeatPattern.FindFilter ##
	def FindFilter (self, look_ahead = 2, match_len = 2):
		return self._rp.FindFilter (look_ahead, match_len)

	## The two following methods initialize an object from another object ##
	def GetPattern (self):
		""" """
		return self._rp.GetPattern ()

	def SetPattern (self, lst):
		""" """
		self._rp.SetPattern (lst)

