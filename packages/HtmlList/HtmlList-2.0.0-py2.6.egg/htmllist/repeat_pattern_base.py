"""
This is a base class for both algorithms for the repeat-pattern class.
It defines some common help methods and the classes interface.
If in the future there will be other algorithms, they will all extend this class.
"""

import math

class RepeatPatternBase(object):
	"""
	Base class for the RepeatPattern classes
	"""
	def __init__(self, min_len=2, min_repeat=2, max_repeat=0, max_stdv=1,
		debug_level=False):
		""" Parameters:
		min_len - Optional minimum length of the output pattern (sub-list),
			default = 1
		min_repeat - Optional minimum time the pattern should repeat in the list,
			default = 2.
			Note: min_repeat must be more then one!
		max_repeat - Optional maximum time the pattern should repeat in the list,
			a value of zero cancels this limit, default = 0.
		max_stdv - Optional Maximum normalized standard deviation of the
			distances between occurrences. This is a number between 0 and 1.
			0 means that the occurrences are in sequence (no other item in
			between). 1 means that there is no importance to the position of the
			occurrences in the list. The default is one.
		debug_level - Print debugging messages. A number between 0 (none)
			and 5 (all)
		All parameters can be also controlled by changing class members with the
		same names.
		"""
		## Configuration Parameters ##
		self.min_len = min_len
		self.min_repeat = min_repeat
		self.max_repeat = max_repeat
		self.max_stdv = max_stdv
		self.debug_level = debug_level

		## Input ##
		self._input_lst = None

		## Output ##
		self.output_lst = None		# output_lst is the pattern
		self.indices_lst = None		# The Places the pattern occurs (two-tuple)
		self.best_factor = 0		# The factor of the chosen pattern
		self.repeats = 0			# Number of time the pattern occurs

	############################################################################

	## Indices Statistics ##

	def _derivative(self, lst, order=1):
		""" This method preforms discrete derive on a list of numbers. This is
		the list of gaps between the numbers of the list.
		order - the derive order.
		Returns a list of numbers or an empty list
		"""
		while order:
			if len(lst) < 2: return []
			lst = [abs(lst[i+1] - lst[i]) for i in range(len(lst) - 1)]
			order -= 1
		return lst

	def _nstdv(self, lst):
		""" This method calculates some kind of normalized standard deviation on
		a list of numbers. It calculates a regular standard deviation and then
		divide it by the total length of the list of items we are working on
		(this is a class member), the result should be equal or bigger than zero
		but less than one.
		"""
		length = len(lst)
		if length == 0: return 0
		if len(self._input_lst) == 0: return 1
		avg = float(sum(lst)) / length
		sqr_sum = float(sum(map(lambda x: x*x, lst)))
		return (math.sqrt((sqr_sum / length) - (avg * avg))) / len(
			self._input_lst)

	############################################################################

	## Public Methods ##

	def process(self, input_lst, lazy=False):
		""" Find the best pattern in a list of items.
		Returns a list of tow-tuple indices (start, end) of the occurrences of
		the best pattern in the input list, or None if there is no "best"
		pattern.

		A derived class MUST implement this method.

		There is an option to work in "lazy" mode. That is, if we already found
		the pattern on a former page, we will use it to find the indices list
		for this input list more cheaply.
		Lazy mode is based on the assumption that we are dealing with the same
		type of page (same format).
		"""
		raise NotImplementedError("You have to implement this method")

	############################################################################

	## The two following methods initialize an object from another object ##

	def get_pattern(self):
		""" """
		return self.output_lst

	def set_pattern(self, lst):
		""" """
		self.output_lst = lst

