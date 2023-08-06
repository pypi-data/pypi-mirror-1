from setuptools import setup, find_packages
import os

version = '0.2.0'

setup(name='collective.autorestart',
      version=version,
      description="Automatically reloads changed code into Plone when you edit Python files",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Framework :: Plone",
        "Framework :: Zope2"
        ],
      keywords='plone reload development server hotstart',
      author='Mikko Ohtamaa',
      author_email='mikko.ohtamaa@twinapex.com',
      url='http://pypi.python.org/pypi/collective.autorestart',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['collective'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          #'ctypes', # pyinotify dependency, pypi entry broken
          'pyinotify',
          'plone.reload'
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
