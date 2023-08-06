from setuptools import setup, find_packages
import os

version = '9.05'

def read(*pathnames):
    return open(os.path.join(os.path.dirname(__file__), *pathnames)).read()

setup(name='collective.types.citation',
      version=version,
      description="Citation content type",
      long_description=''.join((read('docs', 'README.txt'),
                                read('docs', 'HISTORY.txt'),
                                read('docs', 'INSTALL.txt'),
                                read('docs', 'CUSTOMIZATION.txt'))),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Development Status :: 4 - Beta",
        "Framework :: Plone",
        "Framework :: Zope2",
        "Framework :: Zope3",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='plone types citation',
      author='Liz Dahlstrom',
      author_email='lhill2@u.washington.edu',
      url='http://cphi.washington.edu',
      license='GPL 2',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['collective','collective.types'],
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
