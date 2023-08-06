from setuptools import setup, find_packages

version = '1.0'

setup(name='example.archetype',
      version=version,
      description="An example Archetypes-based product.",
      long_description="""An example product package for learning how to develop an Archetypes-based content type for Plone 3.
""",
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Framework :: Zope2",
        "Framework :: Zope3",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='zope archetypes plone',
      author='Kamon Ayeva',
      author_email='kamon ayeva at gmail com',
      url='http://plone.org/products/example.archetype',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['example'],
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
