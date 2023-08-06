from setuptools import setup, find_packages
import os

version = '1.0a1'

setup(name='pipbox.portlet.popform',
      version=version,
      description="Timed popup configured via portlet",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        ],
      keywords='pipbox',
      author='Steve McMahon',
      author_email='plone-developers@lists.sourceforge.net',
      url='http://plone.org/products/pipbox.portlet.popform',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['pipbox', 'pipbox.portlet'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'Products.PloneFormGen',
          'Products.pipbox',
      ],
      entry_points="""
      # -*- Entry points: -*-

      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
