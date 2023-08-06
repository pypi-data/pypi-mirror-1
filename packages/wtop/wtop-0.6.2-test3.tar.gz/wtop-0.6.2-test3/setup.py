#from distutils.core import setup
from setuptools import setup, find_packages

import os, os.path
VERSION = '0.6.2-test3'

cfg_file_path = '/etc'                                        # unix, osx, etc
if (os.name != 'posix') and (os.environ.has_key('HOMEPATH')): # windows
    cfg_file_path = os.environ.get('HOMEPATH')

setup(
    name='wtop',
    version=VERSION,
    packages = find_packages(),

    data_files=[(cfg_file_path, ['wtop.cfg'])],
    scripts=['wtop', 'logrep'],
    py_modules=['logrep'],

    url="http://code.google.com/p/wtop/",
    download_url=("http://pypi.python.org/packages/source/w/wtop/%s.tar.gz" % VERSION),
    author="Carlos Bueno",
    author_email="carlos@bueno.org",

    license='BSD',
    description='running statistics for webservers, plus powerful log-grepping tools'
)
