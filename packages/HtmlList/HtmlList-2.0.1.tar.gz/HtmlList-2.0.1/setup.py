from setuptools import setup, find_packages

setup(
    name = "HtmlList",
    version = "2.0.1",
    packages = find_packages(),
	install_requires = ['html5lib'],
	data_files=[('htmllist',
		['htmllist/the_problem.txt', 'htmllist/test_google.html'])],
	scripts=['htmllist_demo'],

    # metadata for upload to PyPI
    author = "Erez Bibi",
    author_email = "erezbibi@users.sourceforge.net",
    description = "Extract data from HTML pages that have some kind of a repetitive pattern",
    keywords = "HTML list recognition repetitive pattern",
	zip_safe = True,
    url = "http://pyhtmllist.sourceforge.net/",
    # download_url
	license = "BSD",
	long_description = """
This package tries to find a repetitive pattern in an HTML page that contains
some kind of a list (like digest pages). It extracts the sub-html text that
creates the pattern, and tries to extract useful information from it.
The idea is that in a typical HTML data page that contains a list of items,
there will be a repetitive pattern for the human eye (the page format). If this
pattern will be the most prevalent in the page (this will be the case in most
pages) we will be able to recognize it and "scrape" the relevant data.""",
	classifiers = [
    'Development Status :: 4 - Beta',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: BSD License',
    'Operating System :: OS Independent',
    'Programming Language :: Python',
    'Topic :: Text Processing :: Markup',
	'Topic :: Utilities'
    ]
)
