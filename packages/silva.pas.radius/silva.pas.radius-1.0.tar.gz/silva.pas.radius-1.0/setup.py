from setuptools import setup, find_packages
import os

version = '1.0'

setup(name='silva.pas.radius',
      version=version,
      description="Radius support Silva",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Zope2",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: BSD License",
        ],
      keywords='pas silva radius authentication',
      author='Sylvain Viollon',
      author_email='info@infrae.com',
      url='https://svn.infrae.com/silva.pas.radius/trunk',
      license='ZPL and BSD',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['silva', 'silva.pas'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
        "setuptools",
        "silva.pas.base",
        "silva.pas.membership",
        "plone.session == 1.2",
        ],
      )
