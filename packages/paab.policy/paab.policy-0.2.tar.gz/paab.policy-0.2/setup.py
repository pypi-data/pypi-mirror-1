from setuptools import setup, find_packages

version = '0.2'

setup(name='paab.policy',
      version=version,
      description="paab policy product",
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
      keywords='blog weblog ploneblog',
      author='Roberto Allende - menttes',
      author_email='rover@menttes.com',
      url='http://plone.org/products/paab',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['paab'],
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
