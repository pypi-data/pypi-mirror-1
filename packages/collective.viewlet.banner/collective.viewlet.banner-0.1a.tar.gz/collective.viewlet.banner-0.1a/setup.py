from setuptools import setup, find_packages
import os

version = '0.1a'

setup(name='collective.viewlet.banner',
      version=version,
      description="A tool for configuring banners displayed using viewlets",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Development Status :: 3 - Alpha",
        ],
      keywords='viewlet banner configuration',
      author='Raphael Ritz and Robin Harms Oredsson',
      author_email='raphael.ritz@incf.org',
      url='http://svn.plone.org/svn/collective/collective.viewlet.banner',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['collective', 'collective.viewlet'],
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
