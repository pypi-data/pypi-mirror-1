from tests import MyBaseTest

class Test (MyBaseTest):
	def runTest (self):
		""" Test HtmlListSummary on Yahoo Directory results page """
		lst = self.Init ('opensource_yahoodir_20.html',
			args = {'max_stdv_ptrn': 0.05, 'max_stdv_indx': 0.001})
		self.failUnlessEqual (lst[0][0], "/Computers_and_Internet/Software/Open_Source/OpenOffice_org_Project")
		self.failUnlessEqual (lst[0][1], "OpenOffice.org Project (8)")
		self.failUnlessEqual (lst[19][0], "http://gnuwin32.sourceforge.net")
		self.failUnlessEqual (lst[19][1], "GnuWin32")
