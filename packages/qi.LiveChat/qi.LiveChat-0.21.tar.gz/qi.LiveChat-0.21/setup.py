from setuptools import setup, find_packages
import os

version = '0.21'

setup(name='qi.LiveChat',
      version=version,
      description="A chat product for plone",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Framework :: Zope2",
        "Framework :: Zope3",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='plone chat',
      author='G. Gozadinos',
      author_email='ggozad@qiweb.net',
      url='http://svn.plone.org/svn/collective/qi.LiveChat',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['qi'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
      ],
      entry_points={
		'console_scripts':['livechat_server = qi.LiveChat.server.xmlrpcServer:main']
		},
      )
