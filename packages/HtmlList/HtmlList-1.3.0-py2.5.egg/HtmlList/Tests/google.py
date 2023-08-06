from tests import MyBaseTest

class Test (MyBaseTest):
	def runTest (self):
		""" Test HtmlListSummary on Google results page """
		lst = self.Init ('weather_google_100.html', 'clean_google_10.html')
		self.failUnlessEqual (lst[0][0], "http://www.weather.com/")
		self.failUnlessEqual (lst[0][1], "National and Local Weather Forecast, Hurricane, Radar and Report")
		self.failUnlessEqual (lst[99][0], "http://meteora.ucsd.edu/weather.html")
		self.failUnlessEqual (lst[99][1], "The SIO Weather Page")
