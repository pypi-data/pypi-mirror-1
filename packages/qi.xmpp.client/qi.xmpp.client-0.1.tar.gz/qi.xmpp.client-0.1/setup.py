from setuptools import setup, find_packages
import os

version = '0.1'

setup(name='qi.xmpp.client',
      version=version,
      description="A basic xmpp client meant to serve as a base for others.",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='xmpp bot twisted jabber',
      author='G. Gozadinos',
      author_email='ggozad@qiweb.net',
      url='http://chatblox.com/',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['qi', 'qi.xmpp'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools','twisted'
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
