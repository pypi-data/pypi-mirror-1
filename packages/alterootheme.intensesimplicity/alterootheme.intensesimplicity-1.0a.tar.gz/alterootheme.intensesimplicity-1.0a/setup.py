from setuptools import setup, find_packages

version = '1.0a'

setup(name='alterootheme.intensesimplicity',
      version=version,
      description="A Plone 3.0 Theme based on a free template by David Uliana",
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
      keywords='web zope plone theme',
      author='David Bain',
      author_email='david.bain@alteroo.com',
      url='http://themes.alteroo.com',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['alterootheme'],
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
