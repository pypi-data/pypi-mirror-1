from setuptools import setup, find_packages
import os

version = '0.2'

setup(name='collective.multilogo',
      version=version,
      description="A Plone extension package providing wiewlet with user defined multiple portal logos.",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='plone, logo',
      author='Lukas Zdych',
      author_email='lukas.zdych@gmail.com',
      url='http://svn.plone.org/svn/collective/collective.multilogo',
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
