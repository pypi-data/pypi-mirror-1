HtmlList
========

 - Download it from http://pypi.python.org/pypi/HtmlList/ or by running *easy_install HtmlList*

 - Subversion archive of the project is in https://pyhtmllist.svn.sourceforge.net/svnroot/pyhtmllist/ or for browsing  http://pyhtmllist.svn.sourceforge.net/viewvc/pyhtmllist/

This package tries to find a repetitive pattern in an HTML page that contains some kind of a list (like digest pages). It extracts the sub-html text that creates the pattern, and tries to extract useful information from it.
The idea is that in a typical HTML data page that contains a list of items, there will be a repetitive pattern for the human eye (the page format). If this pattern will be the most prevalent in the page (this will be the case in most pages) we will be able to recognize it and "scrape" the relevant data.

The user has to inherit from *HtmlList* and overwrite the *handle_sub_html* method in order to extract the relevant data.

I built one trivial *HtmlList* class - *HtmlListBreak* that only makes sure there is some text in the sub HTML sections. This class is in the *htmllist_demo* module. The module can also be used as a simple demon to process HTML pages from a web browser (see Testing below).

--------------------------------------------------------------------------------

Usage Example
=============

	>>> from htmllist.htmllist_base import HtmlList
	>>> hl = HtmlList()
	>>> hl.set_text(some_html_page_taxt)
	>>> itr = hl.get_html_list()
	>>> if itr:   # must make this test
	...    for itm in itr:
	...        print itm
	... else:
	...    print "Cannot parse the page"

for more detailed example look at *htmllist.htmllist_demo.py*

--------------------------------------------------------------------------------

About the algorithm
===================
this section refer mainly to the *repeat_pattern* module.

*** In version 2.0.0 I changed the algorithm completely, in addition I changed the  modules names and methods names. In fact the only thing that hasn't been changed is this project's name :) ***

I'm trying to detect the most prevalent pattern on the page, assuming that this section of the page will hold the main content. A "pattern" is a repetitive sequence of HTML tags (but other tags can still be in between the sequence items). An "occurrence" is every place in the page this pattern exists. I'm taking the pattern where it's length multiplied by the number of occurrences multiplied by some kind of standard deviation on the occurrences indices, is the greatest. The pattern must occur more than once.

The new algorithm is based upon the heuristic assumption that in most pages the prevalent pattern will have two or more unique tags in it. The package will only recognize patterns that have these unique tags in them.

The idea is to count tags and put them in "buckets" according to the number of occurrences of each tag. Second level of distribution to buckets is tags that appear in a sequence. Each index of a new item in a bucket should be greater
then the last item index but less than then the next index of the first item...
After I have the buckets, I simply find the one with the highest factor and try to expand it as much as I can. For more details see the *repeat_pattern* documentation.

The old algorithm is implemented in *repeat_pattern2.py*. It is working with an improved Suffix Tree data structure. By building a tree from the input list, I can find repetitive patterns relatively fast. In every node of the tree I also keep an indices list of the occurrence of this sequence on the input list. That allows me to check for overlapping, calculate derivative value, and find all the occurrences of the chosen pattern efficiently.

The *break_html_page* module takes an HTML text and builds a list of tags (with optional attributes). So the *repeat_pattern* module works on a list of arbitrary items, it does not know what an HTML tag is.

The derivatives (not mathematical) of *html_list_base* use the two previous modules to extract the information needed from an HTML page.

More about calculating a derivative on a list:

I use the term derivative as the distances between numbers in a list. This is a list by itself, with one less item than the original list. I'm calculating the normalized standard deviation on the first derivative of the occurrences list. This gives some idea of how randomly the occurrences are distributed on the page. This value is normalized to be between 0 and 1, lower being better. A lower value should indicate a good pattern on a typical HTML page.

--------------------------------------------------------------------------------

If the system doesn't work well on pages from some website, you should try to change some parameters of *htmllist_xxx*:

	*min_len* - Minimum number of tags in the pattern.

	*min_repeat* - Minimum number of times the pattern should repeat in the page. Note: min_repeat must be more then one!

	*max_repeat* - Maximum number of times the pattern should repeat in the page.

	*max_stdv* - Maximum normalized standard deviation of the distances between occurrences. This is a number between 0 and 1. 0 means that the occurrences are in sequence (no other tags in between). 1 means that there is no importance to the position of the occurrences in the page. In a normal HTML page you should keep this number low, but maybe larger than zero.

See the documentation for more details.

--------------------------------------------------------------------------------

Testing
=======

*** I still need to build the regression tests for the new version (2.0.0) ***

There is a way for a user to see how the system works by running *htmllist_demo.py*. The *setup.py* installer sets a *htmllist_demo* script that runs this module.
This script will run in the background. The user then should "Save As" the HTML pages from a web browser (as "HTML only") to the sub folder "Temp" of this package. The script will monitor this folder and try to process any file in it. It will then open the result HTML file in the web browser.

try: *htmllist_demo --help*

--------------------------------------------------------------------------------

ToDo
====
 - Build some regression tests.
 - I need to take the HTML data from a browser DOM module and not from the HTML in the page. As a result I will get also dynamic HTML.
 - Use this package to re-display some HTML pages in a web browser.

--------------------------------------------------------------------------------

This package uses *html5lib* in *break_html_page* to parse the HTML, you can download *html5lib* from http://code.google.com/p/html5lib/

HtmlList was originally developed at Blackwood Productions - http://blackwoodproductions.com - for gathering search engines results. I now direct it more for changing an HTML page display (mainly on limited screens - smart phones), but it still works on search engines pages.

2009-12-15
Erez Bibi
erezbibi@users.sourceforge.net

