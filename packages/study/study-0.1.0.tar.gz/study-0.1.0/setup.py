from setuptools import setup, find_packages

requires = ['multiprocessing']
setup(
    name = 'study',
    version = '0.1.0',
    packages = find_packages(),
    install_requires = requires,
    tests_require = ['nose'],
    test_suite = 'nose.collector',

    # metadata for upload to PyPI
    author = 'Alexander Lamaison',
    author_email = 'awl03@doc.ic.ac.uk',
    description = ('Framework for building data studies in a pipe-and-filter '
                   'style that abstracts over issues such as multiprocessing.'),
    license = 'GPL3',
    url = 'http://code.google.com/p/python-study/',
    download_url = 'http://python-study.googlecode.com/svn/trunk/#egg=study-dev',
    classifiers = [
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.5',
        'Programming Language :: Python :: 2.6',
        'Topic :: Scientific/Engineering',
        'Topic :: Scientific/Engineering :: Information Analysis',
        'Topic :: Software Development',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
        ]
    )
