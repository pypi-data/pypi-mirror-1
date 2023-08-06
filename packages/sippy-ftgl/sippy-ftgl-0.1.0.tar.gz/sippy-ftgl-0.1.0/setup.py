from setuptools import setup, Extension, find_packages

import sipdistutils

setup(
    name='sippy-ftgl',
    version='0.1.0',
    ext_modules=[
        Extension('FTGL', 
                  ['ftgl.sip'],
                  library_dirs=['/usr/local/lib'],
                  libraries=['ftgl']),
    ],
    include_dirs=['.', '/usr/local/include', '/usr/local/include/freetype2'],
    cmdclass = {'build_ext':sipdistutils.build_ext},

    # metadata for upload to PyPI
    author = "michael j pan",
    author_email = "mikepan@gmail.com",
    description = "Python binding for FTGL using SIP",
    license = "New BSD",
    keywords = "ftgl SIP",
    url = "http://code.google.com/p/sippy-ftgl/",
    long_description = "This is a Python binding for FTGL using SIP",
    platforms = ["All"]

)

