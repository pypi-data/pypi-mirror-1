import os
from setuptools import setup, find_packages, Extension

setup(
    name="lovely.gae.example",
    version='0.1.0',
    author = "Lovely Systems",
    package_dir = {'':'app'},
    packages=find_packages('app'),
    author_email = "office@lovelysystems.com",
    zip_safe = True,
    include_package_data = False,
    install_requires = ['tornado', 'lovely.gae'],
    extras_require = dict(test=['zope.testing', 'webtest']),
    )
