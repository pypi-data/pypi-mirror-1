from setuptools import setup, find_packages

version = '0.1.1'

setup(name='collective.allowsearch',
      version=version,
      description="Provides an interface and a default adapter to allow users to search the catalog independent of the View permission.",
      long_description=file("README.txt").read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Framework :: Zope2",
        "Framework :: Zope3",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='',
      author='Stefan Eletzhofer',
      author_email='stefan.eletzhofer@inquant.de',
      url='https://svn.plone.org/svn/collective/collective.allowsearch/branches/release-0-1',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['collective'],
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
