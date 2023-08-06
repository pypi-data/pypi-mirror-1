from setuptools import setup, find_packages
import os

version = '0.6b2.2'

setup(name='collective.plonetruegallery',
      version=version,
      description="A gallery product for plone that can aggregate from picasa and flickr",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='gallery plone oshkosh uwosh slideshow photo photos image images picasa flickr',
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
          'gdata.py==1.2.3',
          'flickrapi==1.2',
          'simplejson'
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
