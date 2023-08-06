## this file is generated from settings in build.vel

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

# from options["setup"] in build.vel
config = {'package_data': {'lamson': ['data/prototype.zip']}, 'description': 'Lamson is a modern Pythonic mail server built like a web application server.', 'author': 'Zed A. Shaw', 'url': 'http://pypi.python.org/pypi/lamson', 'author_email': 'zedshaw@zedshaw.com', 'version': '0.9', 'scripts': ['bin/lamson'], 'install_requires': ['jinja2', 'sqlalchemy', 'nose', 'python-daemon'], 'packages': ['lamson', 'lamson.handlers'], 'name': 'lamson'}
setup(**config)

