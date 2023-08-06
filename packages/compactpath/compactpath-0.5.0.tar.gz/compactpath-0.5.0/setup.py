"""a python package to compact filepaths to a desired length

the package provides means to handle compacting of filepaths. compacting of filepaths
may be useful in gui programming for example where filepaths of arbitrary length have
to be displayed in widgets with limited visula space.

the package is designed so you can use it as from everywhere. no need to install it to
site-packages, in case you want to include it in a project. it comes equipped with a 
wrapper for labels to handle filepaths of arbitrary length in qt4.
"""

from distutils.core import setup
 
AUTHOR = 'Juergen Urner'
AUTHOR_EMAIL = 'jUrner@arcor.de'
CLASSIFIERS = [
		'Development Status :: 4 - Beta',
		'Intended Audience :: Developers',
		'License :: OSI Approved :: MIT License',
		'Operating System :: OS Independent',
		'Programming Language :: Python',
		'Topic :: System :: Filesystems',
		]
DOWNLOAD=''
NAME = 'compactpath'
URL = 'https://sourceforge.net/projects/compactpath/'
VERSION = '0.5.0'

MODULES = ['compactpath', ]
DATA = {}


if __name__ == '__main__':
	setup(
		author = AUTHOR,
		author_email = AUTHOR_EMAIL,
		classifiers=CLASSIFIERS,
		description=__doc__.split('\n')[0],
		download_url=DOWNLOAD,
		long_description='\n'.join(__doc__.split('\n')[2:]),
		name=NAME,
		url=URL,
		version=VERSION,    
		
		license='MIT licence',
		platforms=['Many', ],
		py_modules=MODULES,
		package_data = DATA
		)