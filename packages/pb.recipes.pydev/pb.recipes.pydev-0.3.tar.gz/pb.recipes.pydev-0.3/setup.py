#!/usr/bin/env python
from setuptools import setup, find_packages

name = 'pb.recipes.pydev'
entry_points = {'zc.buildout':['default = %s:PyDev' % name]}

setup (
    name='pb.recipes.pydev',
    description="Generates an Eclipse Pydev configuration file with path dependencies for an egg",
    long_description = """A recipe that writes a .pydevproject file in a specified
location. This file will contain paths of all the eggs of the current zope
instance + any other paths specified in the buildout.cfg file. After running
the buildout you'll have to close and reopen the Eclipse project, to regenerate
the project's module indexes.""",
    version='0.3',
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