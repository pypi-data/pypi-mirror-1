import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import pkg_resources
# FIXME pumazi: this stuff is defined twice, once in setup.py and once here. ugh!
pkg_resources.require('WebOb')
pkg_resources.require('oauth2')
pkg_resources.require('httplib2') # dependency of oauth2
# FIXME pumazi: wsgiref is a temporary dependency and should be factored out.
pkg_resources.require('wsgiref')
