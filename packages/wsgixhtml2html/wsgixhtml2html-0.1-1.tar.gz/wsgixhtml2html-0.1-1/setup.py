from setuptools import setup

setup(
    name="wsgixhtml2html",
    version="0.1-1", # added error handling, now checking status codes
    description="WSGI middleware to serve XHTML pages as HTML for old browsers",
    author="chrysn",
    author_email="chrysn@fsfe.org",
    packages=["wsgixhtml2html"],
    license="X11",
    )
