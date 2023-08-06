from talis import version

pkg_config = {
	"version": version,
	"name": "talis",
	"author": "William Waites",
	"author_email": "wwaites [at] gmail.com",
	"description": "Python API for the Talis Triplestore",
	"url": "http://pypi.python.org/pypi/talis/",
	"download_url": "http://pypi.python.org/packages/source/t/talis/talis-%s.tar.gz" % (version,),
	"long_description" : """\
== Talis Triplestore Python API ==

This small module is intended to provide an API similar to
that of rdflib.Graph used to store and query data in a
Talis triplestore.

The module depends on rdflib, and arguments passed in as
well as values returned are one of its URIRef, Literal or
other Node types.
""",
	"packages": ["talis"],
	"install_requires": ["rdflib"],
	"scripts": ["scripts/talis"],
	"license": "BSD",
	"platforms": ["all"]
}

if __name__ == '__main__':
	from ez_setup import use_setuptools
	use_setuptools()
	from setuptools import setup
	setup(**pkg_config)
