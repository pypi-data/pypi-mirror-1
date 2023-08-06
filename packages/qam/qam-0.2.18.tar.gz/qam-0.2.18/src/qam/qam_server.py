"""

The QAM Server executes remote method calls received from a QAMProxy.

**The QAMServer consists of the following classes:**

``qam.qam_server.QAMServer`` :
  The *QAMServer* class provides the basic functions for registering methods and class-instances which could be executed and called by the server.
  Further the QAMServer receives messages (remote-method-calls) from an amqp-queue and passes them the ExecuteMethodThread which executes one method-call.
  
``qam.qam_server.ExecuteMethodThread`` :
  The ExecuteMethodThread is called by the QAMServer and executes one method-call. 
  The QAMServer receives the method-calls and then the QAMServer starts an ExecuteMethodThread for executing the method.
  
``qam.qam_server.PublisherThread`` :
  The PublisherThread sends the result for one method-call back to QAMProxy. The resuls are stored in a queue. 
  The PublisherThread takes continuously a result from the queue and sends it. 
  If the queue is empty, the PublisherThread waits, until a new result is available for sending.

**The QAMServer consists of the following Exceptions:**

``qam.qam_server.QAMMEthodNotFoundException`` :
  This exception signals, that the method the QAMProxy wanted to call isn't registered on the QAMServer. The exception is sent back to QAMProxy as result.

=======
Usage
=======
Register methods
----------------
An example-usage of the QAMServer. The code shows how to register a function.

   >>> from qam.qam_server import QAMServer
   >>> qam_server = QAMServer(hostname="localhost",
   ...                    port=5672,
   ...                    username='guest',
   ...                    password='guest',
   ...                    vhost='/',
   ...                    server_id='qamserver')
   ...
   >>> def adder_function(x, y):    
   ...    return x + y
   ...
   >>> qam_server.register_function(adder_function, 'add')
   ...
   ... # it is also possible to register the adder_function as follows:
   ... # qam_server.register_function(adder_function)
   ... # the method-name for registering in this case is adder_function.__name__
   ...
   >>> qam_server.serve()
   
Register class-instances
------------------------
An example-usage of the QAMServer. The code shows how to register class-instance.

   >>> from qam.qam_server import QAMServer
   >>> qam_server = QAMServer(hostname="localhost",
   ...                    port=5672,
   ...                    username='guest',
   ...                    password='guest',
   ...                    vhost='/',
   ...                    server_id='qamserver')
   ...
   >>> class TestClass():
   ...    def __init__(self):
   ...        pass
   ...    def adder_function(self,a,b):
   ...        return a+b
   ...
   >>> testclass = TestClass()
   >>> qam_server.register_class(testclass,'testclass')
   >>> qam_server.serve()


=======
Classes
=======
"""
__author__ = "christian"
__date__ = "$Aug 14, 2009 8:24:39 PM$"

import thread, sys
from threading import Thread
import time

from amqp_credentials import AMQPCredentials
from carrot.connection import BrokerConnection
from carrot.messaging import Consumer
from carrot.messaging import Publisher
import logging

logger = logging.getLogger('qam.qam_server')


class QAMServer:
  """
  The *QAMServer* class provides the basic functions for registering methods and class-instances which could be executed and called by the server.
  Further the QAMServer receives messages (remote-method-calls) from an amqp-queue and passes them to a thread, which executes the remote-method-calls.

  :param hostname: hostname of the amqp-server
  :param port: port of the amqp-server
  :param username: username for amqp-server
  :param password: password for amqp-server
  :param vhost: virtual host on amqp-server
  :param server_id: see ``server_id``


  *Class-variables of QAMServer:*
  
  ``server_id : string``
    id for QAMServer. 
  ``method_dict : dictionary``
    stores method-registrations {method_name: method}
  ``instance_dict : dictionary``
    stores class-instance-registrations {instance_name: instance}
  ``result_queue : list``
    stores result-messages processed from ExecutionThread
  ``kill : bool``
    tells the serve-function to terminate
  ``finished : bool``
    tells the close-function wether the serve-function has finished or not
  ``closed : bool``
    tells the destructor wether the amqp-connection is closed or not
  """
  def __init__(self,
               hostname="localhost",
               port=5672,
               username='guest',
               password='guest',
               vhost='/',
               server_id='testqamserver',
               serializer='pickle',
               ssl=False):
    self.consumer = None
    self.publisher_thread = None

    """
    Initially the amqp-connection, a consumer and a publisher-thread are being created.
    The publisher-thread sends messages from a given queue (result_queue) to a specified queue.
    """
    logger.debug('Init QAMServer')
    self.server_id = server_id
    self.method_dict = {}
    self.instance_dict = {}
    self.result_queue = []
    self.kill = False
    self.finished = False
    self.closed = False
    self.serializer = serializer

    self.amqp_credentials = AMQPCredentials(hostname=hostname,
                                            port=port,
                                            username=username,
                                            password=password,
                                            vhost=vhost,
                                            ssl=ssl)

    self.amqpconn = BrokerConnection(hostname=hostname,
                                   port=port,
                                   userid=username,
                                   password=password,
                                   virtual_host=vhost,
                                   ssl=ssl)

    self.consumer = Consumer(connection=self.amqpconn,
                             queue=server_id + '_server_queue',
                             exchange=server_id + '_server_exchange',
                             routing_key=server_id + '_server_routing_key')

    self.publisher_thread = PublisherThread(amqp_credentials=self.amqp_credentials,
                                            result_queue = self.result_queue,
                                            server_id= self.server_id,
                                            serializer = self.serializer)
    self.publisher_thread.setDaemon(True)
    self.publisher_thread.start()

  def __del__(self):
    if not self.closed: self.close()

  def register_function(self, method, name=None):
    """
    Methods that should be available on the server for calling, are registered with this function.
    Each method is being stored in a dictionary (method_dict), where the name of the method is the key, and the value is the method itself.

    :param method: method to register on server
    :param name: if a name is given, the method is being registered with this name, else the method is registered with method.__name__
    :type name: String or None
    """

    logger.debug('should register method %s with name %s ' % (method.__name__, name))
    if name != None:
      logger.debug('register method with name %s' % name)
      self.method_dict[name] = method
    else:
      logger.debug('register method with name %s' % method.__name__)
      self.method_dict[method.__name__] = method

  def register_class(self,instance,name):
    """
    Class-instances which should be available for calling, are registered with this function.
    Each class-instance is being stored in a dictionary (instance_dict), where the key is the name given and the value is the instance itself.
    No methods for this instance are stored because they could be reached with the function getattr for any given class.

    :param instance: class-instance which should be registered
    :param name: with this name the instance is being registered
    """
    self.instance_dict[name] = instance

  def close(self):
    """
    The consumer, the publisher and the amqp-connection are being closed.
    The serve-function terminates (kill-signal is set to True).
    """
    if self.closed: return
    
    self.kill = True
    while not self.finished: pass
    self.consumer.close()
    self.publisher_thread.close()
    self.amqpconn.close()
    self.closed = True;
    


  def serve(self):
    """
    The serve-function fetches messages (method-calls) from the amqp-queue.
    Each message is being executed by the ExecuteMethodThread, who calls the function and returns the result.
    """
    while not self.kill:
    #def execute_method(message_data, message):
        try:
          message = self.consumer.fetch()
          if message != None:
                message_data = message.payload
                message.ack()
                execute_method_thread = ExecuteMethodThread(self.result_queue,
                                                      message_data,
                                                      self.method_dict,
                                                      self.instance_dict,
                                                      self.serializer)
                execute_method_thread.start()
          else:
                time.sleep(0.1)
        except Exception:
            try:
                logger.exception('Exception: Connection Lost during fetch')
                self.amqpconn.close()
                time.sleep(1)
                self.amqpconn = BrokerConnection(hostname=self.amqp_credentials.hostname,
                                       port=self.amqp_credentials.port,
                                       userid=self.amqp_credentials.username,
                                       password=self.amqp_credentials.password,
                                       virtual_host=self.amqp_credentials.vhost,
                                       ssl=self.amqp_credentials.ssl)
                #self.consumer.close()

                self.consumer = Consumer(connection=self.amqpconn,
                                 queue=self.server_id + '_server_queue',
                                 exchange=self.server_id + '_server_exchange',
                                 routing_key=self.server_id + '_server_routing_key')
            except Exception, e:
                logger.exception('Exception: during reconnection')

    self.finished = True



class ExecuteMethodThread(Thread):
  """
  The role of the ExecuteMethodThread is calling defined methods and creating messages out of the results, which could be send.
  Messages are stored in the a queue (result_queue) for further processing.
  
  :param result_queue: see ``result_queue``
  :param message_data: see ``message_data``
  :param method_dict: see ``method_dict``
  :param instance_dict: see ``instance_dict``
  
  *Class-variables of ExecuteMethodThread:*

  ``result_queue : list``
    result_queue from parent QAMServer. Results are stored in this list, after executing a specified method.
  ``message_data : dictionary``
    sturcture of the message.
  ``method_dict : dictionary``
    method_dict from parent QAMServer. All registered methods are stored in here.
  ``instance_dict : dictionary``
    instance_dict from parent QAMServer. All registered instances are stored in here.



  """

  def __init__ (self, result_queue, message_data, method_dict, instance_dict, serializer):
    Thread.__init__(self)
    self.result_queue = result_queue
    self.message_data = message_data
    self.method_dict = method_dict
    self.instance_dict = instance_dict
    self.serializer = serializer
   
  def run(self):
    """
    The run-method takes messages, and processes them.
    Content of a message is a simple method call, or a method-call of a given instance.
    For calling the method, it is necessary, that the message is registered on the QAMServer. A method-call of a non-registered method or instance.method throws an exception.
    The result of the call is packed into a message and stored in a queue (result_queue).

    """
    logger.debug('Start Run')
    method_name = self.message_data['method_name']
    params = self.message_data['params']
    routing_key = self.message_data['routing_key']
    id = self.message_data['id']
    result_record = {}

    try:

      if method_name.find('.') == -1:
        # in case a simple method is being called
        logger.debug('in Method Call')
        if method_name not in self.method_dict:
            logger.debug('MethodNotFoundException should be raised')
            raise MethodNotFoundException()
        result = self.method_dict[method_name](*params)
      else:
        # in case instance.method_name is being called
        execution_list = method_name.split('.')
        instance_name = execution_list[0]
        method_name = execution_list[1]

        if instance_name not in self.instance_dict:
          raise MethodNotFoundException()

        instance = self.instance_dict[instance_name]

        if not hasattr(instance,method_name):
          raise MethodNotFoundException

        result = getattr(instance,method_name)(*params)

    # internal exception
    except MethodNotFoundException, e:
      logger.debug('catched MethodNotFoundException')
      result_message = {'id':id, 'result':'Methodname %s is not registered on QAMServer' % method_name, 'exception':True, 'internal_exception':1}
    # external exception
    except:
      logger.debug('Exception happend')
      t,v =  sys.exc_info()[:2]
      
      sys.exc_clear()

      if self.serializer == 'pickle':
          logger.debug('pickle: catched exception: %s' % repr(v))
          result_message = {'id':id, 'result':v, 'exception':True, 'internal_exception':-1}
      else:
          logger.debug('json: catched exception: %s' % repr(v.args))
          result_message = {'id':id, 'result':v.args, 'exception':True, 'internal_exception':-1}

    # no exception
    else:
      result_message = {'id':id, 'result':result, 'exception':False, 'internal_exception':-1}

    result_record = {'result_message':result_message, 'routing_key':routing_key}
    self.result_queue.append(result_record)
    logger.debug('Method Queue: %s' % repr(self.result_queue))

class PublisherThread(Thread):
  """
  The PublisherThread sends given messages from a queue back to the caller proxy.

  :param amqp_credentials: see ``amqp_credentials``
  :param result_queue: see ``result_queue``
  :param server_id: see ``server_id``

  *Class-variables of PublisherThread:*

  ``amqp_credentials : qam.amqp_credentials.AMQPCredentials``
    all necessary stuff for creating a amqp-connection ist stored in here.
  ``result_queue : list``
    result_queue from parent QAMServer. Messages are taken from this queue and sent back to the caller proxy.
  ``server_id : string``
    id for QAMServer.
  ``amqpconn : carrot.connection.AMQPConnection``
    AMQP-Connection for the PublisherThread
  ``kill : bool``
    The kill signal tells the PublisherThread to stop sending messages.
  """

  def __init__ (self, amqp_credentials, result_queue, server_id, serializer):
    Thread.__init__(self)
    self.amqp_credentials = amqp_credentials
    self.result_queue = result_queue
    self.server_id = server_id
    self.amqpconn = BrokerConnection(hostname=self.amqp_credentials.hostname,
                                   port=self.amqp_credentials.port,
                                   userid=self.amqp_credentials.username,
                                   password=self.amqp_credentials.password,
                                   virtual_host=self.amqp_credentials.vhost,
                                   ssl=self.amqp_credentials.ssl)
    self.kill = False
    self.serializer = serializer

  def close(self):
    """
    The PublisherThread is being stopped (kill-signal is set to True)
    """
    self.kill = True
    self.join()

  def run(self):
    """
    Messages from the given queue (result_queue) are sent back to a specified amqp-queue.
    """
    while not self.kill:
      if len(self.result_queue) == 0:
        time.sleep(0.1)
        continue
      result_record = self.result_queue.pop(0)
      logger.debug('popped message from queue: %s' % repr(result_record['result_message']))
      routing_key = result_record['routing_key']
      logger.debug('create Publisher')
      logger.debug('Serialization: %s' % self.serializer)
      try:
        publisher = Publisher(connection=self.amqpconn,
                                exchange=self.server_id + "_client_exchange",
                                routing_key=routing_key,
                                serializer=self.serializer)
        logger.debug('created Publisher')
      
        publisher.send(result_record['result_message'])
        logger.debug('sent message: %s' % repr(result_record['result_message']))
      except Exception:
         logger.exception('Exception: Connection lost during send')
         self.result_queue.insert(0, result_record)
         self.amqpconn.close()
         time.sleep(1)
         self.amqpconn = BrokerConnection(hostname=self.amqp_credentials.hostname,
                                   port=self.amqp_credentials.port,
                                   userid=self.amqp_credentials.username,
                                   password=self.amqp_credentials.password,
                                   virtual_host=self.amqp_credentials.vhost,
                                   ssl=self.amqp_credentials.ssl)
      publisher.close()
      logger.debug('publisher closed')


class MethodNotFoundException(Exception):
  """
  Internal QAMServer Exception, which is thrown, if a non-registered method is being called.
  """
  pass


