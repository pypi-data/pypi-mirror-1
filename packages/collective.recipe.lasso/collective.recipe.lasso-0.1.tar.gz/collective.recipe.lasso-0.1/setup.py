from setuptools import setup, find_packages
import sys, os

version = '0.1'

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.txt')).read()
CHANGES = open(os.path.join(here, 'CHANGES.txt')).read()

setup(
    name='collective.recipe.lasso',
    version=version,
    description="Buildout recipe to install Lasso (SSO library)",
    long_description=README + '\n\n' +  CHANGES,
    # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python",
        "Topic :: Internet :: WWW/HTTP",
        ],
    keywords='buildout recipe lasso sso saml',
    author='Shane Hathaway',
    author_email='shane@hathawaymix.org',
    url='http://shane.willowrise.com',
    license='ZPL',
    package_dir={'': 'src'},
    packages=find_packages('src'),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'setuptools',
        'zc.recipe.cmmi>=1.3.0',
        'elementtree',
    ],
    entry_points="""
    [zc.buildout]
    default = collective.recipe.lasso:Recipe
    """,
    )
