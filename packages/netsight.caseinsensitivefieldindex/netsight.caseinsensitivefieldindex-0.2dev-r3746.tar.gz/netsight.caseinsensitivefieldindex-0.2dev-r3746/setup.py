from setuptools import setup, find_packages

version = '0.2'

setup(name='netsight.caseinsensitivefieldindex',
      version=version,
      description="A case insensitive version of Zope's FieldIndex",
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
      keywords='zope indexing fieldindex',
      author='Matt Hamilton',
      author_email='matth@netsight.co.uk',
      url='http://www.netsight.co.uk/',
      license='BSD',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['netsight'],
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
