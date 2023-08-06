from setuptools import setup, find_packages
import os

version = '0.5'

setup(name='collective.progressbar',
      version=version,
      description="HTML and Javascript progress bar for Plone",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='plone progress bar',
      author='Upfront Systems',
      author_email='info@upfrontsystems.co.za',
      url='http://svn.plone.org/svn/collective/collective.progressbar',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['collective'],
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
