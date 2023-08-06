"""
* This is the "old" repeat-pattern algorithm.

This module defines a class to find a repetitive pattern in a list.
The class takes the pattern that it's length double the number of
occurrences is the biggest. But it has some tools to put limitations on the
selected pattern.

Erez Bibi
"""

from repeat_pattern_base import RepeatPatternBase

class RepeatPattern(RepeatPatternBase):
	""" This class finds a repetitive pattern in a list. It will find a pattern
	such as the length of the pattern multiply by the number of occurrences
	multiply by some value of the pattern indices list  (see below) is the
	biggest possible.

	This class checks the normalized standard deviation in the first derivative
	list. This value should indicate a good candidate of real HTML pattern.

	The user can control the minimum length of the pattern, the minimum and
	maximum number of times the pattern repeat itself and the maximum normalized
	standard deviation of the gaps between the patterns.
	"""

	def _build_tree(self, lst, tree, lst_index):
		""" This is the inner recursive method to build suffix tree from a list.
		Each node in the tree is a three-tuple (tags, childes, indices).
			tags - A list of items from the input list.
			childes - A list of sub trees under this node.
			indices - A list of the indices (from the original input list) of
			the items that are represented by this node.
		"""
		if not lst: return tree		# Base case
		for j in range(len(tree[1])):		# Go over child trees
			# try to match the prefix of the list to insert.
			sub_lst, childs, indices = tree[1][j]
			if sub_lst[0] != lst[0]: continue	# No match here
			else:	# Look for the longest match
				index = 1
				while index < min(len(sub_lst), len(lst)):
					if sub_lst[index] != lst[index]: break
					index += 1
				if index < len(sub_lst): # Need to split sub_lst
					# We split the tags list so we also need to "push" the
					# indices list.
					sub2 = [sub_lst[index:], childs, map(
						lambda x: x + index, indices)]
					# And add the new index to the indices list.
					indices.append(lst_index)
					tree[1][j] = [sub_lst[:index], [sub2], indices]
				else:	# If there is no split, just add the index
					indices.append(lst_index)
				# Insert the rest of the list to the sub tree
				tree[1][j] = self._build_tree(
					lst[index:], tree[1][j], lst_index + index)
				return tree
		# We can't insert the list in an existing sub tree
		#	append to end as new sub-tree
		tree[1].append((lst, [], [lst_index]))	# TODO: use namedtuple in Py2.6
		return tree

	def _build_tree_main(self, lst):
		""" This method builds the suffix tree, you must call it before calling
		find_repeat_pattern. it creates the top most (empty) tree, and inserts
		all the lists suffixes.
		"""
		self._input_lst = lst
		self._tree = ([], [], [])
		for i in xrange(len(self._input_lst)):
			self._tree = self._build_tree(lst[i:], self._tree, i)
		if self.debug_level > 4:
			self.traverse_tree()
		return self._tree

	def _find_repeat_pattern(self, tree=None, cur_lst=None):
		""" This method finds the "best" repetitive pattern in the tree.
		In other words it finds a sequence of items, that it's length multiply
		by the number of repeats and by some factor of STDV, is the biggest.
		In addition, it will not return a pattens that are overlapping.

		When the function returns:
			self.best_factor Will hold the best pattern factor
			self.output_lst Will hold the best pattern
			self.indices_lst Will hold a list of two-tuples, the indices of the
				best pattern (start, end).
			self.repeats Will hold the number of occurrences of the best pattern

		This is also a recursive function. It return the best matched sequence.
		"""
		if not self._tree: return
		if tree is None: tree = self._tree
		if cur_lst is None:		# Init 'global' factor
			self.best_factor = 0
			cur_lst = []
		lst, childs, indices = tree
		cur_lst = cur_lst + list(lst)
		# First criteria - Length and Number of repeats
		if len(indices) >= self.min_repeat and (
		not self.max_repeat or len(indices) <= self.max_repeat) \
		and len(cur_lst) >= self.min_len:
			der = self._derivative(indices)
			stdv = self._nstdv(der)
			min_gap = min(der)
			if self.debug_level > 3:
				print "First criteria: Occurrences", len(indices), len(cur_lst)
			# Second Criteria - Pattern doesn't overlap and under STDV factor
			if min_gap >= len(cur_lst) and stdv <= self.max_stdv:
				factor = len(cur_lst) * len(indices) * (1 - stdv) * (1 - stdv)
				if self.debug_level > 2:
					print "Second Criteria: Gap, STDV", min_gap, stdv
				# Third criteria - Best match test
				if factor > self.best_factor:
					self.best_factor = factor
					self.output_lst = cur_lst
					# end index is end of this list, start is entire list back
					up = len(lst)
					down = len(cur_lst) - len(lst)
					self.indices_lst = [(i - down , i + up - 1) for i in indices]
					self.repeats = len(self.indices_lst)
					if self.debug_level > 1:
						print "Third criteria: Pattern Factor", cur_lst, factor
						print "Indices List:", self.indices_lst
		# Go down in the tree
		for sub_tree in childs:
			self._find_repeat_pattern(sub_tree, cur_lst)
		return self.output_lst

	def _get_indices_list(self, input_lst):
		""" This method returns a list of two-tuples (start, end) of the indices
		the chosen pattern (output-list class variable) occur in the input-list.
		It returns None if there is no pattern to work with.

		This implementation scans for the pattern in the input-list. This is a
		simple sub-sequence search. It is for working in "lazy" mod.
		The method will fill and return the indices_lst class variable.

		input_lst - The input-list to look for the pattern on..
		"""
		if not self.output_lst: return None	# There is no pattern.
		d = len(self.output_lst)
		n = len(input_lst)
		self.indices_lst = []
		self.repeats = 0
		i = 0
		while i < n - d:
			j = 0
			while j < d and input_lst[i+j] == self.output_lst[j]:
				j += 1
			if j == d:		# Fond an occurrence
				self.indices_lst.append((i, i+d))
				i += d
				self.repeats += 1
			else: i += 1
		return self.indices_lst

	## Public Stuff ##

	@property
	def relevant_items(self):
		""" For compatibility with other algorithms. """
		return None

	def traverse_tree(self, tree=None, level=0, index_filter=None):
		""" This is only for debugging - Prints the tree.
		"""
		if not self._tree: return
		if tree is None: tree = self._tree
		lst, childs, indices = tree
		if not index_filter or (indices and indices[0] in index_filter):
			print '>', '  ' * level, lst, '-', indices
		for sub_tree in childs:
			self.traverse_tree(sub_tree, level + 1, index_filter)

	def process(self, input_lst, lazy=False):
		""" Find the best pattern in a list of items (see module documentation
		for more details).
		Returns a list of tow-tuple indices (start, end) of the indices of the
		best pattern, or None if there is no "best" pattern.
		"""
		if lazy and self.output_lst:
			self._tree = None
			return self._get_indices_list(input_lst)
		self._build_tree_main(input_lst)
		#self.traverse_tree(index_filter=[...])
		self._find_repeat_pattern()
		if self.debug_level > 0:
			print "Best Pattern (Factor):", self.output_lst, self.best_factor
			print "Indices List:", self.indices_lst
		return self.indices_lst

	## Testing ##

	@classmethod
	def test(cls, verbose=0):
		""" Tests for this class """
		rp = cls(debug_level=verbose)
		rp.min_repeat = 2
		list1 = list('XYZXYZABCABCABCXYZ')	# ABC better then XYZ
		list2 = list('ABCAYBCAXBC')			# Cannot take ABC take BC
		list3 = list('YXNMLAXBCAYBCAXYBCAYXBCABCVBNXY')	# In lazy mode take BC again

		if verbose: print list1
		lst = rp.process(list1, lazy=False)
		assert rp.output_lst == ['A', 'B', 'C'], rp.output_lst
		assert lst == [(6,8), (9,11), (12,14)], lst
		if verbose: print "----------------------------------------------"

		if verbose: print list2
		lst = rp.process(list2, lazy=False)
		assert rp.output_lst == ['B', 'C'], rp.output_lst
		assert lst == [(1,2), (5,6), (9,10)], lst
		if verbose: print "----------------------------------------------"

		if verbose: print list3
		lst = rp.process(list3, lazy=True)
		assert rp.output_lst == ['B', 'C']
		assert lst == [(7, 9), (11, 13), (16, 18), (21, 23), (24, 26)], lst
		if verbose: print "----------------------------------------------"

if __name__ == '__main__':
	RepeatPattern.test(4)
	print "Test Passed"


