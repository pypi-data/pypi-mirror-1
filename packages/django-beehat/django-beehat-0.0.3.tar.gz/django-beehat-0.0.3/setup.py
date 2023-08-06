from distutils.core import setup

import beehat

setup(
    name = 'django-beehat',
    version = beehat.__version__,
    packages = ['beehat'],
    author = 'John Paulett',
    author_email = 'john@paulett.org',
    description = 'Common Django snippets and other useful code.',
    #long_description = jsonpickle.__doc__,
    license = 'BSD',
    keywords = 'django',
    url = 'http://bitbucket.org/johnpaulett/django-beehat/',
)
