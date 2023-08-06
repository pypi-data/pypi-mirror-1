from setuptools import setup, find_packages
import os

version = '0.3.1'

setup(name='Products.SilvaForum',
      version=version,
      description="Forum for Silva",
      long_description=open(os.path.join("Products", "SilvaForum", "README.txt")).read() + "\n" +
                       open(os.path.join("Products", "SilvaForum", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
              "Framework :: Zope2",
              "License :: OSI Approved :: BSD License",
              "Programming Language :: Python",
              "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='forum silva zope2',
      author='Infrae',
      author_email='info@infrae.com',
      url='http://infrae.com/products/silva/extensions/silva_forum',
      license='BSD',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['Products'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'Products.Silva',
          ],
      )
