
from customeditor import CustomEditor, QtCore, QtGui
from wideeditor import WideEditor
from camelot.view.model_thread import post

class EmbeddedMany2OneEditor( CustomEditor, WideEditor ):
  """Widget for editing a many 2 one relation a a form embedded in another
form.
"""

  def __init__( self, admin = None, parent = None, **kwargs ):
    assert admin != None
    CustomEditor.__init__( self, parent )
    self.admin = admin
    self.layout = QtGui.QHBoxLayout()
    self.entity_instance_getter = None
    self.form = None
    self.setLayout( self.layout )
    self.setEntity( lambda:None, propagate = False )

  def set_value( self, value ):
    value = CustomEditor.set_value( self, value )
    if value:
      self.setEntity( value, propagate = False )

  def setEntity( self, entity_instance_getter, propagate = True ):

    def create_instance_getter( entity_instance ):
      return lambda:entity_instance

    def set_entity_instance():
      entity = entity_instance_getter()
      if entity:
        self.entity_instance_getter = create_instance_getter( entity )
      else:
        self.entity_instance_getter = create_instance_getter( self.admin.entity() )
      return propagate

    post( set_entity_instance, self.update_form )

  def update_form(self, propagate ):
    if self.form:
      self.form.deleteLater()
      self.layout.removeWidget( self.form )

    from camelot.view.proxy.collection_proxy import CollectionProxy

    def create_collection_getter( instance_getter ):
      return lambda:[instance_getter()]

    model = CollectionProxy( self.admin,
                            create_collection_getter( self.entity_instance_getter ),
                            self.admin.getFields )
    self.form = self.admin.create_form_view( '', model, 0, self )
    self.layout.addWidget( self.form )
    if propagate:
      self.emit( QtCore.SIGNAL( 'editingFinished()' ) )