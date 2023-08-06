from tests import MyBaseTest

class Test (MyBaseTest):
	def runTest (self):
		""" Test HtmlListSummary on Yahoo "Explore" results page """
		lst = self.Init ('yahoo_explore_100.html',
			args = {'pattern_tags': ['td', 'p']})
		self.failUnlessEqual (lst[0][0], "http://www.webconfs.com/similar-page-checker.php")
		self.failUnlessEqual (lst[0][1], "Similar Page Checker - Duplicate content checker")
		self.failUnlessEqual (lst[99][0], "http://habbotopsites.com/")
		self.failUnlessEqual (lst[99][1], "Habbo Topsites - Rankings - All Sites")
