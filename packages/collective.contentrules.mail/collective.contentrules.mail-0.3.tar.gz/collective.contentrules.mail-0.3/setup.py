from setuptools import setup, find_packages
import os

version = open(os.path.join("collective", "contentrules", "mail", "version.txt")).read().strip()

setup(name='collective.contentrules.mail',
      version=version,
      description="Flexible mail content rule",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='',
      author='Ingeniweb',
      author_email='support@ingeniweb.com',
      url='https://svn.plone.org/svn/collective/collective.contentrules.mail',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['collective','collective.contentrules'],
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
