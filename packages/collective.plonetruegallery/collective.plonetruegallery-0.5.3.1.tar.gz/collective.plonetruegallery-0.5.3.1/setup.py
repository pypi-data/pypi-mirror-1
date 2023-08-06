from setuptools import setup, find_packages
import os

version = '0.5.3.1'

setup(name='collective.plonetruegallery',
      version=version,
      description="A true gallery implementation with plone using smooth gallery",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='gallery plone oshkosh uwosh slideshow photo photos image images',
      author='Nathan Van Gheem',
      author_email='vangheem@gmail.com',
      url='http://svn.plone.org/svn/collective/collective.plonetruegallery/',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['collective'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'gdata.py',
          'flickrapi',
          'simplejson'
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
