import sys, os
from setuptools import setup, find_packages

name    = "plone.recipe.atcontenttypes"
version = "0.1"

def read(*rnames):
  return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

long_description = "%s\n%s" % (read('README.txt'), read('CHANGES.txt'))

setup( name                 = name
     , version              = version
     , author               = 'Kevin Deldycke'
     , author_email         = 'kev@coolcavemen.com'
     , description          = "ZC Buildout recipe to generate an ATContentTypes configuration file in the etc/ folder of a zope instance"
     , long_description     = long_description
     , license              = 'ZPL 2.1'
     , keywords             = 'zope buildout ATContentTypes recipe plone'
     , url                  = 'http://dev.plone.org/collective/browser/buildout/' + name
     , classifiers          = [ "License :: OSI Approved :: Zope Public License"
                              , "Framework :: Buildout"
                              , "Framework :: Plone"
                              , "Framework :: Zope2"
                              , "Framework :: Zope3"
                              , "Programming Language :: Python"
                              ]
     , packages             = find_packages('src')
     , package_dir          = {'': 'src'}
     , include_package_data = True
     , namespace_packages   = ['plone', 'plone.recipe']
     , install_requires     = ['zc.buildout', 'setuptools', 'zc.recipe.egg']     
     , zip_safe             = False
     , entry_points         = {'zc.buildout': ['default = %s:Recipe' % name]}
     )
