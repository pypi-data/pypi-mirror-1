from setuptools import setup, find_packages
import os

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

long_description = (
    read('README.txt')
    + '\n' +
    read('CHANGES.txt')
    )

setup(name='megrok.yui',
      version='2.5.2',
      description="YUI library packaged as a Grok resource library.",
      long_description=long_description,
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        "Programming Language :: JavaScript",
        "Framework :: Zope3",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='',
      author='Grok Team, YAHOO',
      author_email='grok-dev@zope.org',
      url='',
      license='BSD',
      packages=find_packages('src'),
      package_dir = {'': 'src'},
      namespace_packages=['megrok'],
      include_package_data=True,
      zip_safe=True,
      install_requires=[
          'setuptools',
          'megrok.resourcelibrary',
         ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
