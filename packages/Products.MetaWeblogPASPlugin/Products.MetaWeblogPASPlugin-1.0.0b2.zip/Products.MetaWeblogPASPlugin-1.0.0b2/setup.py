from setuptools import setup, find_packages

version = '1.0.0b2'

setup(name='Products.MetaWeblogPASPlugin',
      version=version,
      description="Enables user authentication for the MetaWeblogAPI",
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
      keywords='plone blogging metaweblog',
      author='Quills Team',
      author_email='quills-dev@lists.etria.com',
      url='http://plone.org/products/quills',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['Products'],
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
