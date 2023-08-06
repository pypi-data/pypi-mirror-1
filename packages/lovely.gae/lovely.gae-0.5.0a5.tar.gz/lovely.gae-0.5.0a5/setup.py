import os
from setuptools import setup, find_packages

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

long_description=(
        'Lovely Appengine Packages\n'
        '*************************\n'
        + '\n' +
        read('src', 'lovely', 'gae', 'snapshot', 'README.txt')
        + '\n' +
        read('src', 'lovely', 'gae', 'async', 'README.txt')
        + '\n' +
        read('src', 'lovely', 'gae', 'db', 'property.txt')
        + '\n' + 
        read('src', 'lovely', 'gae', 'batch', 'README.txt')
        + '\n'
        )

open('doc.txt', 'w').write(long_description)

setup(
    name="lovely.gae",
    version="0.5.0a5",
    description="Appengine related Python Packages from Lovely Systems",
    long_description=long_description,
    packages=find_packages('src'),
    author = "Lovely Systems",
    author_email = "office@lovelysystems.com",
    package_dir = {'':'src'},
    keywords = "appengine datastore backup batch utilities",
    license = "Apache License 2.0",
    zip_safe = True,
    url = 'http://code.google.com/p/lovely-gae/',
    include_package_data = False,
    namespace_packages = ['lovely', 'lovely.gae'],
    install_requires = ['setuptools'],
    extras_require = dict(
                          test=['zope.testing', 'webtest'],
                          ),
    entry_points = {'console_scripts':
                    ['download_snapshot=lovely.gae.snapshot.client:download_script',
                     ]},
    )
