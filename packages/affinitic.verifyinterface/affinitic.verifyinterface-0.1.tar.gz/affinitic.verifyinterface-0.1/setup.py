from setuptools import setup, find_packages
import os

version = '0.1'


def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()


setup(name='affinitic.verifyinterface',
      version=version,
      description="Verify interface contract for all implements/classImplements declaration",
      long_description=open("README.txt").read() + "\n" +
                       read('src', 'affinitic', 'verifyinterface', 'README.txt') + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='interface zope.interface',
      author='Affinitic',
      author_email='jfroche@affinitic.be',
      url='http://hg.affinitic.be/affinitic.verifyinterface',
      license='GPL',
      packages=find_packages('src', exclude=['ez_setup']),
      package_dir={'': 'src'},
      namespace_packages=['affinitic'],
      include_package_data=True,
      zip_safe=False,
      extras_require=dict(
            test=['zope.testing',
                  'zc.recipe.testrunner',
                  'zc.buildout']),
      install_requires=[
          'setuptools',
          'zope.interface'
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
