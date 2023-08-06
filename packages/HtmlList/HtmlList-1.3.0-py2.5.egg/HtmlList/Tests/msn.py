from tests import MyBaseTest

class Test (MyBaseTest):
	def runTest (self):
		""" Test HtmlListSummary on MSN results page """
		lst = self.Init ('weather_msn_49.html', 'clean_msn_10.html')
		self.failUnlessEqual (lst[0][0], "http://www.weather.com/")
		self.failUnlessEqual (lst[0][1], "National and Local Weather Forecast, Hurricane, Radar and Report")
		self.failUnlessEqual (lst[1][1], "Yahoo! Weather")
		self.failUnlessEqual (lst[48][0], "http://www.intellicast.com/National/Default.aspx")
		self.failUnlessEqual (lst[48][1], "Intellicast - United States Weather Maps")
