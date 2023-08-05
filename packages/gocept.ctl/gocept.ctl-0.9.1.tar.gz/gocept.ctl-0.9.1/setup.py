from setuptools import setup, find_packages

name = "gocept.ctl"
setup(
    name = name,
    version = "0.9.1",
    author = "Christian Theune",
    author_email = "ct@gocept.com",
    description = "zc.buildout recipe to create a convenience-script for controlling services",
    long_description = open('README.txt').read(),
    license = "ZPL 2.1",
    keywords = "zope3 buildout",
    url='http://svn.gocept.com/repos/gocept/'+name,
    classifiers = ["Framework :: Buildout"],
    zip_safe=False,
    packages = find_packages('src'),
    include_package_data = True,
    package_dir = {'':'src'},
    namespace_packages = ['gocept'],
    install_requires = ['zc.buildout', 'setuptools'],
    entry_points = {
        'zc.buildout': [
             'default = %s:Recipe' % name,
             ]
        },
    )
