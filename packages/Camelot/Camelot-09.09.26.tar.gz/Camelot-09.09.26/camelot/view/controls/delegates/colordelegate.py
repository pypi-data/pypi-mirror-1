
from customdelegate import *
from camelot.core.utils import variant_to_pyobject

class ColorDelegate(CustomDelegate):
  
  __metaclass__ = DocumentationMetaclass
  
  editor = editors.ColorEditor
  
  def paint(self, painter, option, index):
    painter.save()
    self.drawBackground(painter, option, index)
    background_color = QtGui.QColor(index.model().data(index, Qt.BackgroundRole))
    if (option.state & QtGui.QStyle.State_Selected):
      painter.fillRect(option.rect, option.palette.highlight())
    elif not self.editable:
      painter.fillRect(option.rect, QtGui.QColor(not_editable_background))
    else:
      painter.fillRect(option.rect, background_color)
    color = variant_to_pyobject(index.model().data(index, Qt.EditRole))
    if color:
      pixmap = QtGui.QPixmap(16, 16)
      qcolor = QtGui.QColor()
      qcolor.setRgb(*color)
      pixmap.fill(qcolor)
      rect = QtCore.QRect(option.rect.left()+40,
                        option.rect.top(),
                        option.rect.width()-23,
                        option.rect.height())
      
      QtGui.QApplication.style().drawItemPixmap(painter,
                                                rect,
                                                Qt.AlignVCenter,
                                                pixmap)
      
    painter.restore()
