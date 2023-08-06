from setuptools import setup, find_packages
import os

version = open(os.path.join("Products", "TALESField", "version.txt")).read().strip()

setup(name='Products.TALESField',
      version=version,
      description="An Archetypes field that stores TALES Expressions",
      long_description= \
        open(os.path.join("Products", "TALESField", "README.txt")).read() + \
        '\n' + \
        open('INSTALL.txt').read(),
      classifiers=[
        "Framework :: Plone",
        "Framework :: Zope2",
        "Programming Language :: Python",
      ],
      keywords='Plone ScriptableFields TALESField',
      author='Jens Klein',
      author_email='jens@bluedynamics.com',
      url='http://plone.org/products/scriptablefields',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['Products'],
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
