from setuptools import setup, find_packages

version = '1.0'

setup(name='pipbox.portlet.popform',
      version=version,
      description="Timed PloneFormGen form popup configured via portlet",
      long_description=open("README.txt").read() + "\n" +
                       open("CHANGES.txt").read(),
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
          'Products.PloneFormGen>=1.5.5',
          'Products.pipbox>=0.3a8',
      ],
      entry_points="""
      # -*- Entry points: -*-

      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
