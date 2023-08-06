"""
This module defines a class to find a repetitive pattern in a list.
The class take the pattern that the length of it double the number of occurrences
is the biggest. But it has some tools to put limitations on the selected pattern.

Erez Bibi
"""

import math

class RepeatPattern:
	"""
	This class finds a repetitive pattern in a list. It will find a pattern such
	as the length of the pattern multiply by the number of occurrences is the
	biggest possible.

	The user can control the minimum length of the pattern, the minimum number of
	times the pattern repeat itself, the maximum normalized standard deviation of
	the gaps between the patterns, and the type of the pattern (see __init__).

	This class looks at some properties of the first and second district
	derivative lists of the original occurrences list. It check the minimum and
	maximum first derivative values. The normalized standard deviation in the
	first derivative list. And the number of consecutive zeros in the second
	derivative list. These values should indicate a good candidate of real HTML
	pattern. All this data and the length and number of occurrences it the class
	factors into one value. This value will determent the best pattern.
	"""
	def __init__ (self,
		min_len = 1,
		min_repeat = 2,
		max_stdv_ptrn = 1,
		max_stdv_indx = 1,
		min_der2_factor = 0,
		filter_func = lambda lst: True):
		"""
		min_len - Optional minimum length of the output pattern (sub-list),
			default = 1
		min_repeat - Optional minimum time the pattern should repeat in the list,
			default = 2.
			Note: min_repeat must be more then one!
		max_stdv_ptrn - Optional Maximum normalized standard deviation of the
			distances between occurrences. This is a number between 0 and 1.
			0 means that the occurrences are in sequence (no other tags in
			between). 1 means that there is no importance to the position of the
			occurrences in the page. In a normal HTML page you should keep this
			number low, but maybe bigger than zero. The default is one.
		max_stdv_indx - Optional maximum normalized standard deviation of
			the distances between the returned occurrences. This has the same
			restrictions as "max_stdv_ptrn" but to be effective it must be less
			then "max_stdv_ptrn". When the system picks occurrences of the
			pattern in the HTML page, it will pick the indexes so the STDV of
			the list will be less then this value. This is specially important
			when you use the initialization feature.
			The default is one - no effect.
		min_der2_factor - Optional, The second derivative factor indicates how
			many  consecutive occurrences of the pattern are in constant
			distance from each other. This is the number of consecutive zeros in
			the second derivative on the occurrences list, divide by the length
			of the second derivative list. This is a number between 0 and 1. The
			default is zero.
		filter_func - Optional function that get a sub-list and returns True if this
			sub-list should be considered for a possible output pattern.
			Default is the True function - no filtering.
			This function should test the *beginning* of the list for the
			pattern.
			Note: Each item in the list is tow-tuple (tag-name, tag-attrs)
			** This function is not in use.

		* These parameters can be also be controlled by changing class members
		with the same names.
		"""
		self.min_len = min_len
		self.min_repeat = min_repeat
		self.max_stdv_ptrn = max_stdv_ptrn
		self.max_stdv_indx = max_stdv_indx
		self.min_der2_factor = min_der2_factor
		self.filter_func = filter_func

		self._trie = None
		self._lst_len = 0
		self._output_lst = []
		self._indexes_lst = None

	############################################################################

	def __GetGapsInfo (self, lst):
		"""
		This method returns the minimum, maximum, normalized standard
		deviation of the gaps between the indexes of "lst" (first derivative),
		and the number of consecutive zeros in the second derivative divide by
		the length of the second derivative list.
		"""
		gaps = self.__Derivative (lst)		# First derivative
		if not gaps: return 0, 0, 0, 0
		min_val = min (gaps)
		max_val = max (gaps)
		stdv = self.__NStdv (gaps)
		sec_gaps = self.__Derivative (gaps)	# Second derivative
		con_zeros = len ([i for i in range (len (sec_gaps) - 1) if \
			sec_gaps[i] == 0 and sec_gaps[i+1] == 0])
		if len (sec_gaps):
			sec_derivative_factor = float (con_zeros) / len (sec_gaps)
		else:
			sec_derivative_factor = 1

		#print "---", con_zeros, len (sec_gaps), sec_derivative_factor, stdv
		return min_val, max_val, stdv, sec_derivative_factor

	def __NStdv (self, lst):
		"""
		This method calculates some kind of normalized standard deviation on a
		list of numbers. It calculates a regular standard deviation and then
		divide it by the total length of the list of tags we are working on
		(this is a class member), the result should be equal or bigger than zero
		but less than one.
		"""
		if self._lst_len == 0: return 1
		length = len (lst)
		avg = float (sum (lst)) / length
		sqr_sum = float (sum (map (lambda x: x*x, lst)))
		return (math.sqrt ((sqr_sum / length) - (avg * avg))) / self._lst_len


	def __Derivative (self, lst, order = 1):
		"""
		This function preform discrete derive on a list of numbers. This is the
		list of gaps between the numbers of the list.
		order - the derive order
		Returns a list of numbers or an empty list
		"""
		while order:
			if len (lst) < 2: return []
			lst = [abs (lst[i+1] - lst[i]) for i in range (len (lst) - 1)]
			order -= 1
		return lst

	def __FilterOutOnStdv (self, lst, max_stdv):
		"""
		This method filters out items in a list, that makes the total STDV of
		the list to be more then "max_stdv".

		It break the list in the place the distance between indexes is the
		bigger, and works recursively on the two new lists. That until it get
		to the longer sub list with STDV under the maximum.

		lst - A list of sorted indexes (in the list of tags we are working with)

		max_stdv - The maximum the normalized standard deviation of the
		distances between the indexes in "lst" can be

		Returns a new list of indexes
		"""
		if len (lst) < 3: return lst	# First base case
		min_val, max_val, stdv, tmp = self.__GetGapsInfo (lst)
		#print lst, stdv
		if stdv <= max_stdv: return lst	# Second base case
		for i in range (len (lst) - 1):
			if max_val == lst[i+1] - lst[i]:
				lst1 = self.__FilterOutOnStdv (lst[:i], max_stdv)
				lst2 = self.__FilterOutOnStdv (lst[i+1:], max_stdv)
				if len (lst1) > len (lst2): return lst1
				return lst2
		return lst	# Will not get here

	############################################################################

	def __FindFilter (self, trie, look_ahead, match_len):
		"""
		This is the recursive method of FindFilter. It traverse the trie and
		find the best filter for each level. it combined the filters as it goes
		up the tree.
		When it tries to filter upper levels, it look at the already filtered
		data below (taking the best filter until now), and keep adding to the
		filter.
		Returns: set (the filter), list (the filtered data until now)
		"""
		lst, childs, indexes = trie
		if not childs: return set(), []			# Base case
		# Gather filter results from all childes
		best_filter = set ()
		new_lsts = []
		for sub_trie in childs:
			filters, res_lsts = self.__FindFilter (sub_trie, look_ahead, match_len)
			best_filter |= filters	# Add the filters from this child
			for lst in res_lsts:	# Append this level list to the filtered results lists
				new_lsts.append (sub_trie[0] + lst)	# sut_trie[0] is the list from this level
		if not new_lsts:			# This is another base case: start with childes lists
			new_lsts = [sub[0] for sub in childs]
		# Add the filters for this level and return the filtered lists
		this_filter, this_lsts, tmp = \
			self.__FindInterfereItems (new_lsts, look_ahead, match_len)
		return this_filter | best_filter, this_lsts

	def __FindFilter2 (self, trie, look_ahead, match_len):
		"""
		This another algorithm for FindFilter. It traverse the trie and
		find the best filter for the entire trie. This method require iterative
		usage of FindFilter until we find all possible filters.
		Returns: set (the filter), factor (the best matching factor until now)
		"""
		lst, childs, indexes = trie
		if not childs: return None, 0			# Base case
		best_filter = None
		best_value = 0
		for sub_trie in childs:
			fltr, value = self.__FindFilter2 (sub_trie, look_ahead, match_len)
			if value > best_value:
				best_value = value
				best_filter = fltr
		lsts = [sub[0] for sub in childs]
		fltr, tmp, value = self.__FindInterfereItems (lsts, look_ahead, match_len)
		if value > best_value:
			best_value = value
			best_filter = fltr
		return best_filter, best_value

	def __FindInterfereItems (self, lsts, look_ahead, match_len):
		"""
		This method gets a list of lists and a "look-ahead" value.
		It tries to see if in the range of the look-ahead it can filter out some
		items so there will be good match between the lists.
		It returns the best filter (set) it can finds, so the match area will
		be the biggest.
		There is a condition that one list will not be filtered though, or all
		other lists should be filtered to try to match one unfiltered list.
		It also returns the new lists after filtering and the best matching factor.
		Return: set, list, factor
		"""
		if not lsts or len (lsts) < 2: return set(), lsts, 0	# Not enough data
		opt_filters = set ()	# All optional filters
		for lst in lsts:
			for itm in lst[:min (look_ahead, len (lst))]:
				opt_filters.add (itm)
		# Initial data
		result_filters = set ()
		best_result = 0
		new_lsts = lsts					# Start with the lists unchanged
		for i in range (len (lsts)):	# Go over all lists
			if not lsts[i]: continue
			# Cannot filters items that are in the range of this list
			filters = opt_filters - set (lsts[i][:min (look_ahead, len (lst))])
			# Build new filtered lists
			res_lsts = [lsts[i]]		# Start with this list unfiltered
			for j in range (len (lsts)):
				if i == j: continue				# This is the base list
				if len (lsts[j]) < look_ahead:	# Filter from the first look_ahead items
					tmp_lst = filter (lambda x: x not in filters, lsts[j])
				else:
					tmp_lst = filter (lambda x: x not in filters,
						lsts[j][:look_ahead]) + lsts[j][look_ahead:]
				res_lsts.append (tmp_lst)
			# Find matched results for the new filtered lists
			index = 0
			result = 0
			good = True
			while good:		# Go over all new lists "vertically"
				if index == len (res_lsts[0]): break	# res_lsts[0] is the "base" list
				for k in range (1, len (res_lsts)):
					if index == len (res_lsts[k]) or \
					res_lsts[0][index] != res_lsts[k][index]:
						good = False	# No match here
						break
				if not good: break
				# We had a match on all lists
				result += len (res_lsts)
				index += 1
			# See if this is the best filter
			if index >= match_len and result > best_result:
				best_result = result
				result_filters = filters
				new_lsts = res_lsts
		#if result_filters:
		#	print ">>>", best_result, result_filters
		#	for lst in lsts:
		#		print ">>>>", lst
		#	for lst in new_lsts:
		#		print "<<<<", lst
		#	print "----------------------------"
		return result_filters, new_lsts, best_result

	############################################################################

	def __BuildSuffixTrie (self, lst, trie, lst_index):
		"""
		This is the "inner" recursive function to build suffix tree from a list.
		Each node in the tree is a three-tuple (tags, childes, indexes).
			tags - A list of items from the input list.
			childes - A list of sub tries under this node.
			indexes - A list of the indexes (from the original input list) of
			the items that are represented by this node.
		"""
		if not lst: return trie		# Base case
		for j in range (len (trie[1])):		# Go over child tries
			# try to match the prefix of the list to insert.
			sub_lst, childs, indexes = trie[1][j]
			if sub_lst[0] != lst[0]: continue	# No match here
			else:	# Look for the longest match
				index = 1
				while index < min (len (sub_lst), len (lst)):
					if sub_lst[index] != lst[index]: break
					index += 1
				if index < len (sub_lst): # Need to split sub_lst
					# We split the tags list so we also need to "push" the indexes list.
					sub2 = [sub_lst[index:], childs, map (lambda x: x + index, indexes)]
					indexes.append (lst_index)	# And add the new index to the indexes list.
					trie[1][j] = [sub_lst[:index], [sub2], indexes]
				else: indexes.append (lst_index)	# If there is no split, just add the index
				# Insert the rest of the list to the sub trie
				trie[1][j] = self.__BuildSuffixTrie (lst[index:], trie[1][j], lst_index + index)
				return trie
		# We can't insert the list in an existing sub trie
		#	append to end as new sub-trie
		trie[1].append ([lst, [], [lst_index]])
		return trie

	############################################################################

	def BuildSuffixTrie (self, lst):
		"""
		This function builds the suffix trie, you must call it before calling
		FindRepeatPattern. it creates the top most (empty) trie, and insert all
		the lists suffixes that conform to the filter_func function.
		"""
		self._lst_len = len (lst)
		self._trie = [[], [], []]
		self._output_lst = []
		for i in range (self._lst_len):
			if not self.filter_func (lst[i:]): continue
			self._trie = self.__BuildSuffixTrie (lst[i:], self._trie, i)
		return self._trie

	def TraverseTrie (self, trie = None, level = 0):
		"""
		This is only for debug - Prints the trie.
		"""
		if not self._trie: return
		if trie is None: trie = self._trie
		lst, childs, indexes = trie
		print '>', '  ' * level, lst, '-', indexes
		for sub_trie in childs:
			self.TraverseTrie (sub_trie, level + 1)

	def FindRepeatPattern (self, trie = None, cur_lst = None):
		"""
		This function finds the "best" repetitive pattern in the trie.
		In other words it finds a sequence of items, that it's length multiply
		by the number of repeats, by inverse on the STDV, and by some factor on
		the second derivative list, is the biggest. (complicate...)

		In addition, it test that the distances between the patterns (first
		derivative) is within some limit (this is the STDV, see __init__), and
		it will not return a patten that is overlapping.

		When the function returns:
			self._best_factor Will hold the best pattern factor
				(length * repeats / STDV)
			self._output_lst Will hold the best pattern
			self._indexes_lst Will hold the indexes of the best pattern ends.

		This is also a recursive function. It return the best matched sequence.
		"""
		if not self._trie: return
		if trie is None: trie = self._trie
		if cur_lst is None:		# Init 'global' factor
			self._best_factor = 0
			cur_lst = []
		lst, childs, indexes = trie
		cur_lst = cur_lst + lst
		# First criteria - Length and Number of repeats
		if len (indexes) >= self.min_repeat and len (cur_lst) >= self.min_len:
			min_gap, max_gap, stdv, der2_factor = self.__GetGapsInfo (indexes)
			# Second Criteria - Pattern doesn't overlap and under STDV maximum and...
			if min_gap >= len (cur_lst) and stdv <= self.max_stdv_ptrn and \
				der2_factor >= self.min_der2_factor:
				factor = len (cur_lst) * len (indexes) * der2_factor * (1 - stdv)
				#print '>>>', min_gap, max_gap, len (cur_lst), len (indexes), der2_factor, stdv
				#print '>>> >>>', factor
				#print cur_lst
				# Third criteria - Best match test
				if factor > self._best_factor:
					self._best_factor = factor
					self._output_lst = cur_lst
					self._indexes_lst = map (lambda x: x + len (lst), indexes)
		# Go down in the tree
		for sub_trie in childs:
			self.FindRepeatPattern (sub_trie, cur_lst)
		return self._output_lst

	def GetIndexesList (self, lst = None):
		"""
		This function returns a list of two-tuples (start, end) of the indexes
		the best pattern occur in the input list.

		The function can works in two modes:
		1 - After we did the entire process of building the suffix tree and
		looking for the best pattern, we already have the indexes of where the
		pattern ends, and only need the starting places.
		2 - If working in "lazy" mode, we have the new input list, and the best
		pattern, but not the indexes list. In this case we need to find all the
		places that the pattern occur in the input list.
		* I do it using the brute-force algorithm, I can use a better algorithm
		but I'm not sure it will improve running time by much.
		"""
		if not self._output_lst: return []
		if not self._indexes_lst and not lst: return None
		d = len (self._output_lst)
		if not self._indexes_lst:
			# Find indexes in lazy mode
			self._indexes_lst = []
			n = len (lst)
			i = 0
			while i < n - d:
				j = 0
				while j < d and lst[i+j] == self._output_lst[j]: j += 1
				if j == d:
					i += d
					self._indexes_lst.append (i)
				else: i += 1
		return [(i - d, i) for i in self.__FilterOutOnStdv (
			self._indexes_lst, self.max_stdv_indx)]


	def DoAllAtOnce (self, lst, lazy = True, filter_algo = None):
		"""
		This method runs the BuildSuffixTrie - FindRepeatPattern - GetIndexesList
		cycle in one call. The advantage of this method is when parsing the same
		type of text multiple times with the same instance.

		If the 'lazy' variable is set to True, and the instance already analyze
		a text (list) once, it will just return the output pattern again. That
		is based on the assumption that the output pattern will be exactly the
		same, if the texts are with the same format.

		If the filter_algo is given, it uses the class filtering feature. BUT
		this feature doesn't work well yet, so don't use it!

		So when working with one instance of this class to process multiple
		texts from one source, we only need to build the suffix trie once. It
		will also help in the case of following results that don't have enough
		data to find the output pattern (like search engine result page with
		only one result). We can go even farther and 'initilaize' the instance
		once by processing a dummy text we know is 'good', and then doing the
		real work using this method in a 'lazy' mode.
		"""
		if lazy and self._output_lst:
			self._indexes_lst = None			# Reset Indexes
			return self.GetIndexesList (lst)	# Recalculate Indexes

		self.BuildSuffixTrie (lst)

		## Filtering doesn't work
		if filter_algo:
			fltr = self.FindFilter (algo = filter_algo)
			while fltr:
				#print "Optional Filter:", fltr
				lst = filter (lambda x: x not in fltr, lst)
				self.BuildSuffixTrie (lst)
				if filter_algo == self.ITERATIVE:	# Need more cycles
					fltr = self.FindFilter (algo = filter_algo)
				else: fltr = None

		#self.TraverseTrie ()
		self.FindRepeatPattern ()
		self._trie = None
		return self.GetIndexesList ()

	############################################################################

	## FindFilter  Algorithms ##
	COMPREHENSIVE = 1
	ITERATIVE = 2
	def FindFilter (self, look_ahead = 2, match_len = 2, algo = ITERATIVE):
		"""
		See if we can find tags that if we will filter them out, we will get
		better results
		look_ahead - The number of non structural consecutive tags to look for
		"""
		if not self._trie: return None		# No data to work with
		if algo == self.COMPREHENSIVE:
			fltr, tmp = self.__FindFilter (self._trie, look_ahead, match_len)
		elif algo == self.ITERATIVE:
			fltr, tmp = self.__FindFilter2 (self._trie, look_ahead, match_len)
		else: raise ValueError ("Not filtering algorithm: " + algo)
		if not fltr: return None
		return fltr

	############################################################################

	## The two following methods initialize an object from another object ##
	def GetPattern (self):
		""" """
		return self._output_lst

	def SetPattern (self, lst):
		""" """
		self._output_lst = lst


if __name__ == '__main__':
	rp = RepeatPattern ()
	#lst = list ('XYZXYZABCABCABCXYZ')
	#lst = list ('ABCAYBCAXBC')
	lst = list ('YXNMLAXBCAYBCAXYBCAYXBCABCVBNXY')
	print lst

	#rp.min_repeat = 1
	#rp.max_stdv_ptrn = 0.5
	#rp.filter_func = lambda lst: lst[0] == 'A'
	rp.BuildSuffixTrie (lst)

	#rp.TraverseTrie ()
	print rp.FindRepeatPattern (), rp._best_factor

	fltr = rp.FindFilter (look_ahead = 2, algo = rp.COMPREHENSIVE)
	while fltr:
		print "optional filter:", fltr
		lst = filter (lambda x: x not in fltr, lst)
		print "filtered list:", lst
		rp.BuildSuffixTrie (lst)
		print rp.FindRepeatPattern (), rp._best_factor
		fltr = rp.FindFilter (look_ahead = 2)

	print rp.GetIndexesList ()

	#print rp.DoAllAtOnce (list ('XYZABCABCABCXYZ'))
	#print rp.DoAllAtOnce (list ('erez bibi'))
	#print rp.DoAllAtOnce (list ('erez bibi'), False)



