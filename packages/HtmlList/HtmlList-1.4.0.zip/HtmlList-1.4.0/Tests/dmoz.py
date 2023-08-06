from tests import MyBaseTest

class Test (MyBaseTest):
	def runTest (self):
		""" Test HtmlListSummary on Dmoz results page """
		# Here I get the correct pattern but not all occurrences are correct
		#	I have not to take the "margin" once
		lst = self.Init ('weather_dmoz_20.html', args = {'max_stdv_indx': 0.001})
		self.failUnlessEqual (lst[0][0], "http://weather.unisys.com")
		self.failUnlessEqual (lst[0][1], "Unisys Weather")
		self.failUnlessEqual (lst[19][0], "http://weather.noaa.gov/weather/KE_cc.html")
		self.failUnlessEqual (lst[19][1], "NOAA NWS - Kenya Weather")
