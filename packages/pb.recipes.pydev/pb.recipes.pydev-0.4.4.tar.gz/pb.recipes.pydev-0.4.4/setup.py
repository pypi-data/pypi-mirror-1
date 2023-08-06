#!/usr/bin/env python
from setuptools import setup, find_packages
import os

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()


name = 'pb.recipes.pydev'
entry_points = {'zc.buildout':['default = %s:PyDev' % name]}


setup (
    name=name, 
    description="Generates an Eclipse Pydev configuration file with path dependencies for an egg", 
    long_description = (
                        read('README.txt') 
                        + "\n\n" +
                        read('CHANGES.txt')
    ), 
    version='0.4.4', 
    author = "Tiberiu Ichim - Pixelblaster SRL", 
    author_email = "tibi@pixelblaster.ro", 
    license = "BSD", 
    keywords = "buildout recipe PyDev eclipse", 
    url = 'http://svn.plone.org/svn/collective/pb.recipes.pydev/', 
    packages = find_packages('src'), 
    include_package_data = True, 
    package_dir = {'':'src'}, 
    namespace_packages = ['pb', 'pb.recipes'], 
    install_requires = ['setuptools', 
                        'zc.buildout', 
                        'zc.recipe.egg', 
                        ], 
    test_suite = name + '.tests.test_suite', 
    entry_points = entry_points, 
    zip_safe = True, 
    classifiers = [
        "Development Status :: 4 - Beta", 
        "Environment :: Plugins", 
        "Framework :: Buildout", 
        "Framework :: Zope3", 
        "Intended Audience :: Developers", 
        "License :: OSI Approved :: BSD License", 
        "Operating System :: OS Independent", 
        "Programming Language :: Python", 
        "Topic :: Software Development :: Build Tools", 
        "Topic :: Text Editors :: Integrated Development Environments (IDE)"
        ]
    )
