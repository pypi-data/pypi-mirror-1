from setuptools import setup, find_packages
import os

version = '1.0b1'

setup(name='collective.novate',
      version=version,
      description="Adds an option too reassign ownership on the sharing page",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='plone ownership sharing',
      author='Martin Aspeli',
      author_email='optilude@gmail.com',
      url='http://pypi.python.org/pypi/collective.novate',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['collective'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'plone.app.workflow',
          'five.grok',
          'plone.formwidget.autocomplete',
          'plone.directives.form',
          'plone.principalsource',
      ],
      entry_points="""
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
