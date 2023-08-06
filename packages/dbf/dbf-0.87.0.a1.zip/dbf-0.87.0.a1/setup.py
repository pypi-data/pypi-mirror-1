from distutils.core import setup
from glob import glob
import os

html_docs = glob('html/*')

long_desc="""
package for reading/writing dBase III and Visual FoxPro 6 database files.
primarily intended to ease migration away from vfp.
concurrent access not supported
"""

setup( name='dbf',
       version='0.87.0.a1',
       license='BSD License',
       description='routines for accessing dbf files from python',
       long_description=long_desc,
       url='http://groups.google.com/group/python-dbase',
       py_modules=['test_dbf'],
       packages=['dbf'],
       provides=['dbf'],
       author='Ethan Furman',
       author_email='efurman@admailinc.com',
       classifiers=[
            'Development Status :: 4 - Beta',
            'Intended Audience :: Developers',
            'License :: OSI Approved :: BSD License',
            'Programming Language :: Python',
            'Topic :: Database' ],
       package_data={'dbf': ['html/*']},
     )

