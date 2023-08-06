from setuptools import setup, find_packages

version = '1.0.2'

setup(name='freearch.theme',
      version=version,
      description="Free Arch Theme for Plone",
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
      keywords='web zope plone theme skin',
      author='Mikko Ohtamaa',
      author_email='mikko@redinnovation.com',
      url='freearch',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['freearch'],
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
