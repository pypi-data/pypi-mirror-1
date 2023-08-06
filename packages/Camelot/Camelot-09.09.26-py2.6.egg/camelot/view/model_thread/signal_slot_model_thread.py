'''
Created on Sep 9, 2009

@author: tw55413
'''
import logging
from copy import copy

from PyQt4 import QtCore

from camelot.view.model_thread import AbstractModelThread, gui_function, model_function, setup_model

logger = logging.getLogger('camelot.view.model_thread.signal_slot_model_thread')

class Task(QtCore.QObject):
  
  finished = QtCore.SIGNAL('finished')
  exception = QtCore.SIGNAL('exception')
  
  def __init__(self, request, name=''):
    QtCore.QObject.__init__(self)
    self._request = request
    self._name = name
    
  def clear(self):
    """clear this tasks references to other objects"""
    self._request = None
    self._name = None
    
  def execute(self):
    try:
      result = self._request()
      import sip
      #print '===', self._name, '==='
      #print self.receivers(QtCore.SIGNAL('finished'))
      #sip.dump(self)
      self.emit(QtCore.SIGNAL('finished'), result )
    except Exception, e:
      logger.error( 'exception caught in model thread', exc_info = e )
      exception_info = (e, '')
      self.emit(QtCore.SIGNAL('exception'), exception_info)
  
class TaskHandler(QtCore.QObject):

  def __init__(self, queue):
    """:param queue: the queue from which to pop a task when handle_task 
    is called"""
    self._queue = queue
    self._tasks_done = []
      
  def handle_task(self):
    task = self._queue.pop()
    if task:
      task.execute()
    # we keep track of the tasks done to prevent them being garbage collected
    # apparently when they are garbage collected, they are recycled, but their
    # signal slot connections seem to survive this recycling.
    # @todo: this should be investigated in more detail, since we are causing 
    #        a deliberate memory leak here
    task.clear()
    self._tasks_done.append(task)
            
def synchronized( original_function ):
  """Decorator for synchronized access to an object, the object should
  have an attribute _mutex which is of type QMutex
  """
  
  from functools import wraps
  
  @wraps( original_function )
  def wrapper(self, *args, **kwargs):
    QtCore.QMutexLocker(self._mutex)
    return original_function(self, *args, **kwargs)
    
  return wrapper
  
class SignalSlotModelThread( QtCore.QThread, AbstractModelThread ):
  """A model thread implementation that uses signals and slots
  to communicate between the model thread and the gui thread
  """
  
  task_available = QtCore.SIGNAL('task_available')

  def __init__( self, setup_thread = setup_model ):
    """
    @param setup_thread: function to be called at startup of the thread to initialize
    everything, by default this will setup the model.  set to None if nothing should
    be done. 
    """
    QtCore.QThread.__init__( self )
    AbstractModelThread.__init__( self, setup_thread )
    self._task_handler = None
    self._mutex = QtCore.QMutex()
    self._request_queue = []
    
  def run( self ):
    self.logger.debug( 'model thread started' )
    self._task_handler = TaskHandler(self)
    self.connect(self, self.task_available, self._task_handler.handle_task, QtCore.Qt.QueuedConnection)
    self._setup_thread()
    self.logger.debug('thread setup finished')
    self.exec_()
    self.logger.debug('model thread stopped')

  @synchronized
  def post( self, request, response = None, exception = None ):
    if response:
      name = '%s -> %s.%s'%(request.__name__, response.im_self.__class__.__name__, response.__name__)
    else:
      name = request.__name__
    task = Task(request, name=name)
    self._request_queue.append(task)
    # QObject::connect is a thread safe function
    if response:
      assert response.im_self
      assert isinstance(response.im_self, QtCore.QObject)
      self.connect(task, QtCore.SIGNAL('finished'), response, QtCore.Qt.QueuedConnection)
    if exception:
      self.connect(task, QtCore.SIGNAL('exception'), exception, QtCore.Qt.QueuedConnection)
    task.moveToThread(self)
    #print 'task created --->', id(task)
    self.emit(self.task_available)

  @synchronized
  @model_function
  def pop( self ):
    """Pop a task from the queue, return None if the queue is empty"""
    if len(self._request_queue):
      task = self._request_queue.pop(0)
      return task
    
  @synchronized
  @gui_function
  def busy( self ):
    """Return True or False indicating wether either the model or the
    gui thread is doing something"""
    app = QtCore.QCoreApplication.instance()
    return app.hasPendingEvents() or len(self._request_queue)
    
  @gui_function
  def wait_on_work(self):
    """Wait for all work to be finished, this function should only be used
    to do unit testing and such, since it will block the calling thread until
    all work is done"""
    app = QtCore.QCoreApplication.instance()
    while self.busy():
      app.processEvents()
      
#    app = QCoreApplication.instance()
#    waiting = True
#    while waiting:
#      waiting = False
#      if app.hasPendingEvents():
#        app.processEvents()
#        waiting = True