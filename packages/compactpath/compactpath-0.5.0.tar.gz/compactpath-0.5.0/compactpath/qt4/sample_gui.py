"""qt4 sample gui"""

import os, sys
import ntpath
import macpath
import posixpath

from PyQt4 import QtCore, QtGui


#--> rel import hack
class SysPathHack(object):
	def __init__(self, n):
		fpath = os.path.abspath(__file__)
		for i in xrange(n): fpath = os.path.dirname(fpath)
		sys.path.insert(0, fpath)
	def __del__(self): sys.path.pop(0)
hack = SysPathHack(1)

from pathlabelwrap import PathLabelWrap, compactpath

del hack
#<-- rel import hack 
#********************************************************************************
# test GUI
#*******************************************************************************
CAPTION = "compactPath - [%s]"
PATHS = (
	(posixpath, "/my/very/long/path/containing/many/compoponents/here.txt"),
	(ntpath, "c:\\my\\very\\long\\path\\containing\\many\\compoponents\\here.txt"),
	(macpath, "my:very:long:path:containing:many:compoponents:here.txt"),
	(posixpath, "http://my/very/long/path/containing/many/compoponents/here.txt"),
	)
BLINDTEXT = "xxxxxxxxxx"	 # this is set as text to the labels to force a minimum size. Adjust to your needs 

#******************************************************************************
#
#******************************************************************************
class SampleGui(QtGui.QMainWindow):
	"""test gui"""
	
	def __init__(self):
		QtGui.QMainWindow.__init__(self)
		
		self.mainWidget = QtGui.QWidget(self)
		self.setCentralWidget(self.mainWidget)
					
		# NOTE:
		#
		# too bad, no label or the like is retrievable for the caption bar. so no way to adjust it anything
		# on the caption dynamically. best practice seems to be to init to some fixed width. plus is that 
		# the width of the caption bar label seems to have no effect on the GUI width. but this may
		# vary from window manager to window manager.
		#
		pathModule, fpath = PATHS[0]
		fpath = compactpath(50 - len(CAPTION), fpath, path_module=pathModule)
		self.setWindowTitle(CAPTION % fpath)
					
		
		def newPathlabelWrap(mainWidget, layout, frameStyle, pathModule, fpath, prefix=None):
			label = QtGui.QLabel(BLINDTEXT, mainWidget)
			label.setFrameStyle(frameStyle)
			layout.addWidget(label)
			if prefix is None:
				prefix = pathModule.__name__ + ': '
			wrap = PathLabelWrap(label, fpath=fpath, prefix=prefix, path_module=pathModule)
			mainWidget.pathLabels.append(wrap)
			return wrap
			
		# throw labels into the Gui
		layout = QtGui.QVBoxLayout(self.centralWidget())
		frameStyle = QtGui.QLabel.Sunken | QtGui.QLabel.Box
		self.pathLabels = []
		for pathModule, fpath in PATHS:
			newPathlabelWrap(self, layout, frameStyle, pathModule, fpath, prefix=None)
						
		# add a disabled label
		wrap = newPathlabelWrap(self, layout, frameStyle, pathModule, fpath, prefix='disabled: ')
		wrap.label.setEnabled(False)
				
		# for kicks a styled one
		wrap = newPathlabelWrap(self, layout, frameStyle, pathModule, fpath, prefix='styled: ')
		wrap.label.setStyleSheet('QLabel{border: 2px solid cyan; background: blue; color: white}')
		
		# indent should work, too
		wrap = newPathlabelWrap(self, layout, frameStyle, pathModule, fpath, prefix='indented: ')
		wrap.label.setIndent(20)
		
		# as should margin
		wrap = newPathlabelWrap(self, layout, frameStyle, pathModule, fpath, prefix='margined: ')
		wrap.label.setMargin(20)
		
		
		# default QLabel to see test label to see if our owner drawn labels are ok
		self.labelTest = QtGui.QLabel("no shortcuts, no rich text yet", self.mainWidget)
		self.labelTest.setFrameStyle(frameStyle)
		layout.addWidget(self.labelTest)
		
		layout.addItem(QtGui.QSpacerItem(0, 0, QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Expanding))
					
		# add another wrap on the statusbar
		self.status = self.statusBar()
		self.statusLabelWrap = PathLabelWrap(QtGui.QLabel(BLINDTEXT, self.status), fpath=fpath, prefix='status: ')
		self.statusLabelWrap.label.setFrameStyle(frameStyle)
		self.status.addWidget(self.statusLabelWrap.label, 10)
		self.status.addWidget(QtGui.QLabel('foo-bar', self.status))
		
		
	def styleChange(self, oldStyle):
		"""styleChange handler"""
		self.update()
	

#******************************************************************************
#
#******************************************************************************
if __name__ == "__main__":
	a = QtGui.QApplication(sys.argv)
	QtCore.QObject.connect(a,QtCore.SIGNAL("lastWindowClosed()"),a,QtCore.SLOT("quit()"))
	w = SampleGui()
	w.show()
	a.exec_()
