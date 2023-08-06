from setuptools import setup, find_packages

setup(
    name = "StarScream",
    version = "0.1.1",
    packages = find_packages(),
    scripts = ['starscream.py'],

    install_requires = ['docutils>=0.4', 'lxml>=2.0.2', 'simplejson>=1.7.3',
                        'pygments>=0.9', 'setuptools>=0.6c7'],

    package_data = {
        '': ['*.css', '*.js', '*.txt'],
    },

    author = 'Feihong Hsu',
    description = 'StarScream is a presentation tool',
    license = 'New BSD',
    keywords = 'presentation slideshow handout reStructuredText',
    url = 'http://starscream-slideshow.googlecode.com/',
)
