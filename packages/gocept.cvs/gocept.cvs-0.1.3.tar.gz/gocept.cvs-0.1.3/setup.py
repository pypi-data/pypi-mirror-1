from setuptools import setup, find_packages

name = "gocept.cvs"
setup(
    name = name,
    version = "0.1.3",
    author = "Daniel Havlik",
    author_email = "dh@gocept.com",
    description = "zc.buildout recipe for checking out cvs modules.",
    long_description = open('README.txt').read(),
    license = "ZPL 2.1",
    keywords = "buildout cvs recipe",
    classifiers = ["Framework :: Buildout"],
    url='http://svn.gocept.com/repos/gocept/'+name,
    download_url='https://svn.gocept.com/repos/gocept/gocept.cvs/trunk#egg=gocept.cvs-dev',
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
