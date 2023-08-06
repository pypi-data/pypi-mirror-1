#!/usr/bin/env python
from setuptools import setup, find_packages
entry_points = """
[zc.buildout]
mkdir = ore.recipe.fs:Mkdir
mkfile = ore.recipe.fs:Mkfile
"""

name = "ore.recipe.fs"

setup (
    name=name,
    description = "File and Directory Creation for Buildout, Extracted from lovely.recipe for minimal dependencies",
    version='0.3.1',
    author = "Lovely Systems",
    author_email = "office@lovelysystems.com",
    maintainer = "Kapil Thangavelu",
    maintainer_email = "kapil.foss@gmail.com",
    license = "ZPL 2.1",
    keywords = "buildout recipe filesystem",
    url='http://www.python.org/pypi/'+name,
    packages = find_packages(),    
    include_package_data = True,
    namespace_packages = ['ore', 'ore.recipe'],
    install_requires = ['setuptools',
                        'zc.buildout',
                        'zc.recipe.egg',
                        ],
    entry_points = entry_points,
    zip_safe = True,
    )
