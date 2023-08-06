from setuptools import setup, find_packages
import os

version = '0.1'

setup(name='gomobile.xhtmlmp',
      version=version,
      description="XHTML mobile profile HTML transformer and cleaner for Pyhton",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Intended Audience :: Developers',        
        ],
      keywords='mobile wap safe xhtml profile html cleaner lxml transformer',
      author='Mikko Ohtamaa',
      author_email='mikko.ohtamaa@twinapex.com',
      url='http://www.twinapex.com',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['gomobile'],
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
