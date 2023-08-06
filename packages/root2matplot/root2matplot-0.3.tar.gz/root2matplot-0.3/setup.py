try:
    import setuptools
except ImportError:
    from distribute_setup import use_setuptools
    use_setuptools()
from setuptools import setup, find_packages

import sys, os

setup(
    name         = 'root2matplot',
    version      = '0.3',
    description  = 'Tools to plot ROOT histograms using matplotlib',
    long_description = '',
    author       = 'Jeff Klukas',
    author_email = 'klukas@wisc.edu',
    url          = 'http://packages.python.org/root2matplot/',
    download_url = ('https://klukas.web.cern.ch/klukas/public/'
                    'root2matplot-0.1.tar.gz'),
##     install_requires = ['matplotlib',
##                         'numpy'],
    packages = find_packages('lib'),
    package_dir = {'': 'lib'},
    include_package_data=True,
    entry_points = {
        'console_scripts': [
            'overlayHists = root2matplot.overlayHists:main'
            ]
        },
    classifiers  = [
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Science/Research',
        'License :: Free for non-commercial use',
        'Natural Language :: English',
        'Topic :: Scientific/Engineering :: Visualization',
        'Topic :: Utilities',
        ],
    )
