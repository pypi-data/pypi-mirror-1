from setuptools import setup, find_packages

version = '1.1'

setup(name='webcouturier.city.theme',
      version=version,
      description="",
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
      keywords='web couturier plone zope theme',
      author='Denys Mishunov',
      author_email='denis@webcouturier.com',
      url='http://www.webcouturier.com',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['webcouturier', 'webcouturier.city'],
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
