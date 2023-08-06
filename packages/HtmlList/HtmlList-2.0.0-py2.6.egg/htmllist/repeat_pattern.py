"""
Another way to find the repetitive pattern - This is the "new" algorithm.

This algorithm is based on the heuristic assumption that the pattern we are
looking for will have some items (tags) that will appear only in it. It is not
true for the mathematical representation of the problem, but will be true in
many real world case (HTML pages)

1. count the number of occurrences for each item and build an indices list
2. sort by number of occurrences (keep original order when possible)
3. group by counter (put in "buckets") - consider also different sequences
	within the same counter value*
4. find the best bucket (bucket factor is higher)
5. try to expand the bucket as much as possible (see _expand_bucket)

* For each item we are keeping a list of indices.
We should group items by the length of the indices list (number of occurrences)
BUT every such group (bucket) should only hold items that their indices form a
repetitive sequence. So each index of a new item in a bucket should be bigger
then the last items index but smaller then the next index of the first item.
In other words, there may be more then one bucket for each number of occurrences
value.

Important to note: I always keep the original order of the items. In every
sub-items list, the order of the items will be as it is in the original input
list (first occurrence of the item). Also, every indices list will be sorted
that way.

Erez Bibi
2009-11-6
"""

from collections import defaultdict

from repeat_pattern_base import RepeatPatternBase

class RepeatPattern(RepeatPatternBase):
	"""
	See module documentation
	"""

	## Debugging Methods ##

	def _print_dict(self, name, dic):
		print name, ':'
		for key, val in dic.iteritems():
			print '\t', key, ':', val

	def _print_list(self, name, lst):
		print name, ':'
		for itm in lst:
			print '\t', itm

	def _print_pattern(self, name):
		self._print_list("%s (factor=%s repeats=%s)" % (
			name, round(self.best_factor), self.repeats), self.output_lst)

	## Buckets help methods ##

	def _bucket_factor(self, repeats, items):
		""" Calculate a factor for each bucket.
		repeats - The number of occurrences of the pattern in the list.
		items - A list of the items in the pattern.

		"stdv" is a normalized standard deviation of the distances between the
		indices of the pattern.

		Return 0 if the bucket should not be considered
		"""
		# I apply these limits in _put_in_buckets
		#if repeats < self.min_repeat: return 0
		#if self.max_repeats and repeats > self.max_repeat: return 0
		if len(items) < self.min_len: return 0
		stdv = self._nstdv(self._derivative(self._items_dict[items[0]]))
		if stdv > self.max_stdv: return 0
		return repeats * len (items) * (1 - stdv) * (1 - stdv)

	def _is_in_bucket(self, item, bucket):
		""" Check if an item indices list belong to the sequence that exists in
		this bucket. The new indices list must be after the last one, but before
		the next index of the first list.
		"""
		first_indices = self._items_dict[bucket[0]]
		last_indices = self._items_dict[bucket[-1]]
		new_indices = self._items_dict[item]
		length = len(first_indices)	# all lists are the same length
		# Make sure all new items are in appropriate places,
		# last item is special case
		return all([new_indices[i] > last_indices[i] and \
			(i == length - 1 or new_indices[i] < first_indices[i+1]) \
			for i in range(length)])

	## Expanding methods ##

	def _is_all_same(self, lst):
		""" Return True if all the items in the list are the same """
		return all([lst[0] == itm for itm in lst[1:]])

	def _expand_bucket(self):
		""" This method will try to expand the chosen bucket (self.indices_lst)
		as much a possible, this is a list of two-tuple (start, end) of indices.
		It looks first at all the items before every occurrence, if they all the
		same it adds this item to the pattern. Then it works on the items after
		every occurrence, and so on until it cannot expand anymore from both
		sides.
		Returns the number of new items it manage to add to the pattern
		"""
		# TODO: It might be better (but way more complicated) to expand only
		# specific tags, or in other words, ignore certain tags.
		length = len(self.indices_lst)
		# The minimum gap between occurrences, this is the maximum we can expand
		min_gap = min([self.indices_lst[i+1][0] - self.indices_lst[i][1] - 1 \
			for i in range(length - 1)])

		new_items = 0
		before_ok = after_ok = True
		while new_items < min_gap and (before_ok or after_ok):
			# Try to find common item BEFORE the pattern
			if before_ok and self.indices_lst[0][0] > 0:
				items = [self._input_lst[i - 1] for i,_ in self.indices_lst]
				if self._is_all_same(items):
					# Found new item
					new_items += 1
					# Expand the indices list
					self.indices_lst = [(s-1,e) for s,e in self.indices_lst]
					# Add the item to the beginning of the pattern
					self.output_lst = [items[0]] + self.output_lst
				else: before_ok = False		# Done expanding before the pattern
			else: before_ok = False
			# Try to find common item AFTER the pattern
			if after_ok and self.indices_lst[-1][1] < len(self._input_lst):
				items = [self._input_lst[i + 1] for _,i in self.indices_lst]
				if self._is_all_same(items):
					new_items += 1
					self.indices_lst = [(s,e+1) for s,e in self.indices_lst]
					self.output_lst.append(items[0])
				else: after_ok = False		# Done expanding after the pattern
			else: after_ok = False
		# If we managed to expand - calculate the new factor
		if new_items > 0:
			self.best_factor = self._bucket_factor(
				self.repeats, self.output_lst)
		return new_items

	## First level private methods ##

	def _group_items(self):
		""" Create an indices list for each item in the input list. """
		for index, item in enumerate(self._input_lst):
			self._items_dict[item].append(index)
		if self.debug_level > 3: self._print_dict("Items:", self._items_dict)
		return self._items_dict

	def _put_in_buckets(self):
		""" Distribute the items to buckets according to the number of
		occurrences. There is a second level of distribution (to buckets) by
		different "sequences" in the same first level bucket. A sequence is
		created by items that appear one after the other in the same order.
		"""
		item_indices = self._items_dict.items()
		# Here I filter out indices list that are too short
		item_indices = filter(lambda x: len(x[1]) >= self.min_repeat and (
			not self.max_repeat or len(x[1]) <= self.max_repeat), item_indices)
		# First level of distribution to buckets is by length of indices list
		# I also sort by the first index to preserve the original order in each
		# bucket
		item_indices.sort(key = lambda x: (len(x[1]), x[1][0]))
		# Put items in the buckets and create the second level of distribution
		for item, indices in item_indices:
			new_bucket = True
			for bucket in self._buckets_dict[len(indices)]:
				if self._is_in_bucket(item, bucket):
					bucket.append(item)
					new_bucket = False
					break
			if new_bucket:	# Create new bucket with it's first item
				self._buckets_dict[len(indices)].append([item])
		if self.debug_level > 2: self._print_dict("Backets", self._buckets_dict)
		return self._buckets_dict

	def _find_best_bucket(self):
		""" Find the best bucket, or in other words the best pattern in the
		input list. A bucket is a list of items that repeat same number of times
		and creates a sequence.
		After this method returns:
			self.best_factor Will hold the best bucket factor
			self.output_lst Will hold the best pattern
			self.indices_lst Will hold a list of two-tuple indices of the best
				pattern (start, end).
			self.repeats Will hold the number of occurrences of the best pattern
		After finding the best bucket it tries to expand it.
		"""
		# Flatten the list of buckets (dict of lists), and get the factor and
		# length for each one
		lst = [(length, items, self._bucket_factor(length, items)) for \
			length, bucket in self._buckets_dict.iteritems() for items in bucket]
		if self.debug_level > 4: self._print_list("Pre-Factors", lst)
		# factor 0 is for bucket that should be drooped
		lst = filter(lambda x: x[2] > 0, lst)
		if not lst: return None		# We didn't find a pattern
		if self.debug_level > 1: self._print_list("Factors", lst)
		# Get the best bucket by it's factor
		self.repeats, self.output_lst, self.best_factor = max(
			lst, key = lambda x: x[2])
		# Get the indices list of this bucket (first, last)
		self.indices_lst = zip(self._items_dict[self.output_lst[0]],
			self._items_dict[self.output_lst[-1]])
		if self.debug_level > 0: self._print_pattern("Best")
		# See if we can expand the selected pattern
		if self.repeats > 1 and self._expand_bucket():
			if self.debug_level > 0: self._print_pattern("Expanded")
		return self.best_factor

	def _get_indices_list(self, input_lst):
		""" This method returns a list of two-tuples (start, end) of the indices
		the chosen pattern (output-list class variable) occur in the input-list.
		It returns None if there is no pattern to work with.

		It is for working in "lazy" mode, it scans the input list for the
		pattern, while considering item that are not in the pattern in between.

		input_lst - The input-list to look for the pattern on.
		"""
		if not self.output_lst: return None		# There is no pattern.
		d = len(self.output_lst)
		n = len(input_lst)
		self.indices_lst = []
		self.repeats = 0
		pattern_set = set(self.output_lst)		# For quick search
		i = j = 0		# i - input list index, j - pattern index
		while i < n:
			if input_lst[i] == self.output_lst[j]:	# One item match
				if j == 0: 							# This is the first item
					start = i
				j += 1
			elif input_lst[i] in pattern_set:		# Need to start over
				if input_lst[i] == self.output_lst[0]:
					start = i
					j = 1
				else:
					j = 0
			i += 1
			if j == d:		# Found one
				self.indices_lst.append((start, i-1))
				self.repeats += 1
				j = 0
		return self.indices_lst

	## Public Methods ##

	@property
	def relevant_items(self):
		""" A list of items that might be useful to other algorithms
		"""
		if not hasattr(self, "_buckets_dict"): return None
		return (item for bucket in self._buckets_dict.itervalues() \
			for items in bucket for item in items)


	def process(self, input_lst, lazy=False):
		""" Find the best pattern in a list of items (see module documentation
		for more details).
		Returns a list of tow-tuple indices (start, end) of the indices of the
		best pattern, or None if there is no "best" pattern.

		In lazy mode I just scan the input-list for the pattern occurrences that
		was found in an early run.
		"""
		if lazy and self.output_lst:
			return self._get_indices_list(input_lst)

		self._input_lst = input_lst
		self._items_dict = defaultdict(list)	# Dictionary of item: indices
		self._buckets_dict = defaultdict(list)
		# These are "public" output variables
		self.output_lst = None
		self.best_factor = None
		self.indices_lst = None
		self.repeats = None
		# Here I'm doing the work
		self._group_items()
		self._put_in_buckets()
		if not self._buckets_dict: return None
		self._find_best_bucket()
		return self.indices_lst

	## Testing ##

	@classmethod
	def test(cls, verbose=0):
		""" Tests for this class """
		rp = cls(debug_level=verbose)
		rp.min_repeat = 2
		list1 = list('XYKaLbKcLdKeLXY')	# "KL" is better then "XY"
		list2 = list('gibrishAXBCAYBCAXYBCAYXBCABChsirbig')	# "ABC" drop X and Y
		list3 = list2 + ['B']				# This will drop also the B
		list4 = list('ABCDEFGHIJKLMNOP')	# No pattern
		list5 = list('babaaXYbaXYbaXYbabab')# Expandable pattern
		list6 = list('xAyBCxAyAByCxAyCABC')	# Test lazy mode

		if verbose: print list1
		lst = rp.process(list1)
		assert lst == [(2,4), (6,8), (10,12)], lst
		assert rp.output_lst == ['K', 'L'], rp.output_lst
		#assert rp.best_factor == 6, rp.best_factor	# Equal distances between items
		if verbose: print "----------------------------------------------"

		if verbose: print list2
		lst = rp.process(list2)
		assert rp.output_lst == ['A', 'B', 'C'], rp.output_lst
		# Distances between items are not equal
		#assert rp.best_factor < len (rp.output_lst) * rp.repeats
		if verbose: print "----------------------------------------------"

		if verbose: print list3
		lst = rp.process(list3)
		assert rp.output_lst == ['A', 'C'], rp.output_lst
		if verbose: print "----------------------------------------------"

		if verbose: print list4
		lst = rp.process(list4)
		assert lst is None, lst
		rp.min_repeat = 1	# with no limit on number of repeats there is a much
		assert rp.process(list4)
		assert rp.repeats == 1, rp.repeats
		if verbose: print "----------------------------------------------"
		rp.min_repeat = 2

		if verbose: print list5
		# Expandable - Should add 'a' before and 'b' after the pattern
		lst = rp.process(list5)
		assert rp.output_lst == ['a', 'X', 'Y', 'b'], rp.output_lst
		if verbose: print "----------------------------------------------"

		if verbose: print list6
		rp.set_pattern(['A', 'B', 'C'])
		lst = rp.process(list6, lazy=True)
		assert rp.output_lst == ['A', 'B', 'C'], rp.output_lst
		assert rp.indices_lst == [(1,4), (8,11), (16,18)], rp.indices_lst


if __name__ == '__main__':
	RepeatPattern.test(4)
	print "Test Passed"



