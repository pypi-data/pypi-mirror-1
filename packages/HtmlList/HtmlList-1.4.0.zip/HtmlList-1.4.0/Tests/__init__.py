"""
Tests sub package

The .py files in this package tests the HtmlListSummary module on different
web pages.

tests.py is a general module, if adding tests one need to add the test module
name to the "tests" in the tests module.

To run all the tests run: HtmlListSummary -t
To run specific test run: HtmlListsummary -t <test_name>

Conclusions from the tests:

	1. In order for HtmlList to work well on search engines results, one has to
	initialize it on a "clean" page, that is a page that all the results looks
	the same. This is because some results from search engines format a little
	different from the other. It is a pain though, I use the search for a
	keyword on one not "major" website like "seo" on blackwoodproductions.com,
	it seams to give clean page every time.

	2. I cannot get HtmlList to work on EVERY page with the exact same
	configuration. For example Dmoz need a "max_stdv_indx",the Blackwood
	Productions links page needs a different set of "pattern_tags" and also
	"structural_attrs".
	However it is much easier to set these values then to set the actual format
	of the page. Moreover, the format might change a bit with time, but it is
	most likely won't affect HtmlList.

So it is not perfect but it is better then trying to parse every page type
separately using regular expressions or some similar method.
"""

