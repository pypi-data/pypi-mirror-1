from setuptools import setup, find_packages

version = '0.1'

setup(name='qi.LiveChat',
      version=version,
      description="A chat product for plone",
      long_description="""\
""",
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
          'setuptools','Twisted'
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
