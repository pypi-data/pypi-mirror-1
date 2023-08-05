from setuptools import setup, find_packages

name = "plone.recipe.bundlecheckout"
version = '1.0'

setup(
    name = name,
    version = version,
    author = "Hanno Schlichting",
    author_email = "plone@hannosch.info",
    description = "ZC Buildout recipe for installing a package or bundle checkout",
          long_description="""\
    """,
    license = "ZPL 2.1",
    keywords = "buildout",
    url='http://svn.plone.org/svn/collective/buildout/'+name,
    classifiers=[
      "License :: OSI Approved :: Zope Public License",
      "Framework :: Plone",
      "Framework :: Buildout",
      "Programming Language :: Python",
      ],
    packages = find_packages('src'),
    include_package_data = True,
    package_dir = {'':'src'},
    namespace_packages = ['plone', 'plone.recipe'],
    install_requires = ['zc.buildout', 'setuptools'],
    entry_points = {'zc.buildout': ['default = %s:Recipe' % name]},
    )
