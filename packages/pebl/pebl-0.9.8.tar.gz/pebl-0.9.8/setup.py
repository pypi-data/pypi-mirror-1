import ez_setup
ez_setup.use_setuptools()

from setuptools import setup, find_packages, Extension
import numpy


long_description = """
Pebl is a python library and command line application for inferring the
structure of a Bayesian network given prior knowledge and observations.  Pebl
includes the following features:

 * Can learn with observational and interventional data
 * Handles missing values and hidden variables using exact and heuristic
   methods 
 * Provides several learning algorithms; makes creating new ones simple
 * Has facilities for transparent parallel execution
 * Calculates edge marginals and consensus networks
 * Presents results in a variety of formats
"""



setup(
    name='pebl',
    version='0.9.8',
    description='Python Environment for Bayesian Learning',
    long_description=long_description,
    author='Abhik Shah',
    author_email='abhikshah@gmail.comm',
    url='http://pebl-project.googlecode.com',
    download_url='http://pypi.python.org/pypi/pebl',
    license='MIT',
    zip_safe=False,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
        'Topic :: Scientific/Engineering :: Bio-Informatics',
    ],
    platforms='any',
 
    package_dir={'': 'src'},
    packages=find_packages('src'),

    # required dependencies
    install_requires=[
        # 'numpy >= 1.0.3',       # matrices, linear algebra, etc
        'nose >= 0.9',          # testing framework
        'pydot',                # to output network as dot file
        'pyparsing >= 1.4.7',   # required by pydot but not specified in its setup
        'simplejson',           # for html results
    ],
    
    # data files, resources, etc
    include_package_data = True,

    # tests
    test_suite = 'nose.collector',

    # scripts
    entry_points = {
        'console_scripts': [
            'pebl = pebl.pebl_script:main'
        ]
    },

    # C extension modules
    ext_modules = [
        Extension('pebl._network', sources=['src/pebl/_network.c']),
        Extension('pebl._cpd', sources=['src/pebl/_cpd.c'], include_dirs=[numpy.get_include()]),
    ],
)
