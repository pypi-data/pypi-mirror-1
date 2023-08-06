import os

from setuptools import setup, find_packages

# FIXME: This works around a setuptools bug which gets setup_data.py metadata
# from incorrect packages. Ticket #1592
#from setup_data import INFO
setup_data = dict(__name__='', __file__='setup_data.py')
execfile('setup_data.py', setup_data)
INFO = setup_data['INFO']

# Read long description from README.
f = open(os.path.join(os.path.dirname(__file__), 'README.txt'))
long_description = f.read()
f.close()

setup(
    name=INFO['name'],
    version=INFO['version'],
    description='Index docstrings for full-text search.',
    author='Robert Kern',
    author_email='robert.kern@enthought.com',
    url='http://pypi.python.org/pypi/WhooshDoc',
    long_description=long_description,
    packages=find_packages(),
    install_requires=INFO['install_requires'],
    extras_require=INFO['extras_require'],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Software Development :: Documentation",
    ],
    entry_points = dict(
        console_scripts = [
            "wdoc = whooshdoc.app:main",
        ],
    ),
)
