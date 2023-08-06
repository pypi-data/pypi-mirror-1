pkg_config = {
	"version": "0.90",
	"name": "talis",
	"author": "William Waites",
	"author_email": "wwaites [at] gmail.com",
	"description": "Python API for the Talis Triplestore",
	"packages": ["talis"],
	"scripts": ["scripts/talis"],
	"license": "BSD",
	"platforms": ["all"]
}

if __name__ == '__main__':
	from distutils.core import setup
	setup(**pkg_config)
