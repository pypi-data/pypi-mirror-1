try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

import sys, os

version = '0.1.0'
def read(*rnames):
    path = os.path.join(os.path.dirname(__file__), *rnames)
    if os.path.exists(path):
        return open(path, 'r').read()
    return "No file"

long_description = (
    "\n"+read('docs/index.txt')
    + '\n'
    + read('CHANGELOG.txt')
    + '\n'
    'License\n'
    '=======\n'
    + read('LICENSE.txt')
    + '\n'
    'Download\n'
    '========\n'
)
setup(
    name='SQLAlchemyManager',
    version=version,
    description="Provides a sensible way of using SQLAlchemy in WSGI applications",
    long_description=long_description,
    # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[],
    keywords='',
    author='',
    author_email='',
    url='',
    license='',
    packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        "SQLAlchemy>=0.4.0,<=0.4.99",
    ],
    entry_points="""
    """,
)

