from setuptools import setup, find_packages

version = '0.2.5'

setup(name='inquant.portlet.contextualrecentitems',
      version=version,
      description="A Plone Portlet which displays custom recent types",
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
      author='Ramon Bartl',
      author_email='ramon.bartl@inquant.de',
      url='http://www.inquant.de',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['inquant.portlet'],
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
