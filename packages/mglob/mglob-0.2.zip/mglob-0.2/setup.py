from setuptools import setup, find_packages
import mglob
setup(
    name = 'mglob',
    version = mglob.__version__,
    py_modules = ['mglob'],
    author = "Ville Vainio",
    author_email = "vivainio@gmail.com",
    description = "Enhanced file name globbing module",
    license = "MIT",
    keywords = "glob wildcard",
    long_description = """\
mglob - enhanced file list expansion utility/module

Usable as stand-alone utility (for xargs, backticks etc.), or as a globbing library for own python programs. Globbing the sys.argv is something that almost every Windows script has to perform manually, and this module is here to help with that task. Also Unix users will benefit from enhanced features such as recursion, exclusion, and directory omission.
""",

      entry_points = {
            'console_scripts': [
                'mglob = mglob:main',
		]
	}


)
