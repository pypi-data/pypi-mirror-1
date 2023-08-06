from setuptools import setup, find_packages

version = '1.7.0b1'

setup(name='Products.QuillsRemoteBlogging',
      version=version,
      description="MetaWeblogAPI support for Quills",
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
      keywords='plone blogging',
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
          'quills.remoteblogging>=1.7.0b1,<=1.7.99',
          'Products.Quills>=1.7.0b1,<=1.7.99',
          'Products.MetaWeblogPASPlugin>=1.0.0b2,<=1.0.99',
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
