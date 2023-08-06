# Check python version
import os
from setuptools import setup, find_packages

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

setup(
    name="z3c.recipe.epydoc",
    version='0.0.3',
    author="Andrew Mleczko",
    author_email = "andrew@mleczko.net",
    description="Use EpyDoc to build documentation for python modules",
    long_description=(read(os.path.join('src','z3c','recipe','epydoc','readme.txt'))
                      +'\n\n'+
                      read('CHANGES.txt')),
    license="ZPL 2.1",
    maintainer="Andrew Mleczko",
    maintainer_email="andrew@mleczko.net",
    classifiers=[
        "Development Status :: 3 - Alpha",
        'Framework :: Zope2',
        'Framework :: Zope3',
        'Framework :: Plone',
        'Natural Language :: English',        
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Zope Public License",
        "Operating System :: OS Independent",
        "Programming Language :: Python"],
    url='http://pypi.python.org/pypi/z3c.recipe.epydoc/',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    namespace_packages=['z3c','z3c.recipe'],
    install_requires=['setuptools',
                      'zc.buildout',
                      'zc.recipe.egg',
                      'zope.dottedname',
                      'epydoc'],
    entry_points="""
    [zc.buildout]
    default = z3c.recipe.epydoc:EpyDoc
    """,
    zip_safe=False,
    include_package_data=True,
    )