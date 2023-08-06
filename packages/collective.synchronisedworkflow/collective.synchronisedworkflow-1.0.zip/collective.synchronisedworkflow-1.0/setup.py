from setuptools import setup, find_packages
import os

version = '1.0'

setup(name='collective.synchronisedworkflow',
      version=version,
      description="Causes translated Plone content to share the same workflow state.",
      long_description=open(os.path.join('src', 'collective', 'synchronisedworkflow', 'README.txt')).read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Framework :: Plone",
        "Framework :: Zope2",
        "Topic :: Software Development :: Internationalization",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Development Status :: 4 - Beta",
        ],
      keywords='',
      author='Matthew Wilkes',
      author_email='matthew@circulartriangle.eu',
      url='',
      license='GPL',
      package_dir = {'':'src'},
      packages=find_packages('src', exclude=['ez_setup']),
      namespace_packages=['collective'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'Products.LinguaPlone',
          'Products.CMFCore',
          'collective.testcaselayer',
           ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
