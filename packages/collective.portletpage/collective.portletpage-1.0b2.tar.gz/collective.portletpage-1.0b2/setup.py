from setuptools import setup, find_packages

version = '1.0b2'

setup(name='collective.portletpage',
      version=version,
      description="A Plone page that can contain portlets",
      long_description="""\
After installing this product, you will be able to add a "Portlet Page". This
is a standard Plone "Page", but it also has a "Portlets" tab, from which you
may assign portlets into four slots. The portlets will be shown on the main
view of the content object.
""",
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Framework :: Zope2",
        "Framework :: Zope3",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='',
      author='Martin Aspeli',
      author_email='optilude@gmail.com',
      url='http://plone.org',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['collective'],
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
