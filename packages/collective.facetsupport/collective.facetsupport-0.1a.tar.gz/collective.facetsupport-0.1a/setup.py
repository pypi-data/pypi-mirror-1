from setuptools import setup, find_packages
import os

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

version = '0.1a'
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

setup(name='collective.facetsupport',
      version=version,
      description="Tools for generating facets for content in Plone",
      long_description=long_description,
      # Get more strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        ],
      keywords='plone',
      author='Robin Harms Oredsson',
      author_email='robin@betahaus.net',
      url='https://svn.plone.org/svn/collective/collective.facetsupport',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['collective'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
      ],
      entry_points="""
      # -*- Entry points: -*-

      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
