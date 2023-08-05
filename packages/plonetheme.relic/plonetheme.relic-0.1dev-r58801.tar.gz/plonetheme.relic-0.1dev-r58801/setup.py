from setuptools import setup, find_packages

version = '0.1'

setup(name='plonetheme.relic',
      version=version,
      description="An installable theme for Plone 3.0.",
      long_description="""\
A Plone 3.0 theme based on the Relic web template by Kevin Cannon.  The original can be found at http://www.oswd.org/design/preview/id/2175.""",
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Framework :: Zope2",
        "Framework :: Zope3",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='web zope plone theme relic',
      author='Jonathan Wilde',
      author_email='product-developers@lists.plone.org',
      url='http://www.speedbreeze.com',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['plonetheme'],
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
