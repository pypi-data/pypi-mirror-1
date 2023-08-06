from setuptools import setup, find_packages
import os

version = '0.3'

README = open(os.path.join(os.path.dirname(__file__),
              'iw', 'debug', 'docs', 'README.txt')).read()

setup(name='iw.debug',
      version=version,
      description="Tools to help debugging a zope based application",
      long_description=README,
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Framework :: Zope2",
        "Framework :: Zope3",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='debug pdb ipdb plone zope',
      author='Ingeniweb',
      author_email='support@ingeniweb.com',
      url='https://ingeniweb.svn.sourceforge.net/svnroot/ingeniweb/iw.debug',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['iw'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
          'ipdb',
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
