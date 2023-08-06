from setuptools import setup, find_packages
import os

versionfile = open(os.path.join('collective', 'portlet', 'references',
                                'version.txt'))
version = versionfile.read().strip()
versionfile.close()

setup(name='collective.portlet.references',
      version=version,
      description="Display references of a page",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='',
      author='Zest Software',
      author_email='m.van.rees@zestsoftware.nl',
      url='http://pypi.python.org/pypi/collective.portlet.references',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['collective', 'collective.portlet'],
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
