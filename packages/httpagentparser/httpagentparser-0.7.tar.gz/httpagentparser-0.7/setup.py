from setuptools import setup, find_packages

long_description = """
 >>> import httpagentparser
 >>> s = "Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10.5; en-GB; rv:1.9.0.10) Gecko/2009042315 Firefox/3.0.10"
 >>> print httpagentparser.detect(s)
"""

setup(
    name = "httpagentparser",
    version = 0.7,
    description = "Extracts OS Browser etc information from http user agent string",
    long_description = long_description,
    maintainer = "Shekhar Tiwatne",
    maintainer_email = "pythonic@gmail.com",
    url = "http://pythonik.blogspot.com",
    license = "http://www.zope.org/Resources/ZPL",
    packages=find_packages(),
    platforms = "any")
