import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.txt')).read()
CHANGES = open(os.path.join(here, 'CHANGES.txt')).read()
LICENSE = open(os.path.join(here, 'LICENSE.txt')).read()


__version__ = '0.2'
__name__ = 'wsgioauth.zodb'
__namespace__ = [__name__.split('.')[0]]
__description__ = "A package that implements OAuth with ZODB storage."
__author__ = 'Michael Mulich | WebLion Group, Penn State University'
__email__ = 'support@weblion.psu.edu'

install_requires = [
    'wsgioauth>=0.3',
    'ZODB3',
    'repoze.zodbconn', # connection closer
    'repoze.tm2', # transaction manager
    ]
tests_require = []

setup(
    name=__name__,
    version=__version__,
    description=__description__,
    long_description='\n\n'.join([README, CHANGES, LICENSE]),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Programming Language :: Python",
        "Topic :: Security",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Middleware",
        "Framework :: ZODB",
        ],
    author=__author__,
    author_email=__email__,
    url='http://weblion.psu.edu/',
    license='GPL', # http://www.gnu.org/licenses/gpl.txt
    keywords='web wsgi oauth authentication authorization',
    packages=find_packages(),
    namespace_packages=__namespace__,
    include_package_data=True,
    zip_safe=False,
    install_requires=install_requires,
    tests_require=tests_require,
    test_suite="tests",
    entry_points = """
    [paste.app_factory]
    admin_app = %(name)s:admin_app
    [paste.filter_app_factory]
    zodb_oauth_filter = %(name)s:middleware
    """ % {'name': __name__,}
    )
