.. _doc-delegates:

#############
  Delegates
#############

:Release: |version|
:Date: |today|

:term:`Delegates <delegate>` are a cornerstone of the Qt model/view framework.
A delegate is used to display and edit data from a :term:`model`.

In the Camelot framework, every field of an :term:`Entity` has an associated
delegate that specifies how the field will be displayed and edited.  When a new
form or table is constructed, the delegates of all fields on the form or table
will construct :term:`editors <editor>` for their fields and fill them with
data from the model.  When the data has been edited in the form, the delegates
will take care of updating the model with the new data.

All Camelot delegates are subclasses of :class:`QAbstractItemDelegate`.

Specifying delegates
====================

The use of a specific delegate can be forced by using the ``delegate`` field
attribute.  Suppose ``rating`` is a field of type :ctype:`integer`, then it
can be forced to be visualized as stars::

  from camelot.view.controls import delegates
  
  class Movie(Entity):
    title = Field(Unicode(50))
    rating = Field(Integer)
  
    class Admin(EntityAdmin):
      list_display = ['title', 'rating']
      field_attributes = {'rating':{'delegate':delegates.StarDelegate}}
	
The above code will result in:

.. image:: ../_static/rating.png

If no ``delegate`` field attribute is given, a default one will be taken depending
on the sqlalchemy field type.

Available delegates
===================

All available delegates can be found in :file:`camelot.view.controls.delegates.py`

.. automodule:: camelot.view.controls.delegates
   :members:

Attributes common to most delegates
===================================

**editable** :const:`True` or :const:`False`
  Indicates whether the user can edit the field.

**minimum, maximum**
  The minimum and maximum allowed values for :ctype:`Integer` and
  :ctype:`Float` delegates or their related delegates like the Star delegate.

**choices**
  A function taking as a single argument the object to which the field
  belongs.  The function returns a list of tuples containing for each
  possible choice the value to be stored on the model and the value
  displayed to the user.

  The use of :attr:`choices` forces the use of the ComboBox delegate::

    field_attributes = {'state':{'choices':lambda o:[(1, 'Active'), 
                                                     (2, 'Passive')]}}
	                                                 
**minimal_column_width**
  An integer specifying the minimal column width when this field is 
  displayed in a table view.  The width is expressed as the number of 
  characters that should fit in the column::

    field_attributes = {'name':{'minimal_column_width':50}}
  
  will make the column wide enough to display at least 50 characters.
