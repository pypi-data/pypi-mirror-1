from setuptools import setup, find_packages

version = '0.2.2'

setup(name='currency.converter',
      version=version,
      description="Currency Converter",
      long_description="""\
Converts currency derived from European Central Bank.""",
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Framework :: Zope2",
        "Framework :: Zope3",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='',
      author='Taito Horiuchi',
      author_email='taito.horiuchi@abita.fi',
      url='http://taito.abita.fi/',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['currency'],
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
