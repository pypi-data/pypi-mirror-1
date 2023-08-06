## Copyright (c) 2009 Nathan R. Yergler, Creative Commons

from setuptools import setup, find_packages

import sys

setup(
    name = "wsgi_cache",
    version = "0.1",
    packages = ['wsgi_cache'],
    
    # scripts and dependencies
    install_requires = [
        'setuptools',
        ],

    tests_require = [
        'nose',
        'coverage',
        'WebTest',
        ],

    # author metadata
    author = 'Nathan R. Yergler',
    author_email = 'nathan@yergler.net',
    license = 'MIT',
    entry_points = """\
      [paste.filter_app_factory]
      middleware = wsgi_cache:CacheMiddleware
      """
    )
