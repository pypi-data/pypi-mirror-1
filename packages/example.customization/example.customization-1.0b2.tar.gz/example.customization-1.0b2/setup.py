from setuptools import setup, find_packages

version='1.0b2'

setup(name='example.customization',
      version=version,
      description="Examples of Plone 3 customization",
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
      keywords='Plone example customiszation',
      author='Martin Aspeli',
      author_email='optilude@gmx.net',
      url='http://plone.org/documentation/tutorial/customization-for-developers',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['example'],
      include_package_data=True,
      zip_safe=True,
      install_requires=[
          'setuptools',
          'plone.app.portlets',
          'plone.browserlayer',
      ],
      entry_points="""
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
