"""Generates epydoc documentation for the package in --> packageDir/doc

gen_docs.py

@note: the script assumes it is located in the <doc> or any other emidiate subdirectory of the package 
@note: Use gen_docs.py -? or --help to print out this help text

@requires: epydoc
"""

import sys, os
from epydoc import cli
import subprocess
#************************************************************************************
# consts
#************************************************************************************
PACKAGE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))	
DOC_DIR = os.path.join(PACKAGE_DIR, 'doc')
EPYDOC_FOLDER = 'epydoc'
EPYDOC_DIR = os.path.join(DOC_DIR, EPYDOC_FOLDER)

#************************************************************************************
# helpers
#************************************************************************************
def save_create_dir(directory):
	"""creates a directory if it does not exist already"""
	if not os.path.isdir(directory):
		os.makedirs(directory)
		
def enshure_doc_dir_dxists():
	"""enshures epydoc docdir exists"""
	save_create_dir(EPYDOC_DIR)
			
#**************************************************************************
# 
#**************************************************************************
def main():
	""""""
	enshure_doc_dir_dxists()
	print 'calling epydoc'
	sys.argv = [
			__file__, 
			'-v', 
			'-o%s' % EPYDOC_DIR, 
			'--src-code-tab-width', '4',
			#'--debug',
			PACKAGE_DIR,
			]
	cli.cli()
	print 'ok'
	
	# create a redirect to 'epydoc/index.html'
	print 'creating redirect'
	fp = open(os.path.join(DOC_DIR, 'index.html'), 'w')
	try:
		fp.write('''<html>
	<head>
		<meta http-equiv="Refresh" content="0; URL=%s">
	</head>
</html>
''' % (EPYDOC_FOLDER + '/' + 'index.html') )	
	finally:
		fp.close()
		
	print 'ok'
	print 'done'
			
#**************************************************************************************
#
#**************************************************************************************
if __name__ == '__main__':
	wantsHelp = len(sys.argv) > 1 and sys.argv[1] or None
	if wantsHelp not in ('-?', '--help'):
		sys.exit(main())
	print __doc__
	
		

