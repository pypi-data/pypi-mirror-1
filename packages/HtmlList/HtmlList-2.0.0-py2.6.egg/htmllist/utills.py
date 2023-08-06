"""
Utilities File
"""

import re, htmlentitydefs
import itertools
from urllib2 import urlopen, Request, HTTPError

################################################################################

def iter2tuple(func):
	""" Simple decorator to convert iterator to tuple """
	def _iter2tuple (*args, **kw):
		return tuple(func(*args, **kw))
	return _iter2tuple


def not_empty_iter(func):
	""" Decorator over a function that returns a iterator. If the returned
	iterator is empty, it will return None. So the user can (must) check if the
	iterator is not None before using.
	"""
	def _iter_or_none(*args, **kw):
		itr = func(*args, **kw)
		try:
			first = itr.next()
		except StopIteration:
			return None
		else:
			return itertools.chain([first], itr)
	return _iter_or_none

################################################################################
## Unquote HTML ##
_re_unquote = re.compile("&(#?)(.+?);")

def _convert_entity(m):
    """ Convert an HTML entity into normal string (ISO-8859-1)
	From: http://groups.google.com/group/comp.lang.python/browse_thread/thread/7f96723282376f8c/"""
    if m.group(1)=='#':
        try:
            return chr(int(m.group(2)))
        except ValueError:
            return '&#%s;' % m.group(2)
    try:
        return htmlentitydefs.entitydefs[m.group (2)]
    except KeyError:
        return '&%s;' % m.group(2)

def unquote_html(string):
	""" Convert an HTML quoted string into normal string (ISO-8859-1).
	Works with &#XX; and with &nbsp; &gt; etc.
	From: http://groups.google.com/group/comp.lang.python/browse_thread/thread/7f96723282376f8c/"""
	if not string: return string
	return _re_unquote.sub(_convert_entity, string)

################################################################################
## Remove tags ##

_ptrn_script = """<script
	(
		# [^>]*/> |	# Links that closes in the start tag (<script .... />)
		[^>]*> .*? </script>	# Regular <script>...</script>
	)
"""
_re_script = re.compile(_ptrn_script, re.DOTALL | re.VERBOSE | re.IGNORECASE)

def strip_scripts(data):
	""" Removes <script> tags from a string """
	return _re_script.sub(' ', data)

_re_tags = re.compile("<.*?>")

def strip_tags(data):
	""" Removes any tg from a string """
	return _re_tags.sub('', data)

################################################################################
## Open URL ##

def url_open(url, user_agent=None, err=None):
	""" Open a URL with an optional user agent.
	url can be a string or a Request instance

	If err is a list object, in case of URL-Error it will append to this list
	the error code, error message, and URL

	Return the pages text.
	"""
	text = ''
	try:
		if not isinstance(url, Request):
			req = Request(url)
		else: req = url
		if user_agent:
			req.add_header("user-agent", user_agent)
		page = urlopen(req)
		text = page.read()
		page.close()
	except HTTPError, e:
		if isinstance(err, list):
			err.append(e.code)
			err.append(e.msg)
			err.append(e.url)
		print "Cannot open:", e.url, e.msg, e.code
	except:
		print "Error opening:", url
	return text

if __name__ == '__main__':
	err_lst = []
	url_open("http://pyhtmllist.sourceforge.net/foo.bar", err = err_lst)
	assert err_lst



