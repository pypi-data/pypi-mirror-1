from setuptools import setup, find_packages

version = '0.11'

setup(name='plonetheme.greencommunity',
      version=version,
      description="An installable theme for Plone 3.0.",
      long_description="""\
This is an installable theme for Plone 3.0 that is based on the website template by t-3k.  The original can be found at <http://www.oswd.org/design/preview/id/2265>.""",
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Framework :: Zope2",
        "Framework :: Zope3",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='web zope plone theme',
      author='Jonathan Wilde',
      author_email='product-developers@lists.plone.org',
      url='http://www.speedbreeze.com',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['plonetheme'],
      include_package_data=True,
      zip_safe=True,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
