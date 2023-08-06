from setuptools import setup, find_packages

version = '1.0'

setup(name='webcouturier.hosting.theme',
      version=version,
      description="Web Couturier Hosting Theme",
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
      keywords='web couturier plone theme',
      author='Denys Mishunov',
      author_email='denis@webcouturier.com',
      url='http://www.webcouturier.com',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['webcouturier', 'webcouturier.hosting'],
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
