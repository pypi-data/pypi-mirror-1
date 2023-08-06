from setuptools import setup, find_packages
import sys, os

version = '0.1'

package_dir = os.path.join(
    os.path.dirname(__file__), 'grouparchy', 'schema')

setup(name='grouparchy.schema',
      version=version,
      description="Grouparchy zope.schema extensions",
      long_description=(
          open(os.path.join(package_dir, 'event.txt')).read() + '\n' +
          open(os.path.join(package_dir, 'interface.txt')).read()),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Framework :: Zope2",
        "Framework :: Zope3",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='',
      author='Ross Patterson',
      author_email='me@rpatterson.net',
      url='http://pypi.python.org/pypi/grouparchy.schema',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['grouparchy'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
          'zope.schema',
          'zope.dottedname',
          'zope.publisher',
          'zope.app.form',
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
