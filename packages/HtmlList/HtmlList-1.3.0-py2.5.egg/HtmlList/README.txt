HtmlList
========

This package tries to find a repetitive pattern in an HTML page that contains some kind of a list (like summary pages). It extracts the sub-html text list that creates the pattern, and try to extract useful information from it.

The user has to inherit from HtmlListBase and overwrite the HandleSubHtml method in order to extract the relevant data.

I build one HtmlList class - HtmlListSummary to try and extract Link, Title, and Description from "summary" page that have a list of Link-Description. It works well with many "summary" like pages.

Although it is optional to Initialize the system (HtmlListXXX.Init) it is highly recommended. The system might not work well with every HTML text. One should initialize it on text he/she know works well, and then one will get consistent results on other HTML text with the *same* format (called "lazy" mode).

On the other hand, in some cases it might be hard or impossible to get a "clean" page for initialization. For these cases I'm working on a "FindFilter" feature. After parsing the page once, the package can try to identify some tags that if we will filter them out, we will get a better parse. Unfortunately, this feature is not working well yet :(

The third feature to help with correct pattern selection is limitation on the distances of the occurrences from each other. This is a limit on the standard deviation on the list of distances between the occurrences of the pattern on the page. The assumption here is that an HTML page will be formatted in a way that the spaces between items in a list will be (more or less) equal.

================================================================================

If the system doesn't work well on pages from some website, you should try to change some parameters of HtmlListXXX:

	pattern_tags - A list of tag names to include in the pattern.

	structural_attrs - A list of tag attribute names *not* to ignore.

	min_len - Minimum number of tags in the pattern.

	min_repeat - Minimum number of times the pattern should repeat in the page. Note: min_repeat must be more then one!

	max_stdv_ptrn - Maximum normalized standard deviation of the distances between the patterns. This is a number between 0 and 1. 0 means that the patterns are in sequence (no other tags in between). 1 means that there is no importance to the position of the patterns in the page. In a normal HTML page you should keep this number low, but maybe bigger than zero.

	max_stdv_indx - Maximum normalized standard deviation of the distances between the returned indexes. This has the same restrictions as "max_stdv_ptrn" but to be effective it must be less then "max_stdv_ptrn". When the system picks occurrences of the pattern in the HTML page, it will pick the indexes so the STDV of the list will be less then this value. This is specially important when you use the initialization feature.

	filter_func - Function that gets a list and returns True if this list should be considered for a possible output pattern. This function should test the *beginning* of the list for the pattern. Note: Each item in the list is tow-tuple (tag-name, tag-attrs).

See the documentation for more details.

================================================================================

About the algorithm
These section refer to RepeatPattern.py
The main data structure of this module is an improved Suffix Tree (also called Trie). The input data is a list of items (tags). Building a Trie from this list lets me find repetitive patterns relatively fast. In every node of the Trie I also keep an indices list of the occurrence of this sequence on the input list. That allow me to check for overlapping, calculate the STDV, and find all the occurrences of the chosen pattern efficiently.

More about the different between max_stdv_ptrn and max_stdv_indx
max_stdv_ptrn is an STDV limit on pattern to even consider as optional lists. If some occurrences of a pattern are out of this limit, the pattern will not be taken at all.
max_stdv_indx is the same limit, but for occurrences and not for the pattern itself. HtmlList will filter out occurrences that are outside of this limit, but it will return other occurrences of this pattern.

Abut the Find Filter feature
FindFilter looks for items in the input list (tags) that unnecessarily break the suffix tree (Trie). The places to look for these items is in the beginning of every node in the Trie. These set of methods scan the Trie from the bottom up. In every level it looks at beginning of all the sequences of this level and see if we can filter out some items that will let us join *all* the sequences of this level. Then it moves up while joining all the item it found, and considering the already filtered (in lower levels) sequences.
The assumption here is that, in an HTML page, tags that are safe to filter out in one place will be safe to filter out everywhere in the page. This is a heuristic though, it doesn't work on the mathematical model.
* The FindFilter feature work nicely on testing sequences, but it doesn't work on a real HTML tags lists. I need to work more on it.

================================================================================

This package uses BeautifulSoup in BreakHtmlPageBS to parse the HTML, you can download Beautiful Soup from http://www.crummy.com/software/BeautifulSoup/
BreakHtmlPage parse the page using the python HTMLParser, but it fails if the HTML is not perfect.

TODO:
The initialization is problematic, but I don't think I can give it up.
Try to get FindFilter to work.
Compute better normalized STDV.

2009-06-05
Erez Bibi
erezbibi@frontiernet.net

