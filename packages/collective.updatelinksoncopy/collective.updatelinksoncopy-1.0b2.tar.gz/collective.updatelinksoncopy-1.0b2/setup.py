from setuptools import setup, find_packages
import os

version = '1.0b2'

tests_require=[
    'ely.contentgenerator',
    'collective.testcaselayer',
    ]

setup(name='collective.updatelinksoncopy',
      version=version,
      description="Update links to child objects in TextFields when an Archetypes based object is copied and pasted",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "INSTALL.txt")).read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        ],
      keywords='Plone Archetypes',
      author='Matt Halstead',
      author_email='matt@elyt.com',
      url="http://pypi.python.org/pypi/collective.updatelinksoncopy",
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['collective'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
      ],
      tests_require=tests_require,
      extras_require={'test': tests_require},
      entry_points="""
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
