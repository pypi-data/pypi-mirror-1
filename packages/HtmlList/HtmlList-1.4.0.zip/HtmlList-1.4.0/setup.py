from setuptools import setup, find_packages

setup(
    name = "HtmlList",
    version = "1.4.0",
    packages = ['HtmlList', 'HtmlList.Tests'],
	install_requires = ['BeautifulSoup'],
	package_dir = {
		'HtmlList': '.'
	},
	package_data = {
        'HtmlList': ['*.txt'],
		'HtmlList.Tests': ['*.html']
    },

    # metadata for upload to PyPI
    author = "Erez Bibi",
    author_email = "erezbibi@frontiernet.net",
    description = "Extract data from HTML pages that contains some kind of a list",
    keywords = "HTML list recognition repetitive pattern",
	zip_safe = True,
    #url = "http://blackwoodproductions.com/HtmlList",
    # download_url
	license = "BSD",
	long_description = """
This package tries to find a repetitive pattern in an HTML page that contains
some kind of a list (like digest pages). It extracts the sub-html text that
creates the pattern, and try to extract useful information from it.
The idea is that in a typical HTML data page that contains a list of items,
there will be a repetitive pattern for the human eye (the page format). If this
pattern will be the most prevalent in the page (this will be the case in most
pages) we will be able to recognize it and "scrape" the relevant data."""
)
