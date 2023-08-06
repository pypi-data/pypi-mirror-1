from tests import MyBaseTest

class Test (MyBaseTest):
	def runTest (self):
		""" Test HtmlListSummary on Yahoo results page """
		# This will work even w/o initialization
		#	but it is recommended - not every page will work
		lst = self.Init ('weather_yahoo_100.html') #, 'clean_yahoo_10.html')
		self.failUnlessEqual (lst[0][0], "http://rds.yahoo.com/_ylt=A0oGkkOvXCRJ9lsB0m5XNyoA;_ylu=X3oDMTEzZjQ1NjRhBHNlYwNzcgRwb3MDMQRjb2xvA3NrMQR2dGlkA0Y5NDVfMTIy/SIG=11bfvarl8/EXP=1227206191/**http%3a//www.weather.com/")
		self.failUnlessEqual (lst[0][1], "The Weather Channel")
		self.failUnlessEqual (lst[1][1], "National and Local Weather Forecast, Hurricane, Radar and Report")
		self.failUnlessEqual (lst[99][0], "http://rds.yahoo.com/_ylt=A0oGkkOvXCRJ9lsBl29XNyoA;_ylu=X3oDMTE1Y25kYjcwBHNlYwNzcgRwb3MDMTAwBGNvbG8Dc2sxBHZ0aWQDRjk0NV8xMjI-/SIG=11u65f9ra/EXP=1227206191/**http%3a//www.edheads.org/activities/weather/")
		self.failUnlessEqual (lst[99][1], "Edheads - Weather Activities - Temperature Converter - Kids Weather ...")
