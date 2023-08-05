from setuptools import setup, find_packages

name = "koansys.recipe.hooks"
setup(
    name = name,
    version = open("version.txt").read(),
    author = "Chris Shenton",
    author_email = "chris@koansys.com",
    description = "buildout recipe to run python methods as hooks",
    long_description = open("README.txt").read(),
    license = "GPL",
    keywords = "buildout",
    classifiers = [
    "Framework :: Buildout",
    ],
    url = 'http://koansys-recipe-hooks.googlecode.com/svn/trunk',
    packages=find_packages(exclude=['ez_setup']),
    namespace_packages=['koansys.recipe'],
    include_package_data=True,
    zip_safe=False,
    install_requires = ['zc.buildout', 'setuptools'],
    entry_points = {'zc.buildout':
                    ['default = %s:Recipe' % name]},
    )
