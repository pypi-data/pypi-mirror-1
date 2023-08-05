from setuptools import setup, find_packages
import sys, os

version = '1.0-beta1'
shortdesc ="Post-It portlet and content type for Plone 3."
longdesc = open(os.path.join(os.path.dirname(__file__), 'README.txt')).read()


setup(name='collective.portlet.postit',
      version=version,
      description=shortdesc,
      long_description=longdesc,
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Framework :: Zope2",
        "Framework :: Zope3",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='',
      author='Jens Klein',
      author_email='jens@bluedynamics.com',
      url='http://svn.plone.org/svn/collective/collective.portlet.postit',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['collective', 'collective.portlet'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
