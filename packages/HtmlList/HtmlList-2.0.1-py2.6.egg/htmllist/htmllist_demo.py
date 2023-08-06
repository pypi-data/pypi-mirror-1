#!python
"""
This module define HtmlListBreak which does not apply any processing to the
sub HTML sections, but makes sure it has some text in it.

When run as a stand-alone it creates a quick and dirty way to break pages from
a web browser. The user should save web browser pages to the Temp folder under
this folder. The script runs in the background, monitors this folder and will
process files in it. Then it tries to open the result as an HTML page again
using a web browser.

It will try the new algorithm first, if there are not results, it will try the
old one.

If the saved file name is "old", it will use the old algorithm only.

try: htmllist_demo.py --help
"""
from __future__ import with_statement
from glob import iglob
from sys import argv
from optparse import OptionParser
import os, time, codecs, re, sys

from htmllist_base import HtmlList
from repeat_pattern import RepeatPattern
from repeat_pattern2 import RepeatPattern as RepeatPatternOld
from break_html_page import validate_list

EXCLUDE_TAGS = None #'b', 'u', 'i', 'em'
MIN_LEN = 2
MIN_REPEAT = 5
MAX_REPEAT = 60

class HtmlListBreak(HtmlList):
	""" Add validation that a sub HTML section has some text in it. """
	def handle_sub_html(self, lst, next):
		if validate_list(lst, next):
			return HtmlList.handle_sub_html(self, lst, next)
		return None

def prepare(debug, old, break_cls=None):
	""" Create an HtmlList object """
	if old:
		hl = HtmlListBreak(pattern_cls=RepeatPatternOld, break_cls=break_cls)
	else:
		hl = HtmlListBreak(pattern_cls=RepeatPattern, break_cls=break_cls)
	if EXCLUDE_TAGS:
		hl.exclude_tags += EXCLUDE_TAGS
	hl.min_len = MIN_LEN
	hl.min_repeat = MIN_REPEAT
	hl.max_repeat = MAX_REPEAT
	hl.debug_level = debug
	return hl

def main(argv):
	""" A quick and dirty way to process HTML pages from a web browser.
Save pages as "HTML only" to the MONITOR directory. The script runs in the
background, will process these files, and reopen the result page.
"""
	parser = OptionParser(description=main.__doc__)
	parser.add_option("-b", "--browser", action="store", type="string", dest="browser",
		help="web-browser (with path if needed), if not given will not open output file in a web-browser")
	parser.add_option("-m", "--monitor", action="store", type="string",
		default="./Temp", dest="monitor",
		help="Directory to monitor [default: %default]")
	parser.add_option("-o", "--output", action="store", type="string",
		default="./temp.html", dest="outfile", help="Output file [default: %default]")
	parser.add_option("-v", "--verbose", action="store", type="int", default="0",
		dest="verbose",  help="Verbose mode (level 0-5) [default: %default]")
	parser.add_option("--old", action="store_true", dest="old", default=False,
		help="Start with the old algorithm [default: %default]")
	parser.add_option("--only_one", action="store_true", dest="only_one",
		default=False, help="Use only one algorithm [default:%default]")
	options, args = parser.parse_args(argv)

	SLEEP = 0.5
	old_file = re.compile("old(.html?)?$", re.I)

	if not os.path.exists(options.monitor):
		os.mkdir(options.monitor)

	print "Waiting..."

	while True:		#  Poll a folder indefinitely (need to work on Windows too:)
		time.sleep(SLEEP)
		for fl in iglob(options.monitor + "/*"):
			# If file exists - process, open in browser and delete them
			print "Handling:", fl
			old = old_file.search(fl)
			with open(fl) as html_file:
				start = time.time()
				text = html_file.read()
				hl = prepare(options.verbose, options.old)
				hl.set_text(text)
				itr = hl.get_html_list()
				if not itr and not options.only_one:
					print "No results - Will try the old algorithm"
					hl = prepare(options.verbose, not options.old,
						break_cls=hl.break_cls)
					itr = hl.get_html_list()
				if itr:
					with codecs.open(options.outfile, "wb", "utf-8") as flo:
						flo.write(		# TODO: Need to get the original url
							u'<HTML><HEAD><BASE href="/" /></HEAD><BODY>\n\n')
						for sub in itr:
							flo.write(sub)
							flo.write(u"\n<HR>\n")
						flo.write(u"\n</BODY></HTML>")
					if options.browser:
						os.system("%s file://%s" % (
							options.browser, os.path.abspath(options.outfile)))
				else:
					print "Cannot find a pattern"
			duration = time.time() - start
			print "Processing took:", duration
			os.remove(fl)

			print "Waiting..."

if __name__ == '__main__':
	main(sys.argv)
