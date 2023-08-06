from setuptools import setup, find_packages

version = '0.2.1'

setup(name='collective.gacontext',
      version=version,
      description="Context dependend GoogleAnalytics",
      long_description=file("README.txt").read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Framework :: Zope2",
        "Framework :: Zope3",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='',
      author='InQuant GmbH',
      author_email='ramon.bartl@inquant.de',
      url='https://svn.plone.org/svn/collective/collective.gacontext/trunk',
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
