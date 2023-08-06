"""
This module define a few classes that simplify the dealing with HTML tags.
BreakHtmlPage uses them, and it is decoupled from the 3rd party tool that
BreakHtmlPage use to parse the HTML text.
"""

# This is not likely to change, and there is not a n easy interface to change it.
FORMAT_ATTRIBUTES = "class", "style", "type", # "width"

class Tag(object):
	"""
	Represent a simple HTML tag with optional formating attributes.
	I calculate the hash value in advance, for efficiency.
	I need this class to easily compare tags with each other.
	These are the "items" RepeatPattern uses.
	"""
	def __init__(self, name, attrs=None):
		__slots__ = "_name", "_attrs", "_hash"
		self._name = name
		if attrs:
			self._attrs = [(name, val) for name, val in attrs.iteritems() if \
				 name in FORMAT_ATTRIBUTES]
		else: self._attrs = None
		self._hash = hash(repr(self))

	def __repr__(self):
		""" Print for debugging """
		if self._attrs:
			attrs = ' ' + ','.join(['%s="%s"' % (name, val) for \
				name, val in self._attrs
			])
		else: attrs = ''
		return "<%s%s>" % (self._name, attrs)

	def __hash__(self):
		return self._hash

	def __cmp__(self, other):
		return cmp(self._hash, other._hash)

	def tag_name(self):
		""" Return the tag name. I need it for the TagSet class. """
		return self._name

class TagSet(object):
	""" This class holds two sets, one of Tags, and one of strings.
	The class implement the __contains__ operator. The item to test is always a
	Tag, it checks the tags set first, if it is not there, it checks if the Tag
	name is in the strings set.

	The class also have a += operator. It adds elements to both sets like
	'update'. One can add a Tags or a string or tuples/lists/sets of Tags and
	strings.
	"""
	def __init__(self):
		""" """
		self._set_tags = set()
		self._set_strs = set()

	def __iadd__(self, other):
		""" Add Tags or strings or sequence of Tags and strings """
		if not other: return self
		if type(other).__name__ not in ("set", "list", "tuple", "generator"):
			other = [other]
		tags = []
		strs = []
		for item in other:
			if isinstance(item, Tag):
				tags.append(item)
			else:
				strs.append(str(item))
		self._set_tags.update(tags)
		self._set_strs.update(strs)
		return self

	def __contains__(self, item):
		""" Check if an item is in one of the sets. 'item' will always be a Tag
		object. Checks first if an identical Tag object is in the tags set. If
		not, checks if the Tag name is in the strings set.
		"""
		if not isinstance(item, Tag):
			raise TypeError("'item' has to be a Tag")
		return item in self._set_tags or item.tag_name() in self._set_strs

	def __len__(self):
		""" The length of both sets """
		return len(self._set_tags) + len(self._set_strs)

	def __repr__(self):
		""" For debugging mainly """
		return "Tags: %s\nStrings: %s" % (self._set_tags, self._set_strs)

	def clear(self):
		""" Clear both sets """
		self._set_tags.clear()
		self._set_strs.clear()

	@classmethod
	def test(cls, verbose=False):
		""" Testing of both classes """
		ts = cls()

		ts += "aaa"
		ts += "aaa", "bbb"
		ts += ["aaa", "bbb", "ccc"]
		ts += set(("ccc", "ddd"))
		ts += Tag("aaa")
		ts += Tag("eee"), Tag("fff", {"class": "foo"})

		if verbose:
			print ts

		assert Tag("aaa") in ts
		assert Tag("ccc", {"type": "foo"}) in ts
		assert Tag("eee") in ts
		assert Tag("eee", {"class": "bar"}) not in ts
		assert Tag("fff", {"class": "foo"}) in ts
		assert Tag("fff", {"class": "bar"}) not in ts


if __name__ == '__main__':
	TagSet.test(verbose=True)
	print "Test Passed"

