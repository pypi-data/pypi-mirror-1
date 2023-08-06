"""
The QAMProxy sends method-calls to a QAMServer-instance and receives the results.
It is possible to register a callback-method on the proxy.
This method is  called when a result for a specific method-call is available.

**The QAMProxy consists of the following classes:**

``qam.qam_proxy.QAMProxy`` :
  This class manages the start of:
  
    - ConsumerThread
    - PublisherThread
    - CallbackObserverThread

  The PublisherThread runs in an infinite-loop and sends continuously messages to the QAMServer.
  The messages which are send to the QAMServer are stored in a method_queue.

  The ConsumerThread receives continuously messages from the QAMServer and signals that a message has arrived.
  If a callback is registered the ConsumerThread signals the CallbackObserverThread that a message has arrived, else it signals the QAMProxy that the message has arrived.

  The CallbackObserverThread checks continuously if it is time to execute a callback-method.
  A callback-method is executed if a callback-method is registered and the ConsumerThread signals that a result has arrived.
``qam.qam_proxy.ConsumerThread`` :
  The ConsumerThread receives continuously messages from the QAMServer and signals that a message has arrived.
  Therefor it is necessary to keep track of all remote-method-calls ever send to the QAMServer.
  The ConsumerThread keeps a list with all QAMServer calls, that haven't received a result yet, so it is possible to relate a result to a caller.
  This list consists of "slots". A slot is identified by an id.
  The slot is reserved if the caller is still waiting on a message and the slot with the given id is being freed if the result has arrived.
``qam.qam_proxy.PublisherThread`` :
  The PublisherThread runs in an infinite-loop and sends continuously messages to the QAMServer.
  Therefor he keeps a queue (``method_queue``) so that every method which is not sent yet, isn't loosed.
  If the queue is empty, the PublisherThread waits until a new message arrives the queue.
``qam.qam_proxy.CallbackObserverThread`` :
  The CallbackObserverThread checks continuously if it is time to execute a callback-method.
  If a callback-method is registered and a result arrived in the ConsumerThread, the CallbackObserverThread will be informed about it.
  Then the he checks wether an error occourred on the QAMServer or not.
  If no error occoured the callback-method which is registered for this request is being called with the result from the QAMServer as parameter.
  If an error occoured and a error-method is registered this method will be called, with the exception as parameter.
  Else a log-message will be written into the logfiles.
  It is the job of the ExecuteCallbackThread to call the callback-methods, otherwise the CallbackObserverThread would block.

``qam.qam_proxy.ExecuteCallbackThread`` :
  The ExecuteCallbackThread receives a method and parameters from the CallbackObserverThread.
  The job of the ExecuteCallbackThread is to execute this method.

``qam.qam_proxy.Callback`` :
  This Class is used to realize the callback-mechanism.
``qam.qam_proxy._Method`` :
  This Class is used to realize the remote-method-call.


**The QAMProxy consists of the following Exceptions:**

``qam.qam_proxy.QAMException`` :
  This is the class for internal exceptions. An internal exception would be everything raised by the QAMServer.
``qam.qam_proxy.QAMMEthodNotFoundException`` :
  This exception is created, if the method called by the QAMProxy isn't registerd on the QAMServer.

=======
Usage
=======

Calling a method without callback
---------------------------------
An example-usage of the QAMProxy. The code shows how to call a method that is registered on QAMServer.

   >>> from qam.qam_proxy import QAMProxy, QAMMethodNotFoundException, QAMException
   >>> qam_proxy = QAMProxy(hostname="localhost",
   ...                    port=5672,
   ...                    username='guest',
   ...                    password='guest',
   ...                    vhost='/',
   ...                    server_id='qamserver',
   ...                    client_id='qamproxy')
   ...
   >>> result = qam_proxy.add(2,3) # name of method registered on QAMServer
   >>> qam_proxy.close()
   
Calling a method with callback
------------------------------
An example-usage of the QAMProxy with callback functions.

   >>> from qam.qam_proxy import QAMProxy, QAMMethodNotFoundException, QAMException
   >>> qam_proxy = QAMProxy(hostname="localhost",
   ...                    port=5672,
   ...                    username='guest',
   ...                    password='guest',
   ...                    vhost='/',
   ...                    server_id='qamserver',
   ...                    client_id='qamproxy')
   ...
   ... # defining functions for callback
   >>> def success(arg):
   ...    print arg
   >>> def error(arg):
   ...    # if an error occours on QAMServer
   ...    print arg 
   >>> uid = qam_proxy.callback(success, error).adder_function(2,4)
   >>> while True:
   ...    state = qam_proxy.get_callback_state(uid)
   ...    if state == 2 :
   ...        # execution of callback finished
   ...        break
   ...
   >>> qam_proxy.close()
   
 
Calling a registered Class
------------------------------
An example-usage of the QAMProxy for calling a registered class-instance on QAMServer.

   >>> from qam.qam_proxy import QAMProxy, QAMMethodNotFoundException, QAMException
   >>> qam_proxy = QAMProxy(hostname="localhost",
   ...                    port=5672,
   ...                    username='guest',
   ...                    password='guest',
   ...                    vhost='/',
   ...                    server_id='qamserver',
   ...                    client_id='qamproxy')
   ...
   >>> result = qam_proxy.testclass.adder_function(2,4)
   >>> qam_proxy.close()

=======
Classes
=======
"""
import copy
import logging
import thread
from threading import Thread
import time
import uuid

from amqp_credentials import AMQPCredentials
from carrot.connection import BrokerConnection
from carrot.messaging import Consumer
from carrot.messaging import Publisher

logger = logging.getLogger('qam.qam_proxy')


#===========================================================================
class QAMProxy:
    """
    The role of the QAMProxy is sending messages to a specific QAMServer.
    Instead of waiting on the message it is also possible to register a callback-method which is being called if a result from QAMServer has arrived.
    The QAMProxy manages the start of ConsumerThread, PublisherThread an CallbackObserverThread.

    :param server_id: id of the QAMServer, for reaching the right queue
    :param hostname: hostname where amqp-server is running
    :param port: port for amqp-server
    :param username: username for amqp-server
    :param password: password for amqp-server
    :param vhost: virtual host of amqp-server
    :param client_id: see ``client_id``

    *Class-variables of QAMProxy:*

    ``amqp_credentials : qam.amqp_credentials.AMQPCredentials``
        all necessary stuff for creating a amqp-connection ist stored in here.
    ``consumer_thread : qam.qam_proxy.ConsumerThread``
        Thread for receiving messages from QAMServer.
    ``publisher_thread : qam.qam_proxy.PublisherThread``
        Thread for sending messages to a QAMServer
    ``callback_observer_thread : qam.qam_proxy.CallbackObserverThread``
        Thread for calling the callback-functions when a result is available
    """
    closed = False
    def __init__(self,
                 server_id,
                 hostname="localhost",
                 port=5672,
                 username='guest',
                 password='guest',
                 vhost='/',
                 client_id=None,
                 serializer='pickle',
                 ssl=False):
        self.publisher_thread = None
        self.consumer_thread = None
        self.callback_observer_thread = None
        
        if client_id == None:
            self.client_id = str(uuid.uuid4())
        else:
            self.client_id = client_id

        logger.info('Init QAMProxy')
        self.serializer = serializer

       

      
        self.amqp_credentials = AMQPCredentials(hostname=hostname,
                                                port=port,
                                                username=username,
                                                password=password,
                                                vhost=vhost,
                                                ssl=ssl)

        
        logger.debug('Pre Consumer Thread init')
        self.consumer_thread = ConsumerThread(amqp_credentials=self.amqp_credentials,
                                              server_id=server_id,
                                              client_id=self.client_id,
                                              serializer=self.serializer)
        logger.debug('After Consumer Thread Init')
        self.publisher_thread = PublisherThread(amqp_credentials=self.amqp_credentials,
                                                server_id=server_id,
                                                client_id=self.client_id,
                                                serializer=self.serializer)
        
        logger.debug('After Publisher Thread Init')
        self.callback_observer_thread = CallbackObserverThread(self)
        logger.debug('After CallbackObserver Thread Init')

        self.consumer_thread.setDaemon(True)
        self.publisher_thread.setDaemon(True)
        self.callback_observer_thread.setDaemon(True)
    
        self.consumer_thread.start()
        logger.debug('After Consumer Thread Start')
        self.publisher_thread.start()
        logger.debug('After Publisher Thread Start')
        self.callback_observer_thread.start()
        logger.debug('After CallbackObserver Thread Start')

    def __del__(self):
        self.close()

    def close(self):
        """
        The PublisherThread, the ConsumerThread and the CallbackObserverTrhead are being stopped (kill-signal set to True).
        """
        if self.closed == True: return
        
        if self.publisher_thread != None:
            self.publisher_thread.exit()
        if self.consumer_thread != None:
            self.consumer_thread.exit()
        if self.callback_observer_thread != None:
            self.callback_observer_thread.exit()
        self.closed = True
    
    def callback(self, callback_method, exception_method=None):
        """
        The callback-function registers a callback-method and an exception-method if an exception-method is given.

        :param callback_method: the function that should be called
        :param exception_method: exception_method
        :type exception_method: function or None
        :type callback_method: function
        :rtype: callable ``qam.qam_proxy.Callback``-instance
        """
        if self.callback_method is not None and self.exception_method is None:
            logger.warning('Method has NO exception_method defined. \
                      In case of an Exception on the Server you WILL NOT\
                      get notified!')
        id = self.consumer_thread.get_free_result_list_id(callback_method, exception_method)
        return Callback(self, id, self.client_id)

    def set_timeout(self, timeout):
        """
        The set_timeout-function sets a timeout in seconds and returns a callable
        class where the remote function can be called. If a timeout occurs a
        QAMTimeoutException is raised.

        :param timeout: timeout value in seconds
        :type timeout: integer
        :rtype: callable ``qam.qam_proxy.SynchronTimeout``-instance
        """
        
        return SynchronTimeout(self, self.client_id, timeout)


    def get_num_waiting_callbacks(self):
        """
        This function returns the number of callacks which are waiting for a result from QAMServer.

        :rtype: number of callbacks not executed yet
        """

        return len(self.callback_observer_thread.callback_uid_dict)

    def get_callback_state(self, uid):
        """
        Returns the state of the callback method registered for a specific uid.

        :rtype: state of the callback:

          - 0 = waiting for processing
          - 1 = processing
          - 2 = finished
        """
        item = self.callback_observer_thread.get_callback_item(uid)
        if item is None:
            state = 2
        else:
            state = item['state']
        return state
  

    def __request(self, methodname, params):
        """
        The remote-method-call is packed into a message and the message is stored in a sending-queue.
        A PublisherThread sends the messages to the AMQPServer.
        This function waits, until a result from the QAMServer arrives.

        :param methodname: name of the method that should be executed on the QAMServer
        :param params: parameter for the remote-method-call
        :type methodname: string
        :type param: list of parameters
        :rtype: result received from QAMServer
        """
        logger.debug('Request: ' + repr(methodname) + '; Params: '+ repr(params))
        id = self.consumer_thread.get_free_result_list_id()
        #assemble message structure (dict) and send message
        self.publisher_thread.add_message_to_send({'id':id,
                                                  'method_name': methodname,
                                                  'routing_key': self.client_id + '_client_routing_key',
                                                  'params': params})

        #loop until result is in list and then return
        while True:
            if self.consumer_thread.is_result_received(id):
                return self.consumer_thread.get_result(id)
            else:
                time.sleep(0.1)

    def __getattr__(self, name):
        """
        This method is invoked, if a method is being called, which doesn't exist on QAMProxy.
        It is used for RPC, to get the function which should be called on the QAMServer.
        """
        # magic method dispatcher
        logger.debug('Recursion: ' + name)
        return _Method(self.__request, name)


class Callback:
    """
    The class Callback is callable. It is used to realize the callback-mechanism.

    :param parent: instance of QAMProxy
    :param id: id of slot in the result-list
    :param client_id: used for routing-key generation
    """
    def __init__(self, parent, id, client_id):
        self.id = id
        self.client_id = client_id
        self.parent = parent
        self.timeout = None

    def set_timeout(self, timeout):
        """
        This method is for setting a timeout for a asynchronous remote method call.
        If the timeout happens before the callback function is called a
        QAMTimeoutException will be passed to the registered error function.

        :param timeout: the timeout in seconds
        :type timeout: integer

        """
        self.timeout = timeout
        return self
        
    
    def __request(self, methodname, params):
        """
        This function is only used, if a callback-function is registered on QAMProxy. The original remote-method-call is packed into a message and stored in a sending-queue.
        A PublisherThread sends the message to the AMQP-Server.
        The CallbackObserverThread is being told to wait for a result from the QAMServer and calls the callback-function when a result arrives.

        :param methodname: name of the method that should be called on the QAMServer
        :param params: parameters for the remote-method-call
        :type methodname: string
        :type params: list of parameters

        :rtype: an uid to identify the acutal callback, necessary for telling the actual state of the callback (waiting,processing,finished)
        """
   

        #assemble message structure (dict) and send message
        self.parent.publisher_thread.add_message_to_send({'id':self.id,
                                                         'method_name': methodname,
                                                         'routing_key': self.client_id + '_client_routing_key',
                                                         'params': params})


        uid = self.parent.callback_observer_thread.init_waiting_callback_item(self.id, self.timeout)
    
        return uid
    
    def __getattr__(self, name):
        # magic method dispatcher
        """
        This method is invoked, if a method is being called, which doesn't exist in the Callback-class.
        It is used for RPC, to get the function which should be called on the QAMServer.
        """
        return _Method(self.__request, name)

#===========================================================================
class SynchronTimeout:
    """
    The class SynchronTimeout is callable. It is used to realize the synchronous
    Timeout-mechanism.

    :param parent: instance of QAMProxy
    :param client_id: used for routing-key generation
    :param timeout: timeout in seconds
    """
    def __init__(self, parent, client_id, timeout):
        self.client_id = client_id
        self.parent = parent
        self.timeout = timeout

    def __request(self, methodname, params):
        """
        The remote-method-call is packed into a message and the message is stored in a sending-queue.
        A PublisherThread sends the messages to the AMQPServer.
        This function waits, until a result from the QAMServer arrives or
        if a timeout occours a QAMTimeoutException gets raised.

        :param methodname: name of the method that should be executed on the QAMServer
        :param params: parameter for the remote-method-call
        :type methodname: string
        :type param: list of parameters
        :rtype: result received from QAMServer
        """
        id = self.parent.consumer_thread.get_free_result_list_id()
        #assemble message structure (dict) and send message
        self.parent.publisher_thread.add_message_to_send({'id':id,
                                                         'method_name': methodname,
                                                         'routing_key': self.client_id + '_client_routing_key',
                                                         'params': params})
        start_time = time.time()
        #loop until result is in list and then return, or if timeout occours
        #raise QAMTimeoutException
        while True:
            curr_time = time.time()
            if curr_time - start_time > self.timeout:
                self.parent.consumer_thread.free_result_item(id)
                raise QAMTimeoutException('Timeout happened during a call of %s' % methodname)
            if self.parent.consumer_thread.is_result_received(id):
                return self.parent.consumer_thread.get_result(id)
            else:
                time.sleep(0.1)

    def __getattr__(self, name):
        # magic method dispatcher
        """
        This method is invoked, if a method is being called, which doesn't exist in the SynchronTimeout-class.
        It is used for RPC, to get the function which should be called on the QAMServer.
        """
        return _Method(self.__request, name)

#===========================================================================

class _Method:
    """
    The _Method-class is used to realize remote-method-calls.
    :param send: name of the function that should be executed on QAMProxy
    :param name: name of the method which should be called on the QAMServer
    """
    # some magic to bind an XML-RPC method to an RPC server.
    # supports "nested" methods (e.g. examples.getStateName)
    def __init__(self, send, name):
        self.__send = send
        self.__name = name
    def __getattr__(self, name):
        return _Method(self.__send, "%s.%s" % (self.__name, name))
    def __call__(self, * args):
        return self.__send(self.__name, args)

#===========================================================================
class ConsumerThread(Thread):
    """
    The ConsumerThread receives messages from the QAMServer.
    When a message arrives, the result is stored in the result_list, identified by the id.
    Further the specific entry in the result_list gets the state *DONE*.

    Structure of the received message:
    
        - "id": integer
        - "result": result of method-call
        - "exception": bool
        - "internal_exception": integer


    :param amqp_credentials: all necessary stuff for creating a amqp-connection ist stored in here.
    :param server_id: see ``server_id``
    :param client_id: see ``client_id``

    *Class-variables of ConsumerThread:*

    ``free_index_queue : list``
        Free slots (ids) from the result_list are stored in the free_index_queue.
    ``result_list : list``
        The result_list stores the result and a state for a remote-method-call identified by an id.
        Before receiving the result the specific slot for a remote-method-call in the result_list has the state *WAITING*.
        After receiving the slot gets the state *DONE*.
    ``server_id : string``
        server_id received from parent QAMProxy. Used for amqp-connection to the server.
    ``client_id : string``
        client_id received from parent QAMProxy. Used for defining routing-key and amqp-queue-name
    ``kill : bool``
        The kill signal tells the ConsumerThread to stop receiving messages.
    ``amqpconn : carrot.connection.AMQPConnection``
        AMQPConnection for the ConsumerThread
    ``consumer : carrot.messaging.Consumer``
        AMQPConsumer for the ConsumerThread. The AMQPConsumer receives the messages sent by the QAMServer
    """
    (WAITING, DONE, FREE) = range(3)
    def __init__(self, amqp_credentials, server_id, client_id, serializer):
        Thread.__init__(self)
        self.free_index_queue = []
        self.result_list = []
        self.server_id = server_id
        self.client_id = client_id
        self.kill = False
        self.serializer = serializer
        self.amqp_credentials = amqp_credentials
        try:
            self.amqpconn = BrokerConnection(hostname=amqp_credentials.hostname,
                                       port=amqp_credentials.port,
                                       userid=amqp_credentials.username,
                                       password=amqp_credentials.password,
                                       virtual_host=amqp_credentials.vhost,
                                       ssl=amqp_credentials.ssl)
            self.amqpconn.connect()
        except Exception:
            logger.exception('Init BrokerConnection in ConsumerThread')
            raise
        try:
            self.consumer = Consumer(connection=self.amqpconn,
                                 queue=client_id + '_client_queue',
                                 exchange=server_id + '_client_exchange',
                                 routing_key=client_id + '_client_routing_key')
        except Exception:
            logger.exception('Init Consumer in ConsumerThread')
            raise

    def get_result_item(self, id):
        """
        This function returns the result from the result_list, for a specific id.

        :param id: id for the desired result_list "slot"
        :type id: integer
        :rtype: result for a specific id
        """
        return self.result_list[id]

    def get_result(self, id):
        """
        This function is a high level function for getting the result of
        the remote method call. It makes several checks to validate the result
        against Exceptions and raises them if any occoured

        Exceptions:
            - QAMMethodNotFoundException: gets raised when the method
              on the server is not found
            - Exception: is raised when a user defined exception is raised on
              the server.


        :param id: id for the desired result
        :type id: integer
        :rtype: result for a specific id
        """
        result_item = self.get_result_item(id)
        result = result_item['result_message']
        self.free_result_item(id)

        if result['exception'] == True:
            if result['internal_exception'] > 0:
                raise QAMMethodNotFoundException(result['result'])
            else:
                if self.serializer == 'pickle':
                    logger.debug("Consumerthread: pickle result: %s" % repr(result['result']))
                    raise result['result']
                else:
                    logger.debug("ConsumerThread: json result: %s " % repr(result['result']))
                    raise Exception(*result['result'])
        else:
            return result['result']

    def is_result_received(self, id):
        """
        This function checks, if a desired result from the QAMServer is already received.

        :param id: id for checking the state in the result_list.
        :type id: integer
        :rtype: True if the message is already received, else False
        """
        if self.result_list[id]['state'] == ConsumerThread.DONE:
            return True
        else:
            return False

    
    def free_result_item(self, id):
        """
        This function frees a specific result_list "slot".

        :param id: id of the slot to free
        :type id: integer
        """
        self.result_list[id]['state'] = ConsumerThread.FREE
        self.free_index_queue.append(id)

    def get_free_result_list_id(self, callback_method=None, exception_method=None):
        """
        This method assigns a free slot to a new request. The new request is appended to result_list with the state *WAITING*.

        :param callback_method: name of the method to call when result arrives
        :param exception_method: name of the method to call if an exception occured on the QAMServer
        :type callback_method: function or None
        :type exception_method: function or None
        :rtype: id of the assigned slot
        """

        blank_record = {'result_message':None,
            'state':ConsumerThread.WAITING,
            'callback_method': callback_method,
            'exception_method': exception_method
            }

        queue_lock = thread.allocate_lock()
        queue_lock.acquire()
   
        if len(self.free_index_queue) > 0:
            id = self.free_index_queue.pop(0)
            queue_lock.release()
            self.result_list[id] = blank_record
        else:
            queue_lock.release()
            lock = thread.allocate_lock()
            lock.acquire()
            self.result_list.append(blank_record)
            id = len(self.result_list) - 1
            lock.release()
        return id

    def exit(self):
        """
        The exit method terminates the ConsumerThread and closes the amqp-consumer and the amqp-connection of the ConsumerThread.
        """
        self.kill = True
        self.join()
        self.consumer.close()
        self.amqpconn.close()
    
    def run(self):
        """
        Messages are received from QAMServer and stored in the result_list. T
        he state in the result_list for specific results is set *DONE*.
        """
        while not self.kill:
            try:
                message = self.consumer.fetch()
                if message != None:
                    message.ack()
                    message_data = message.payload
                    result_id = message_data['id']

                    if self.result_list[result_id]['state'] != ConsumerThread.FREE:
                        self.result_list[result_id]['result_message'] = message_data
                        self.result_list[result_id]['state'] = ConsumerThread.DONE
                else:
                    time.sleep(0.1)

            except Exception:
                try:
                    logger.exception('Exception: Lost Connection during Fetch in Consumer Thread')
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
                                     queue=self.client_id + '_client_queue',
                                     exchange=self.server_id + '_client_exchange',
                                     routing_key=self.client_id + '_client_routing_key')
                except Exception:
                    logger.exception('Exception: during reconnect')
#===========================================================================
class PublisherThread(Thread):
    """
    The PublisherThread takes messages from the method_queue and sends them to the QAMServer.
    The method_queue is filled by ``qam.qam_proxy.QAMProxy.__request`` and by ``qam.qam_proxy.Callback.__request``.

    :param amqp_credentials: see ``amqp_credentials``
    :param server_id: see ``server_id``
    :param client_id: see ``client_id``

    *Class-variables of PublisherThread:*

    ``amqp_credentials : qam.amqp_credentials.AMQPCredentials``
        all necessary stuff for creating a amqp-connection ist stored in here.
    ``server_id : string``
        server_id received from parent QAMProxy. Used for amqp-connection to the server.
    ``client_id : string``
        client_id received from parent QAMProxy. Used for defining routing-key and amqp-queue-name
    ``kill : bool``
        The kill signal tells the PublisherThread to stop receiving messages.
    ``method_queue : list``
        All requests for a method-call on the QAMServer are stored in the method_queue.
    ``publisher : carrot.messaging.Publisher``
        The publisher sends messages to the QAMServer.
    """

    def __init__(self, amqp_credentials, server_id, client_id, serializer):
        Thread.__init__(self)
        self.server_id = server_id
        self.client_id = client_id
        self.method_queue = []
        self.amqp_credentials = amqp_credentials
        self.kill = False
        self.serializer = serializer

    def add_message_to_send(self, message):
        """
        A new message is appended to the method_queue. All messages that are stored in the method_queue are sent to the QAMServer.

        :param message: the message which should be appended.
        :type message: dictionary

        The structure of the message is as follows:
          - "id": integer
          - "method_name": string
          - "routing_key": string
          - "params": list
        """
        self.method_queue.append(message)
  
    def exit(self):
        """
        The exit method terminates the PublisherThread and closes the publisher and the amqp-connection
        """
        self.kill = True
        self.join()
        self.publisher.close()
        self.amqpconn.close()

    def run(self):
        """
        The run method sends messages which are stored in the method_queue to the QAMServer.
        """
        self.amqpconn = BrokerConnection(hostname=self.amqp_credentials.hostname,
                                       port=self.amqp_credentials.port,
                                       userid=self.amqp_credentials.username,
                                       password=self.amqp_credentials.password,
                                       virtual_host=self.amqp_credentials.vhost,
                                       ssl=self.amqp_credentials.ssl)

        logger.debug('Serialization: %s' % self.serializer)
        self.publisher = Publisher(connection=self.amqpconn,
                                   exchange=self.server_id + "_server_exchange",
                                   routing_key=self.server_id + "_server_routing_key",
                                   serializer=self.serializer)
    
        while self.kill == False:
            if len(self.method_queue) == 0:
                time.sleep(0.1)
                continue
            method_message = self.method_queue.pop(0)
            try:
                self.publisher.send(method_message)
            except Exception, e:
                logger.exception('Exception: During sending.')
                self.method_queue.insert(0, method_message)
                try:
                    self.amqpconn.close()
                    time.sleep(1)
                    self.amqpconn = BrokerConnection(hostname=self.amqp_credentials.hostname,
                                   port=self.amqp_credentials.port,
                                   userid=self.amqp_credentials.username,
                                   password=self.amqp_credentials.password,
                                   virtual_host=self.amqp_credentials.vhost,
                                   ssl=self.amqp_credentials.ssl)

                    #self.publisher.close()

                    self.publisher = Publisher(connection=self.amqpconn,
                                   exchange=self.server_id + "_server_exchange",
                                   routing_key=self.server_id + "_server_routing_key",
                                   serializer=self.serializer)
                except Exception:
                    logger.exception('Exception: During connection a broken AMQP Connection')
    
#===========================================================================

class CallbackObserverThread(Thread):
    """

    The CallbackObserverThread checks continuosly if for an registered callback-function a result arrived.
    If the result arrived the specific callback-function is being executed by the ExecuteCallbackThread.

    :param parent: see ``parent``

    *Class-variables of CallbackObserverThread:*

    ``parent : qam.qam_proxy.QAMProxy``
        the QAMProxy is necessary to reach the methods of ``qam.qam_proxy.ConsumerThread``
    ``callback_uid_dict : dictionary``
        Dictionary which monitors the callbacks, that are not executed yet.
          Structure of the callback_uid_dict:
            - "id": string (id in the result_list)
            - "state": integer
    ``callback_dickt_lock : threading.Lock``
        A lock for locking the critical sections.
    ``kill : bool``
        The kill signal tells the CallbackObserverThread to stop calling callback-methods.
    """

    def __init__(self, parent):
        Thread.__init__(self)
        self.callback_uid_dict = {}
        self.callback_dict_lock = thread.allocate_lock()
        self.kill = False
        self.parent = parent
    
    def get_callback_item(self, uid):
        """
        This function returns an item from the callback_uid_dict, identified by the given uid.

        :param uid: uid of the desired item
        :type uid: string
        :rtype: dictionary, {"id": string, "state": integer}

        It is a critical section so it is necessary to lock this section.
        """
        
        self.callback_dict_lock.acquire()
        if uid in self.callback_uid_dict:
            item = self.callback_uid_dict.get(uid)
            cpy_item = copy.deepcopy(item)
            #logger.debug('copy' + repr(item))
        else:
            #logger.debug('copy none')
            cpy_item = None
        self.callback_dict_lock.release()
        return cpy_item

    def change_callback_item_state(self, uid, state):
        """
        This method changes the state of a specific callback-item.
        Possible values for the state are:
          - 0 = waiting for processing
          - 1 = processing
          - 2 = finished

        :param uid: uid of the desired item
        :param state: state to be set
        :type uid: string
        :type state: integer

        It is a critical section so it is necessary to lock this section.
        """
        self.callback_dict_lock.acquire()
        item = self.callback_uid_dict[uid]
        item['state'] = state
        self.callback_dict_lock.release()

    def remove_callback_item(self, uid):
        """
        This method removes an item from the callback_uid_dict. This is the case, when a callback is already executed.

        :param uid: uid of the desired item
        :type uid: string

        It is a critical section so it is necessary to lock this section.
        """
        self.callback_dict_lock.acquire()
        del self.callback_uid_dict[uid]
        self.callback_dict_lock.release()

    def __generate_uid(self):
        """
        A new unique uid for callback-registration is generated.

        :rtype: string which contains the generated uid
        """
        while True:
            logger.debug('Search for uid')
            uid = str(uuid.uuid4())
            if uid not in self.callback_uid_dict: break
        return uid

    def init_waiting_callback_item(self, id, timeout):
        """
        This method initializes a new callback-item with an unique uid. The given id is being stored and the state is set to *WAITING*.
        The new item is stored in the callback_uid_dict.

        :param id: id of the item in the result_list
        :type id: integer
        """
        uid = self.__generate_uid()
        self.callback_uid_dict[uid] = {'id':id,
            'state':0,
            'timeout':timeout,
            'start_time': time.time()}
        logger.debug('init uid done')
        return uid

    def check_timeout(self, uid, callback_info):
        """
        This method checks if a timeout has occoured and calls the error method
        with a QAMTimeoutException

        :param uid: uid of the callback info in callback_uid_dict
        :type uid: integer
        :param callback_info: the corresponding info from the callback_uid_dict
        :type cakkback_info: dict
        """
        #check timeout
        id = callback_info['id']
        curr_time = time.time()
        
        if callback_info['timeout'] == None: return False

        if curr_time - callback_info['start_time'] > callback_info['timeout']:
            self.change_callback_item_state(uid, 1)
            result_item = self.parent.consumer_thread.get_result_item(id)
            exception_method = result_item['exception_method']
            self.parent.consumer_thread.free_result_item(id)
            if exception_method == None:
                logger.error('Remote Exception not cought due to exception_method = None')
                self.remove_callback_item(uid)
            else:
                #logger.debug('Start Timeout exception, List: %s' % repr(self.callback_uid_dict))
                exception = QAMTimeoutException('Timeout for callback method occoured.')
                exec_timeout_thread = ExecuteCallbackThread(self.parent,
                                                            exception_method,
                                                            exception,
                                                            uid)
                exec_timeout_thread.start()
                
            return True
        else:
            return False

    def exit(self):
        """
        The exit method terminates the CallbackObseverThread.
        """
        self.kill = True
        self.join()

    def run(self):
        """
        The run method checks for every registered callback, if the result has already arrived. If the result has arrived:
          - in case of success the registered callback-function is being called
          - in case of an error:

            - if an error-function is registered this function is being called with the exception as parameter
            - if no error-function is registered a log-message is written into logfile

        For the execution of the callback-function a new ExecuteCallbackThread is being started. This thread finally executes the method.
        """
        while self.kill == False:
            #logger.debug("In Loop")
            for uid, val in self.callback_uid_dict.items():
                if val['state'] != 0: continue
                id = val['id']

                if self.check_timeout(uid, val): continue

                # check if result is already here
                if self.parent.consumer_thread.is_result_received(id):
                    self.change_callback_item_state(uid, 1)
                    result_item = self.parent.consumer_thread.get_result_item(id)
                    result = result_item['result_message']
                    callback_method = result_item['callback_method']
                    exception_method = result_item['exception_method']
                    self.parent.consumer_thread.free_result_item(id)

                    # check if exception_method is defined
                    if result['exception'] == True:
                        logger.debug('Callback Observer: Exception happened')
                        if exception_method == None:
                            logger.error('Remote Exception not cought due to exception_method = None')
                            self.remove_callback_item(uid)
                        else:
                            # check if it is an internal QAM Exception
                            if result['internal_exception'] > 0:
                                exception = QAMMethodNotFoundException(result['result'])
                                exec_error_thread = ExecuteCallbackThread(self.parent,
                                                                          exception_method,
                                                                          exception,
                                                                          uid)
                                exec_error_thread.start()
                            # else it is a user defined exception
                            else:
                                logger.debug("CallbackObserver: user defined exception: %s " % repr(result['result']))
                                exec_error_thread = ExecuteCallbackThread(self.parent,
                                                                          exception_method,
                                                                          result['result'],
                                                                          uid)
                                exec_error_thread.start()
                    # everything is ok no exception happened
                    else:
                        logger.debug("Callback SUCCESS %s" % repr(result['result']))
                        exec_succes_thread = ExecuteCallbackThread(self.parent,
                                                                   callback_method,
                                                                   result['result'],
                                                                   uid)
                        exec_succes_thread.start()
            
            time.sleep(0.1)

#===========================================================================

class ExecuteCallbackThread(Thread):
    """
    The ExecuteCallbackThread executes a registered callback-function with the results received from the QAMServer as parameter.

    :param parent: see ``parent``
    :param method: see ``method``
    :param params: see ``params``
    :param uid: see ``uid``

    *Class-variables of ExecuteCallbackThread:*

    ``parent : qam.qam_proxy.QAMProxy``
        the QAMProxy is necessary to reach the methods of ``qam.qam_proxy.CallbackObserverThread``:
    ``method : function``
        The method that should be called by the ExecuteCallbackThread.
    ``params : string``
        result received from QAMServer.
    ``uid : string``
        The uid which identifies the actual callback.
    """

    def __init__ (self, parent, method, params, uid):
        Thread.__init__(self)
        self.method = method
        self.params = params
        self.uid = uid
        self.parent = parent
   
    def run(self):
        """
        The run method executes the given callback-function.
        """
       
        self.method(self.params)
        self.parent.callback_observer_thread.remove_callback_item(self.uid)

class QAMException(Exception):
    """
    Internal QAMServer Exception.
    """
    pass

class QAMMethodNotFoundException(QAMException):
    """
    Internal QAMServer Exception, which is generated if the method called by the QAMProxy doesn't exist on the QAMServer.
    """
    pass

class QAMTimeoutException(QAMException):
    """
    Internal QAMServer Exception, which is generated if the method called by the QAMProxy produces a timeout.
    """
