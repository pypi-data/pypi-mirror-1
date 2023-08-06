from setuptools import setup, find_packages
import os

version = '0.2'

setup(name='collective.sectionsubskin',
      version=version,
      description="Apply a marker interface to a request to code for special presentation of a subsection.",
      long_description=open(os.path.join("collective", "sectionsubskin", "README.txt")).read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='',
      author='Matthew Wilkes',
      author_email='matthew.wilkes@circulartriangle.eu',
      url='http://code.liberalyouth.org/basket/collective.sectionsubskin',
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
