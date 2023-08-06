import os
from setuptools import setup, find_packages

version = '1.1'

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

long_description = "%s\n%s" % (read('README.txt'), read('docs', 'HISTORY.txt'))

setup(name='collective.workflowed',
      version=version,
      description="A graphical workflow editor for Plone",
      long_description=long_description,
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Framework :: Zope2",
        "Framework :: Zope3",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='zope plone workflow editor',
      author='Carlos de la Guardia',
      author_email='cguardia@yahoo.com',
      url='http://svn.plone.org/svn/collective/collective.workflowed',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['collective'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'collective.wtf',
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
