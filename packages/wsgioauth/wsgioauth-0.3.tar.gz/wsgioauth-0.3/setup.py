import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.txt')).read()
CHANGES = open(os.path.join(here, 'CHANGES.txt')).read()
LICENSE = open(os.path.join(here, 'LICENSE.txt')).read()

__version__ = '0.3'
__name__ = 'wsgioauth'
__description__ = """
A WSGI OAuth for working with OAuth from the consumer and service provider
perspective. Contains a middleware for protected WSGI applications with an
associated administration application. Provides a simple library to help
consumers integrate OAuth protected resources into their applications."""
__author__ = 'Michael Mulich | WebLion Group, Penn State University'
__email__ = 'support@weblion.psu.edu'

install_requires = [
    'webob',
    'oauth2',
    'httplib2', # dependency of oauth2
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
        ],
    author=__author__,
    author_email=__email__,
    url='http://weblion.psu.edu/',
    license='GPL', # http://www.gnu.org/licenses/gpl.txt
    keywords='web wsgi oauth authentication authorization',
    packages=find_packages(),
    namespace_packages=[__name__],
    include_package_data=True,
    zip_safe=False,
    install_requires=install_requires,
    tests_require=tests_require,
    test_suite="tests",
    entry_points = """\
    [paste.app_factory]
    mock_oauth_admin = %(name)s.mock:app_factory
    mock_echo_app = %(name)s.mock:echo_app_factory
    [paste.filter_app_factory]
    mock_oauth_filter = %(name)s.mock:filter_factory

    [wsgioauth_authentication]
    no_auth = %(name)s.provider:no_auth
    user_grabber = %(name)s.provider:user_grabber
    [wsgioauth_signatures]
    plaintext = %(name)s.signatures:PLAINTEXT
    hmac_sha1 = %(name)s.signatures:HMAC_SHA1
    """ % {'name': __name__,}
    )
