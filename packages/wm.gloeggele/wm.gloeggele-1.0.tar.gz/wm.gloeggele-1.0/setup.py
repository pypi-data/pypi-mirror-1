from setuptools import setup, find_packages
import os

version = '1.0'

setup(name='wm.gloeggele',
      version=version,
      description="Commandline parser for the online-menu of http://www.gloeggele.com",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='xml fun gloeggele',
      author='Harald Friessnegger',
      author_email='harald at webmeisterei (dot) com',
      url='https://svn.webmeisterei.com/repos/public/wm.gloeggele',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['wm'],
      include_package_data=True,
      zip_safe=True,
      install_requires=[
          'setuptools',
          'elementtree',
          # -*- Extra requirements: -*-
      ],
      entry_points={
            'console_scripts': ['gloeggele = wm.gloeggele.menu:main',]
            },

      )
