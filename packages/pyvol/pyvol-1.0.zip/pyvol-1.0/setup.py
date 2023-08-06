"""Setup script for installing/distribuging package.
"""

from setuptools import setup, find_packages
setup(
    name = "pyvol",
    #version = "1.1.0.dev" would be a pre-release tag of dev,
    #version = "1.1.0-p1" would be a post-release tag of -p1,    
    version = "1.0",
    author = "Emin Martinian, Li Lee, Henry Xu",
    author_email = "emin.martinian@gmail.com",    
    packages = find_packages(),
    # metadata for upload to PyPI
    description = "Volatility estimation in python.",
    license = "MIT",
    keywords = "volatility, estimation",
    test_suite = 'pyvol.testing.unitTestsFromSrc.MakeMainDoctest',
    install_requires = [],
    dependency_links = [],
    zip_safe = True,
    provides = ['pyvol'],
    url = "http://code.google.com/p/pyvol/",   # project home page
    long_description = """


The pyvol project is framework for testing volatility forecasting ideas in financial (or other) time series.

Pyvol provides an easy way for researchers to share and compare volatility estimation approaches. A researcher can subclass the CovEstimator class in pyvolest.est.CovEst and use pyvol to evaluate performance and compare to other estimators.

The pyvol project is also designed to serve as the framework for a number of contests and class projects. Teachers or contest sponsors can create a custom pyvol distribution focused on the types of models and ideas they are interested in, have contestants create estimators, submit them, and evaluate performance in an automated way.

For details and software, see http://code.google.com/p/pyvol.
"""
    
    # could also include long_description, download_url, classifiers, etc.
)
