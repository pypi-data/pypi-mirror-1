from setuptools import setup, find_packages
import os

version = '0.1b3'

setup(name='plone.z3cform',
      version=version,
      description="A library that allows use of z3c.form with Zope 2 and Plone",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Framework :: Zope2",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='zope plone forms',
      author='Daniel Nouri and contributors',
      author_email='daniel.nouri@gmail.com',
      url='http://pypi.python.org/pypi/plone.z3cform',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['plone'],
      include_package_data=True,
      zip_safe=False,

      # If the dependency to z3c.form gives you trouble within a Zope
      # 2 environment, try the `fakezope2eggs` recipe
      install_requires=[
          'setuptools',
          'z3c.form',
      ],
      )
