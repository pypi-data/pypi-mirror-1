import sys

from setuptools import setup, find_packages

deps = []
if float(sys.version[0:3]) < 2.6:
    deps.append('simplejson>=0.9.1')

setup(
    name = 'pypaster',
    version = '0.6',
    py_modules = ['pypaster'],
    package_data = {'' : './tools/pypaster.vim',
                   },
    provides = ['pypaster'],
    install_requires = deps,
    entry_points = {
        'console_scripts': [
            'pypaster = pypaster.pypaster:main',
        ]
    },

    zip_safe = True,
    # metadata for upload to PyPI
    author = "Matt Kemp",
    author_email = "matt@mattikus.com",
    description = "Uploads code snippets to http://pypaste.com",
    license = "MIT",
    keywords = "pastebin, pypaste, pypaster",
    url = "https://hg.mattikus.com/pypaster/",   # project home page, if any
)

