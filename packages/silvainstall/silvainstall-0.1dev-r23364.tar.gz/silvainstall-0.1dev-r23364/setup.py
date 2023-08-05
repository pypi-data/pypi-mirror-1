from setuptools import setup, find_packages
import sys, os

version = '0.1'

def long_description():
    readme = open('README.txt').read()
    readme += """

The development version is available in a `Subversion repository
<https://infrae.com/svn/silvainstall/trunk#egg=silvainstall-dev>`_.
"""
    return readme

setup(name='silvainstall',
      version=version,
      description="A script that lets you quickly set up a Zope instance in which you can use standard Python tools like easy_install to add packages",
      long_description=long_description(),
      classifiers=['Framework :: Zope2'],
      keywords='plone zope content management cms',
      author='Infrae',
      author_email='silva-dev@infrae.com',
      url='http://cheeseshop.python.org/pypi/silvainstall',
      license='',
      packages=find_packages(exclude=['ez_setup']),
      include_package_data=True,
      zip_safe=False,
      install_requires=["ploneenv"],
      entry_points = dict(
          console_scripts=[
              'silvainstall = silvainstall.main:main',
          ],
      )
      )
