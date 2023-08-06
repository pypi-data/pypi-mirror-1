from setuptools import setup, find_packages

version = '0.1'

setup(name='menttes.action.createfolder',
      version=version,
      description="An action to create folders with content rules",
      long_description="""\
An action to create folders with content rules""",
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Framework :: Zope2",
        "Framework :: Zope3",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='content rules action create folder',
      author='Roberto Allende',
      author_email='rover@menttes.com',
      url='http://labs.menttes.com',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['menttes.action', 'menttes'],
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
