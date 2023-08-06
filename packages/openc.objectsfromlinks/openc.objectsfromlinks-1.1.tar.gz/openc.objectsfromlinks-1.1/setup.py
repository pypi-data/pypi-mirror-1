from setuptools import setup, find_packages
import os

version = '1.1'

setup(name='openc.objectsfromlinks',
      version=version,
      description="Converts a link in a piece of text to an embed code.",
      long_description=open(os.path.join("openc", "objectsfromlinks", "README.txt")).read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='',
      author='Matthew Wilkes',
      author_email='matthew@matthewwilkes.co.uk',
      url='http://svn.plone.org/svn/plone/plone.example',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['openc'],
      include_package_data=True,
      zip_safe=False,
      tests_require=[
           'Products.PloneTestCase',
      ],
      install_requires=[
          'setuptools',
          'hexagonit.swfheader',
          'hachoir-core',
          'hachoir-parser',
          'hachoir-metadata',
          'BeautifulSoup',
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
