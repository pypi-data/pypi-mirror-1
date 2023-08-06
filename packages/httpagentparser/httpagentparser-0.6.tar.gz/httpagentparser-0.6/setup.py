from setuptools import setup, find_packages

setup(
    name = "httpagentparser",
    version = 0.6,
    description = "Extracts OS Browser etc information from http user agent string",
    maintainer = "Shekhar Tiwatne",
    maintainer_email = "pythonic@gmail.com",
    license = "http://www.zope.org/Resources/ZPL",
    packages=find_packages(),
    platforms = "any")
