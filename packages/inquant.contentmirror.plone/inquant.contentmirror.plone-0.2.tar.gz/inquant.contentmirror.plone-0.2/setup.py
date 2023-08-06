from setuptools import setup, find_packages

version = '0.2'

setup(name='inquant.contentmirror.plone',
      version=version,
      description="Plone UI for contentmirror",
      long_description=file("inquant/contentmirror/plone/README.rst").read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Framework :: Zope2",
        "Framework :: Zope3",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='',
      author='Stefan Eletzhofer',
      author_email='stefan.eletzhofer@inquant.de',
      url='',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['inquant', 'inquant.contentmirror'],
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
