import os
from setuptools import setup, find_packages

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

version = read('src/Products/PloneFlashUpload/version.txt').strip()

setup(name='Products.PloneFlashUpload',
      version=version,
      description="Product that allows mass-upload of files and images.",
      long_description=(
        read('src/Products/PloneFlashUpload/README.txt') +
        '\n\n' +
        read('src/Products/PloneFlashUpload/HISTORY.txt')
        ),
      classifiers=[
        "Framework :: Plone",
        "Framework :: Zope2",
        "Framework :: Zope3",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='plone upload images',
      author='Rocky Burt (3.0 support by Reinout van Rees)',
      author_email='reinout@zestsoftware.nl',
      url='http://www.plone4artists.org/products/ploneflashupload',
      license='Zope Public License (ZPL) Version 2.1',
      package_dir={'':'src'},
      packages=find_packages('src'),
      namespace_packages=['Products', 'z3c', 'z3c.widget'],
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
