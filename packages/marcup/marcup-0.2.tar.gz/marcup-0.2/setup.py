# bootstrap easy_install
import ez_setup
ez_setup.use_setuptools()

from setuptools import setup, find_packages

classifiers = """
Intended Audience :: Developers
Intended Audience :: Information Technology
License :: Public Domain 
Programming Language :: Python
Topic :: Text Processing :: General
"""

setup( 
    name = 'marcup',
    version = '0.2',
    url = 'http://cheeseshop.python.org/pypi/marcup',
    author = 'Ed Summers',
    author_email = 'ehs@pobox.com',
    license = 'http://creativecommons.org/licenses/publicdomain/',
    py_modules = ['marcup', 'ez_setup'],
    install_requires = ['pymarc'],
    description = 'manage create/update/deletes marc feeds',
    classifiers = filter(None, classifiers.split('\n')),
    test_suite = 'tests',
    scripts = ['bin/marcup'],
)
