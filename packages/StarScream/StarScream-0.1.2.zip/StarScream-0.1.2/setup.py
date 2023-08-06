from setuptools import setup, find_packages

long_desc = """
StarScream lets you write your entire presentation using reStructuredText_.
The resulting slides and handouts are generated as DHTML files, viewable
in any modern web browser.

.. _reStructuredText: http://en.wikipedia.org/wiki/ReStructuredText
"""

setup(
    name = "StarScream",
    version = "0.1.2",
    packages = find_packages(),
    scripts = ['starscream.py'],

    install_requires = ['docutils>=0.4', 'lxml>=2.0.2', 'simplejson>=1.7.3',
                        'pygments>=0.9', 'setuptools>=0.6c7'],

    package_data = {
        '': ['*.css', '*.txt', 'scripts/*.js'],
    },

    author = 'Feihong Hsu',
    description = 'StarScream is a presentation tool',
    long_description = long_desc,
    license = 'New BSD',
    keywords = 'presentation slideshow handout reStructuredText',
    url = 'http://starscream-slideshow.googlecode.com/',
)
