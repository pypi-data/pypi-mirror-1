import ez_setup
ez_setup.use_setuptools()

from setuptools import setup, find_packages
setup(
    name = "pypaster",
    version = "0.5.2",
    packages = find_packages(),
    package_data = {'' : ['./ez_setup.py']},
    requires = ['simplejson (>=0.9.1)'],
    install_requires = ['simplejson>=0.9.1'],
    provides = ['pypaster'],
    entry_points = {
        'console_scripts': [
            'pypaster = pypaster.pypaster:main',
        ]
    },

    # metadata for upload to PyPI
    author = "Matt Kemp",
    author_email = "matt@mattikus.com",
    description = "Uploads code snippets to FriendPaste.com",
    license = "MIT",
    keywords = "pastebin, pypaste",
    url = "https://hg.mattikus.com/pypaster/",   # project home page, if any
)

