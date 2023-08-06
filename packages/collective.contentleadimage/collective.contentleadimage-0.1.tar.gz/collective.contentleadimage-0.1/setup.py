from setuptools import setup, find_packages

version = '0.1'

setup(name='collective.contentleadimage',
      version=version,
      description="Adds lead image to any content in plone site",
      long_description="""\
This product allows to add descriptiove image to any Archetypes based content in Plone site.""",
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Framework :: Zope2",
        "Framework :: Zope3",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='plone',
      author='Radim Novotny',
      author_email='radim.novotny@corenet.cz',
      url='https://svn.plone.org/svn/collective/collective.contentleadimage',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['collective'],
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
