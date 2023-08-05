from setuptools import setup, find_packages

name = "gocept.ooodocma"
setup(
    name = name,
    version = "0.9",
    author = "Christian Theune",
    author_email = "ct@gocept.com",
    description = "zc.buildout recipe for installing an OpenOffice.org/DocmaServer package",
    long_description = open('README.txt').read(),
    license = "ZPL 2.1",
    keywords = "zope3 buildout",
    classifiers = ["Framework :: Buildout"],
    url='ftp://ftp.gocept.com/OOoDocmaServer/',
    zip_safe=False,
    packages = find_packages('src'),
    include_package_data = True,
    package_dir = {'':'src'},
    namespace_packages = ['gocept'],
    install_requires = ['zc.buildout', 'setuptools', 'gocept.download', 'zc.recipe.egg', 'zdaemon'],
    entry_points = {
        'zc.buildout': [
             'default = %s:Recipe' % name,
             ]
        },
    )
