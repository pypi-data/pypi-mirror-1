import time
from threading import Thread
from qam.qam_server import QAMServer
from custom_exception import CustomException
import os
import sys

sys.path.insert(0, os.pardir+'/src')
sys.path.append(os.getcwd())


class QAMTestServer(Thread):
  def __init__ (self, server_id, serializer='pickle'):
    Thread.__init__(self)
     # Create server
    print "before create"
    self.server = QAMServer(hostname="localhost",
                       port=5672,
                       username='guest',
                       password='guest',
                       vhost='/',
                       server_id=server_id,
                       serializer=serializer)
    print "after create"

  def close(self):
    self.server.close()

  def run(self):

   
                       


    # Register a function under a different name
    def adder_function(x, y):
      #print 'I am the adder func'
      return x + y

    def hello(str):
      #time.sleep(3)
      return 'Hello ' + str

    def excp_method(arg, arg2):
      raise Exception(arg, arg2)

    def object_method(arg):
      return arg

    def callback_test_method(str):
      #time.sleep(1)
      return 'Callback test result: ' + str

    def callback_exception(msg):
      raise Exception(msg)

    def looong_lasting_method():
      time.sleep(2)
      return

    def complex_type_method(testcomplex):
        return testcomplex.var

    def complex_method_exception(exception):
        return exception[0]

    def complex_method_custom_exception():
        raise CustomException

    def delayed_exception_method():
        time.sleep(2)
        raise CustomException
    
    self.server.register_function(hello, 'hello')
    self.server.register_function(adder_function, 'add')
    self.server.register_function(excp_method)
    self.server.register_function(object_method)
    self.server.register_function(callback_test_method)
    self.server.register_function(callback_exception)
    self.server.register_function(looong_lasting_method)
    self.server.register_function(complex_type_method)
    self.server.register_function(complex_method_exception)
    self.server.register_function(complex_method_custom_exception)
    self.server.register_function(delayed_exception_method)

    testclass = TestClass()
    self.server.register_class(testclass,'testclass')

    # Run the server's main loop
    self.server.serve()

class TestClass():
  def __init__(self):
    pass

  def test_method(self,a,b):
    return a+b
