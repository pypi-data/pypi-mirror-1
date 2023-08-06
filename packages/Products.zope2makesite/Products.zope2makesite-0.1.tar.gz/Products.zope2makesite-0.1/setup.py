import os
from setuptools import setup
from setuptools import find_packages

NAME = 'zope2makesite'

VERSION = '0.1'

setup(name='Products.%s' % NAME,
      version=VERSION,
      description='Makes the zope2-root a site (providing a componentregistry).',
      author="Daniel Havlik",
      author_email="dh@gocept.com",
      license="ZPL 2.1 (http://www.zope.org/Resources/License/ZPL-2.1)",
      packages=find_packages(),
      include_package_data=True,
      namespace_packages=['Products'],
      zip_safe=False,
      install_requires=[
          'setuptools',
          'five.localsitemanager',
          ],
      entry_points="""
      [zope2.initialize]
      Products.%s = Products.%s:initialize
      """ % (NAME, NAME),
      )


