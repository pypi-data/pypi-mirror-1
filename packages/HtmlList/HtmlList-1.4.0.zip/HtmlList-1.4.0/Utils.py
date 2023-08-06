"""
Utilities File
"""

import re, htmlentitydefs
from urllib2 import urlopen, Request, HTTPError


def ListToDict (lst):
	"""
	Convert a two-tuple list to dictionary.
	Isn't there a built-in function for it?
	"""
	dic = {}
	if not lst: return dic
	for key, val in lst:
		dic[key] = val
	return dic

################################################################################
## Unquote HTML ##
_re_unquote = re.compile ("&(#?)(.+?);")

def _ConvertEntity (m):
    """Convert a HTML entity into normal string (ISO-8859-1)
	From: http://groups.google.com/group/comp.lang.python/browse_thread/thread/7f96723282376f8c/"""
    if m.group (1)=='#':
        try:
            return chr (int (m.group(2)))
        except ValueError:
            return '&#%s;' % m.group(2)
    try:
        return htmlentitydefs.entitydefs[m.group (2)]
    except KeyError:
        return '&%s;' % m.group(2)

def UnquoteHtml (string):
	"""Convert a HTML quoted string into normal string (ISO-8859-1).
	Works with &#XX; and with &nbsp; &gt; etc.
	From: http://groups.google.com/group/comp.lang.python/browse_thread/thread/7f96723282376f8c/"""
	if not string: return string
	return _re_unquote.sub (_ConvertEntity, string)

################################################################################
## Remove tags ##

_ptrn_script = """
	<script
	(
		# [^>]*/> |	# Links that closes in the start tag (<script .... />)
		[^>]*> .*? </script>	# Regular <script>...</script>
	)
"""
_re_script = re.compile (_ptrn_script, re.DOTALL | re.VERBOSE | re.IGNORECASE)

def StripScripts (data):
	""" Removes <script> tags from a string """
	return _re_script.sub (' ', data)

_re_tags = re.compile ('<.*?>')

def StripTags (data):
	""" Removes any tg from a string """
	return _re_tags.sub ('', data)

################################################################################
## Open URL ##

def UrlOpen (url, user_agent = None, err = None):
	"""
	Open a URL with an optional user agent.
	url can be a string or a Request instance

	If err is a list object, in case of URL-Error it will append to this list
	the error code, error message, and URL

	Return the pages text.
	"""
	text = ''
	try:
		if not isinstance (url, Request):
			req = Request (url)
		else: req = url
		if user_agent:
			req.add_header ('user-agent', user_agent)
		page = urlopen (req)
		text = page.read ()
		page.close ()
	except HTTPError, e:
		if isinstance (err, list):
			err.append (e.code)
			err.append (e.msg)
			err.append (e.url)
		print 'Cannot open:', e.url, e.msg, e.code
	except:
		print 'Error opening:', url
	return text

if __name__ == '__main__':
	err_lst = []
	UrlOpen ('http://beesnest.sourceforge.net/foo.bar', err = err_lst)
	print err_lst



