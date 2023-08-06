from setuptools import setup, find_packages

version = '1.0'

setup(name='plone.oofill',
      version=version,
      description="Uses the oofill python module to fill an odt document with data.",
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
      keywords='OpenOffice odf odt',
      author='atReal',
      author_email='contact@atreal.net',
      url='https://svn.plonegov.org/plone.oofill',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['plone'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'oofill',
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
