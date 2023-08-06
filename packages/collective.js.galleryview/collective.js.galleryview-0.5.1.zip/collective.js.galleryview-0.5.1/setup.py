from setuptools import setup, find_packages
import os

version = '0.5.1'

setup(name='collective.js.galleryview',
      version=version,
      description="GalleryView aims to provide jQuery users with a flexible, attractive content gallery that is both easy to implement and a snap to customize.",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        ],
      keywords='',
      author='JeanMichel FRANCOIS',
      author_email='jeanmichel.francois@makina-corpus.com',
      url='https://svn.plone.org/svn/collective/collective.js.galleryview',
      license='MIT',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['collective', 'collective.js'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-

      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
