from tests import MyBaseTest

class Test (MyBaseTest):
	def runTest (self):
		""" Test HtmlListSummary on Yahoo Directory results page """
		lst = self.Init ('resources_bp_53.html')
		self.failUnlessEqual (lst[0][0], "/content_resource.php?k=Search%2DEngine%2DOptimization&PageID=89")
		self.failUnlessEqual (lst[0][1], "Search engine optimization")
		self.failUnlessEqual (lst[52][0], "/content_resource.php?k=internet%2Doptimization&PageID=3591")
		self.failUnlessEqual (lst[52][1], "Internet optimization")
