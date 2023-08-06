HtmlList
========

This package tries to find a repetitive pattern in an HTML page that contains some kind of a list (like digest pages). It extracts the sub-html text that creates the pattern, and try to extract useful information from it.
The idea is that in a typical HTML data page that contains a list of items, there will be a repetitive pattern for the human eye (the page format). If this pattern will be the most prevalent in the page (this will be the case in most pages) we will be able to recognize it and "scrape" the relevant data.

*** This is not perfect but it is pretty good :) I still cannot get one configuration that will work on *any* page. Version 1.4.0 will probably be the final version for a while.

The user has to inherit from HtmlListBase and overwrite the HandleSubHtml method in order to extract the relevant data.

I build one HtmlList class - HtmlListSummary to try and extract Link, Title, and Description from "summary" page that have a list of Link-Description. It works well with many "summary" like pages.

Although optional, Initializing the system (HtmlListXXX.Init) is highly recommended. The system might not work well with *every* HTML page. One should initialize it on a "clean" page he/she know works well, and then one will get consistent results on other HTML pages with the *same* format (this is called "lazy" mode).

On the other hand, in some cases it might be hard or impossible to get a "clean" page for initialization. For these cases I'm working on a "FindFilter" feature. After parsing the page once, the package can try to identify some tags that if we will filter them out, we will get a better parse. Unfortunately, this feature is not working well yet :(

The third feature to help with correct pattern selection is a limit on some properties of the first and second derivative on the occurrences list. More on that below.

================================================================================

About the algorithm (this section refer mainly to the RepeatPattern module)
---------------------------------------------------------------------------
I'm trying to detect the most prevalent pattern on the page, assuming that this section of the page will hold the main content. A "patten" is a repetitive sequence of HTML tags (after filtering out none formatting tags). "occurrence" is every place in the page this pattern exists. I'm taking the pattern that it's length multiply by the number of occurrences multiply by some factor on the first and second derivative of the occurrences list, is the biggest. The pattern must occur more then once.

The main data structure of this module is an improved Suffix Tree (also called Trie). The input data is a list of items (tags). Building a Trie from this list lets me find repetitive patterns relatively fast. In every node of the Trie I also keep an indices list of the occurrence of this sequence on the input list. That allow me to check for overlapping, calculate derivative values, and find all the occurrences of the chosen pattern efficiently.

The BreakHtmlPage[BS] module takes an HTML text and builds a list of tags (with optional attributes). So the RepeatPattern module works on a list of arbitrary items, it does not know what an HTML tag is.

The derivatives (not mathematical one :) of HtmlListBase use the two previous modules to extract the information we need from an HTML page.

More about calculating a derivative on a list
---------------------------------------------
I use the term derivative as the distances between numbers in a list. This is a list by itself, with one less item then the original list. I'm calculating the normalized standard deviation on the first derivative of the occurrences list. This give some idea of how randomly the occurrences are distributed on the page.
I count the number of consecutive zeros on the second derivative, This give some idea of how many of the occurrences are in constant distant from each other.
This two values are normalized to be between 0 and 1, for STDV lower is better, for "der2-factor" higher is better. They should indicate a good pattern on a typical HTML page.

More about the different between max_stdv_ptrn and max_stdv_indx
----------------------------------------------------------------
max_stdv_ptrn is an STDV limit on pattern to even consider as optional lists. If some occurrences of a pattern are out of this limit, the pattern will not be taken at all.
max_stdv_indx is the same limit, but for occurrences and not for the pattern itself. HtmlList will filter out occurrences that are outside of this limit, but it will return other occurrences of this pattern. This might be the first parameter to try changing.
both value are taken from the first derivative list.

About the Find Filter feature
-----------------------------
FindFilter looks for items in the input list (tags) that unnecessarily break the suffix tree (Trie), that is items that might be breaking the pattern. The places to look for these items is in the beginning of every node in the Trie. These set of methods scan the Trie from the bottom up. In every level it looks at the beginning of all the sequences of this level and see if we can filter out some items that will let us join *all* the sequences of the level. I use two different algorithms. One moves up while joining all the items (filters) it found, and considering the already filtered (in lower levels) sequences. The other take the best filter from all levels, filter the input sequence and repeat this process until there is not more optional filters.
The assumption here is that, in an HTML page, tags that are safe to filter out in one place will be safe to filter out everywhere in the page. This is a heuristic assumption though, it doesn't work on the mathematical model.
*** The FindFilter feature work nicely on testing sequences (using both algorithms), but it doesn't work on a real HTML tags lists. I need to work more on it.

================================================================================

If the system doesn't work well on pages from some website, you should try to change some parameters of HtmlListXXX:

	pattern_tags - A list of tag names to include in the pattern.

	structural_attrs - A list of tag attribute names *not* to ignore.

	min_len - Minimum number of tags in the pattern.

	min_repeat - Minimum number of times the pattern should repeat in the page. Note: min_repeat must be more then one!

	max_stdv_ptrn - Maximum normalized standard deviation of the distances between occurrences. This is a number between 0 and 1. 0 means that the occurrences are in sequence (no other tags in between). 1 means that there is no importance to the position of the occurrences in the page. In a normal HTML page you should keep this number low, but maybe bigger than zero.

	max_stdv_indx - Maximum normalized standard deviation of the distances between the returned occurrences. This has the same restrictions as "max_stdv_ptrn" but to be effective it must be less then "max_stdv_ptrn". When the system picks occurrences of the pattern in the HTML page, it will pick the indexes so the STDV of the list will be less then this value. This is specially important when you use the initialization feature.

	min_der2_factor - The second derivative factor indicates how many  consecutive occurrences of the pattern are in constant distance from each other. This is the number of consecutive zeros in the second derivative on the occurrences list, divide by the length of the second derivative list. This is a number between 0 and 1.

	filter_func - Function that gets a list and returns True if this list should be considered for a possible output pattern. This function should test the *beginning* of the list for the pattern. Note: Each item in the list is tow-tuple (tag-name, tag-attrs).

See the documentation for more details.

================================================================================

This package uses BeautifulSoup in BreakHtmlPageBS to parse the HTML, you can download Beautiful Soup from http://www.crummy.com/software/BeautifulSoup/
BreakHtmlPage parse the page using the python HTMLParser, but it fails if the HTML is not perfect.

TODO:
The initialization is problematic, but I don't think I can give it up.
Try to get FindFilter to work on a real life texts.


HtmlList was developed at Blackwood Productions
http://blackwoodproductions.com

2009-06-09
Erez Bibi
erezbibi@frontiernet.net

