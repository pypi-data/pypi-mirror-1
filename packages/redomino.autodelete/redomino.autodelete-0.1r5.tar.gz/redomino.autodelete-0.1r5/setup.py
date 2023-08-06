from setuptools import setup, find_packages
import os

version = '0.1r5'
longdesc = open(os.path.join(os.path.dirname(__file__), 'README.txt')).read()

setup(name='redomino.autodelete',
      version=version,
      description="Plone autodelete objects expired tool",
      long_description=longdesc,
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Framework :: Zope2",
        "Framework :: Zope3",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='plone zope',
      author='Davide Moro',
      author_email='davide.moro@redomino.com',
      url='http://www.redomino.com/it/labs/progetti/redomino-autodelete',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['redomino'],
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
