from setuptools import setup, find_packages

name = "plone.recipe.unifiedinstaller"
version = '0.1'

setup(
    name = name,
    version = version,
    author = "Steve McMahon",
    author_email = "steve@dcn.org",
    description = "ZC Buildout recipe for Unified Installer install finalization",
    long_description = open("README.txt").read(),
    license = "ZPL 2.1",
    keywords = "zope2 buildout",
    url='https://svn.plone.org/svn/collective/buildout/plone.recipe.unifiedinstaller/trunk',
    classifiers=[
      "License :: OSI Approved :: Zope Public License",
      "Framework :: Buildout",
      "Framework :: Zope2",
      "Programming Language :: Python",
      ],
    packages = find_packages('src'),
    include_package_data = True,
    package_dir = {'':'src'},
    namespace_packages = ['plone', 'plone.recipe'],
    install_requires = ['zc.buildout', 'setuptools', 'zc.recipe.egg'],
    dependency_links = ['http://download.zope.org/distribution/'],
    zip_safe=False,
    entry_points = {'zc.buildout': ['default = %s:Recipe' % name]},
    )
