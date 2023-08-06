from setuptools import setup, find_packages

version = '0.1'

setup(name='Products.Organization',
      version=version,
      description="An Archetypes to represent an organization.",
      long_description="""more info latter
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
      author='Rui Guerra',
      author_email='rui at v2 dot nl',
      url='http://svn.v2.nl/plone_dev',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['Products'],
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
