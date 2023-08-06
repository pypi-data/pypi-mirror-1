from setuptools import setup, find_packages
import os

version = '1.0b1'

setup(name='collective.sharingroles',
      version=version,
      description="Makes it easier to manage the roles that show up on the 'sharing' page in Plone 3",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='plone sharing local roles',
      author='Martin Aspeli',
      author_email='optilude@gmail.com',
      url='http://pypi.python.org/pypi/collective.sharingroles',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['collective'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'zope.interface',
          'zope.component',
          'plone.app.workflow',
          'Products.GenericSetup',
      ],
      entry_points="""
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
