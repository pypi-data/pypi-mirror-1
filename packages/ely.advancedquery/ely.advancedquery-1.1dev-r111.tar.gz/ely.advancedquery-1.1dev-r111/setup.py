from setuptools import setup, find_packages

version = '1.1'

setup(name='ely.advancedquery',
      version=version,
      description="Advanced Query wraps the Advanced Query extension to zope's ZCatalog (http://www.dieter.handshake.de/pyprojects/zope/AdvancedQuery.html) for use in plone.",
      long_description=open("README.txt").read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Framework :: Zope2",
        "Framework :: Zope3",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='zope plone catalog query',
      author='Matt Halstead',
      author_email='matt@elyt.com',
      url='http://ely.googlecode.com/svn/ely.advancedquery/trunk',
      license='new BSD',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['ely'],
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

