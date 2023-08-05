#!/usr/bin/env python
"""cclib: parsers and algorithms for computational chemistry

cclib is a Python library that provides parsers for computational
chemistry log files. It also provides a platform to implement
algorithms in a package-independent manner.
"""

doclines = __doc__.split("\n")

# Chosen from http://www.python.org/pypi?:action=list_classifiers
classifiers = """\
Development Status :: 4 - Beta
Environment :: Console
Intended Audience :: Science/Research
Intended Audience :: Developers
License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)
Natural Language :: English
Operating System :: OS Independent
Programming Language :: Python
Topic :: Scientific/Engineering :: Chemistry
Topic :: Software Development :: Libraries :: Python Modules
"""

programs = ['ADF', 'GAMESS', 'GAMESS-UK', 'Gaussian', 'Jaguar', 'Molpro']

def setup_cclib():

    from distutils.core import setup


    # Setup the list of packages.
    cclib_packages = ['cclib',
                      'cclib.parser', 'cclib.progress', 'cclib.method', 'cclib.bridge']

    setup(
        name = "cclib",
        version = "0.8",
        url = "http://cclib.sf.net",
        author = "cclib development team",
        author_email = "cclib-users@lists.sourceforge.net",
        maintainer = "cclib development team",
        maintainer_email = "cclib development team",
        license = "LGPL",
        description = doclines[0],
        long_description = "\n".join(doclines[2:]),      
        classifiers = filter(None, classifiers.split("\n")),
        platforms = ["Any."],
        scripts = ["src/scripts/ccget", "src/scripts/cda"],
        package_dir = {'cclib':'src/cclib', 'cclib.test':'test'},
        packages = cclib_packages,
        # data_files = cclib_datafiles
	)

if __name__ == '__main__':
    setup_cclib()
