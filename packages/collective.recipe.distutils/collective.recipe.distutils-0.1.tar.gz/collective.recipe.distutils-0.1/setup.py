import os
from setuptools import setup, find_packages

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

setup(
    name = "collective.recipe.distutils",
    version = '0.1',
    description = "A buildout recipe to install distutils Python packages.",
    long_description=(read('README.txt')),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Plugins",
        "Intended Audience :: System Administrators",
        "Framework :: Buildout",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Programming Language :: Python",
        "Topic :: System :: Installation/Setup",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords='build distutils',
    author='Kevin Teague',
    author_email='kevin@bud.ca',
    url='http://svn.plone.org/svn/collective/buildout/collective.recipe.distutils',
    license='GPL',
    packages=find_packages(),
    namespace_packages=['collective','collective.recipe'],
    include_package_data=True,
    zip_safe=True,
    install_requires=['zc.buildout','setuptools',],
    entry_points = {'zc.buildout':
                    ['default = collective.recipe.distutils:Recipe']},
)
