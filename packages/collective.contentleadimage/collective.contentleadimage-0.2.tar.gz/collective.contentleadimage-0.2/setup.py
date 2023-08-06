from setuptools import setup, find_packages

version = '0.2'

setup(name='collective.contentleadimage',
      version=version,
      description="Adds lead image to any content in plone site",
      long_description="""\
This products adds complete support for adding descriptive image to any Archetypes based 
content in Plone site. Each object has new tab "Edit lead image", which allows to upload 
new or remove current image. It is similar behaviour as Plone News Item (you can add image
to news item and this image is displayed in news item overview listing.

There is folder_leadimage_view page template, which can be used to list all items in the folder
together with images attached. 

There is configuration control panel, where you can set maximum width and height of the uploaded
images. The widht and height is applied on each image upload (image is automatically resized).

There is FieldIndex and metadata in portal_catalog: hasContentLeadImage (True/False).
""",
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
