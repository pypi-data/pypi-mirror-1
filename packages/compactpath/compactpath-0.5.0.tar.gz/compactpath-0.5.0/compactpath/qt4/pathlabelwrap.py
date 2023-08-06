"""QLabel wrapper to turn a QLabel into a label that displays a compacted filepath 
"""

import os, sys
from PyQt4 import QtCore, QtGui 

#--> rel import hack
class SysPathHack(object):
	def __init__(self, n):
		fpath = os.path.abspath(__file__)
		for i in xrange(n): fpath = os.path.dirname(fpath)
		sys.path.insert(0, fpath)
	def __del__(self): sys.path.pop(0)
hack = SysPathHack(2)

from compactpath import compactpath

del hack
#<-- rel import hack 
#********************************************************************************
#
#********************************************************************************
class PathLabelWrap(object):
	"""class wrapping a QLabel to display a filepath or url that is compacted or decompacted on resizing of the label
	
	usage::
		# create a label in designer or wherever and wrap it afterwards
		self.wrap = PathLabelWrap(self.myLabel, '/foo/bar/baz', prefix='MyPath: ')
	
	@ivar fpath: filepath wrapped. setting this attr directly will not update the label. use L{setPath} instead
	@ivar label: the QLabel wrapped
	@ivar path_module: module to use to split and join the filepath. setting this attr directly will not update the label. use L{setPath} instead
	@ivar prefix: fixed size string to prefix the filepath with. setting this attr directly will not update the label. use L{setPath} instead
	"""
	
	def __init__(self, label, fpath='', prefix='', path_module=os.path):
		"""constructor
		
		@param label: an initialized QLabel to wrap compactPath funktionality around
		@param fpath: the filepath or url the label should display
		@param path_module: module to use to split and join the filepath. hint: if you want
		to display a macpath on linux pass macpath.
		@param prefix: fixed size string to prefix the filepath with (will never be compacted)
		
		@note: problem to tackle is that qt adjusts the size of any label to fit its contents. this wrapper
		does it vice versa and adjusts the contents to the size of the label. so by default qt has to assume
		the label is empty. you can set a text to the label (wich never gets displayed) to force a minimum label size
				
		@note: currently the wrapper does not know how anything about rich text. no use to pass
		a label containing rich text. the rich text it won't show up and behaviour of the label is undefined
		
		@note: when used on a statusbar you may want to adjust the stretch facor. otherwise label
		contents may not be visible because it never gets resized
		"""
		self.fpath = fpath		
		self.label = label
		self.path_module = path_module
		self.prefix = prefix
				
		self.label.paintEvent = self.paintEvent	# overwrite
				
			
	def setPath(self, fpath, prefix=None, path_module=None):
		"""sets the filepath to be displayed by the label
		
		@param fpath: the filepath or url the label should display
		@param path_module: module to use to split and join the filepath or None to keep the current one
		@param prefix: fixed size string to prefix the filepath with (will never be compacted) or None to keep the current one
		"""
		if prefix is not None:
			self.prefix = prefix
		if path_module is not None:
			path_module = path_module
		self.fpath = fpath
		self.label.update()
		
	
	def path(self):
		"""retrieves the (uncompacted) filepath wrapped
		"""
		return self.fpath
	
	
	def paintEvent(self, event):
		"""reimplemented QLabel.paintEvent()"""
		style = self.label.style()
		painter = QtGui.QPainter(self.label)
		palette = self.label.palette()
		fm = self.label.fontMetrics()
		cr = self.label.contentsRect()
		align = style.visualAlignment(self.label.layoutDirection(), self.label.alignment())
		
		cr.adjust(self.label.margin(), self.label.margin(), -self.label.margin(), -self.label.margin())
				
		indent = self.label.indent()
		if indent < 0:		  # see Qt docs: label.indent()
			if indent > 0:
				indent = fm.width("x") / 2
			else:
				indent = 0
		if  indent > 0:
			if align & QtCore.Qt.AlignLeft:
				cr.setLeft( cr.left() + indent);
			if align & QtCore.Qt.AlignRight:
				cr.setRight(cr.right() - indent)
			if align & QtCore.Qt.AlignTop:
				cr.setTop(cr.top() + indent)
			if align & QtCore.Qt.AlignBottom:
				cr.setBottom(cr.bottom() - indent)
				
		w = cr.width()
		if self.prefix:
			w -= fm.width(self.prefix)
		fpath = compactpath(
						w, 						
						self.fpath, 
						measure=fm.width, 
						path_module=self.path_module
						)
		self.label.drawFrame(painter)
		style.drawItemText(painter, cr, align, palette, self.label.isEnabled(), self.prefix + fpath, self.label.foregroundRole())
				
		
	#************************************************************************************************
	# the original QLabel.painEvent() handler (for readability pixmap and movie stuff removed)
	# quite a beast with calls to obscure private methods ...the reason why PathLabelWrap() currently 
	# does not support rich text
	#
	# as a hint: QTextDocument can be retrieved like this:
	##textDocument = None
	##for i in self.label.children():
	##	for j in i.children():
	##		if isinstance(j, QtGui.QTextDocument):
	##			textDocument = j
	##
	##if textDocument is not None:
	##	# process		
			
	"""
	void QLabel::paintEvent(QPaintEvent *)
	{
		Q_D(QLabel);
		QStyle *style = QWidget::style();
		QPainter painter(this);
		drawFrame(&painter);
		QRect cr = contentsRect();
		cr.adjust(d->margin, d->margin, -d->margin, -d->margin);
		int align = QStyle::visualAlignment(layoutDirection(), QFlag(d->align));


		if (d->isTextLabel) {
			QRectF lr = d->layoutRect();
			if (d->control) {
	#ifndef QT_NO_SHORTCUT
				const bool underline = (bool)style->styleHint(QStyle::SH_UnderlineShortcut, 0, this, 0);
				if (d->shortcutId != 0
					&& underline != d->shortcutCursor.charFormat().fontUnderline()) {
					QTextCharFormat fmt;
					fmt.setFontUnderline(underline);
					d->shortcutCursor.mergeCharFormat(fmt);
				}
	#endif
				d->ensureTextLayouted();

				QAbstractTextDocumentLayout::PaintContext context;
				QStyleOption opt(0);
				opt.init(this);

				if (!isEnabled() && style->styleHint(QStyle::SH_EtchDisabledText, &opt, this)) {
					context.palette = palette();
					context.palette.setColor(QPalette::Text, context.palette.light().color());
					painter.save();
					painter.translate(lr.x() + 1, lr.y() + 1);
					painter.setClipRect(lr.translated(-lr.x() - 1, -lr.y() - 1));
					QAbstractTextDocumentLayout *layout = d->control->document()->documentLayout();
					layout->draw(&painter, context);
					painter.restore();
				}

				// Adjust the palette
				context.palette = palette();
				if (foregroundRole() != QPalette::Text && isEnabled())
					context.palette.setColor(QPalette::Text, context.palette.color(foregroundRole()));

				painter.save();
				painter.translate(lr.topLeft());
				painter.setClipRect(lr.translated(-lr.x(), -lr.y()));
				d->control->setPalette(context.palette);
				d->control->drawContents(&painter, QRectF(), this);
				painter.restore();
			} else {
				int flags = align;
				if (d->hasShortcut) {
					flags |= Qt::TextShowMnemonic;
					QStyleOption opt;
					opt.initFrom(this);
					if (!style->styleHint(QStyle::SH_UnderlineShortcut, &opt, this))
						flags |= Qt::TextHideMnemonic;
				}
				style->drawItemText(&painter, lr.toRect(), flags, palette(), isEnabled(), d->text, foregroundRole());
			}
		} else
		#ifndef QT_NO_PICTURE
		
		(...)

	"""
	
#******************************************************************************
#
#******************************************************************************
if __name__ == "__main__":
	
	# for playing around...
	a = QtGui.QApplication(sys.argv)
	QtCore.QObject.connect(a,QtCore.SIGNAL("lastWindowClosed()"),a,QtCore.SLOT("quit()"))
	w = QtGui.QLabel('aaa')
	w.setIndent(39)
	w.setStyleSheet('QLabel {background: yellow; border: 1py solid black}')
	w.setTextFormat(QtCore.Qt.RichText)
	
	PathLabelWrap(w, os.path.join(*[i*5 for i in 'abcdefg']))
	w.show()
	a.exec_()
	
	