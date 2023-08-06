from setuptools import setup, find_packages
import os

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

version = '0.1a1'
long_description = (
    read('README.txt')
    + '\n' +
    'Change history\n'
    '==============\n'
    + '\n' +
    read('CHANGES.txt')
    + '\n' +
    'Contributors\n'
    '============\n'
    + '\n' +
    read('CONTRIBUTORS.txt')
    + '\n' +
    'Known Issues\n'
    '============\n'
    + '\n' +
    read('KNOWN_ISSUES.txt')
)

setup(name='collective.portlet.facet',
      version=version,
      description="Facet navigation portlet",
      long_description=long_description,
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        ],
      keywords='plone portlet',
      author='Martin Lundwall and Robin Harms Oredsson',
      author_email='robin@betahaus.net',
      url='http://plone.org/products',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['collective', 'collective.portlet'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'collective.facetsupport',
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
