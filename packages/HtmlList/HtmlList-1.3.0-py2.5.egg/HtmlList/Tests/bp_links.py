from tests import MyBaseTest

class Test (MyBaseTest):
	def runTest (self):
		""" Test HtmlListSummary on Blackwood Productions links page """
		lst = self.Init ('links_bp_7.html', \
			args = {'structural_attrs': ['style'], 'pattern_tags': ['td', 'span']})
		self.failUnlessEqual (lst[0][0], "http://www.freerelevantlinks.com")
		self.failUnlessEqual (lst[0][1], "free link exchange")
		self.failUnlessEqual (lst[6][0], "http://www.blackwoodproductions.mv")
		self.failUnlessEqual (lst[6][1], "search engine optimization firm")
		self.failUnlessEqual (lst[6][2], "Maldives #1 search engine optimization company. Blackwood Productions.mv cool runnings.")
