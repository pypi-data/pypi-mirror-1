from setuptools import setup, find_packages
import os

version = '0.3'
name = 'collective.namedblobfile'

here=os.path.dirname(__file__)

longdesc = open(os.path.join(here, 'README.txt')).read()

setup(name='collective.namedblobfile',
      version=version,
      description="File field and widget with enhancements for zope3 (using blobs for storage).",
      long_description=longdesc,
      classifiers=[
        "Framework :: Zope3",
        "Programming Language :: Python",
        "License :: OSI Approved :: Zope Public License",
        "Operating System :: OS Independent",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Software Development :: Libraries :: Python Modules"
        ],
      keywords='',
      author='Wichert Akkerman, Martijn Pieters, Laurence Rowe, Dirceu Pereira Tiegs',
      author_email='dirceutiegs@gmail.com',
      maintainer='Dirceu Pereira Tiegs',
      maintainer_email='dirceutiegs@gmail.com',
      url='http://svn.plone.org/svn/collective/collective.namedblobfile',
      license='ZPL 2.1',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['collective'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'collective.namedfile == 1.1',
          'z3c.blobfile == 0.1.0'
      ],
      )
