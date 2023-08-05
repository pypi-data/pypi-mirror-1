from setuptools import setup, find_packages

name = "plone.recipe.plone25install"
version = '0.1'

setup(
    name = name,
    version = version,
    author = "Hanno Schlichting",
    author_email = "plone@hannosch.info",
    description = "ZC Buildout recipe for installing Plone 2.5.",
          long_description="""\
    """,
    license = "ZPL 2.1",
    keywords = "zope2 buildout",
    url='http://svn.plone.org/svn/collective/buildout/plone.recipe.plone25install/trunk',
    classifiers=[
      "License :: OSI Approved :: Zope Public License",
      "Framework :: Zope2",
      "Framework :: Buildout",
      "Programming Language :: Python",
      ],
    packages = find_packages('src'),
    include_package_data = True,
    package_dir = {'':'src'},
    namespace_packages = ['plone', 'plone.recipe'],
    install_requires = ['zc.buildout', 'setuptools'],
    dependency_links = ['http://download.zope.org/distribution/'],
    entry_points = {'zc.buildout': ['default = %s:Recipe' % name]},
    )
