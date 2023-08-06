# To change this template, choose Tools | Templates
# and open the template in the editor.

from threading import Thread
import unittest
import time
import os
import sys
import logging
import logging.handlers


sys.path.insert(0, os.pardir+'/src')
sys.path.append(os.getcwd())


from qam.qam_proxy import QAMProxy, QAMMethodNotFoundException, QAMException
from qamtestserver import QAMTestServer

# setup logging
formatter = logging.Formatter("%(asctime)s|%(name)s|%(levelname)s|%(filename)s|%(funcName)s| #%(lineno)d: %(message)s")

logger_proxy = logging.getLogger('qam.qam_proxy')
handler = logging.handlers.RotatingFileHandler('log/qamproxy.log', maxBytes=200000, backupCount=5)
handler.setFormatter(formatter)
logger_proxy.addHandler(handler)
logger_proxy.setLevel(logging.DEBUG)

logger_server = logging.getLogger('qam.qam_server')
handler = logging.handlers.RotatingFileHandler('log/qamserver.log', maxBytes=200000, backupCount=5)
handler.setFormatter(formatter)
logger_server.addHandler(handler)
logger_server.setLevel(logging.DEBUG)

logger = logging.getLogger('qam.qam_test')
handler = logging.handlers.RotatingFileHandler('log/qamtest.log', maxBytes=200000, backupCount=5)
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)
# end setup logging

class  QamTestCase(unittest.TestCase):

 

  def setUp(self):
    print "Init Testing..."
    self.amqp_hostname = "localhost"
    self.amqp_port = 5672
    self.amqp_user = 'guest'
    self.amqp_pwd = 'guest'
    self.amqp_vhost = '/'

    self.server = QAMTestServer()
    self.server.setDaemon(True)
    self.server.start()
    

  def tearDown(self):
    self.server.close()
  #    self.foo.dispose()
  #    self.foo = None

  def test_basic_method_call(self):
    print 'test_basic_method_call'
    proxy = QAMProxy(hostname=self.amqp_hostname,
                     port=self.amqp_port,
                     username=self.amqp_user,
                     password=self.amqp_pwd,
                     vhost=self.amqp_vhost,
                     server_id='testqamserver',
                     client_id='testqamclient1'
                     )

    for i in range(10):
      a = i
      b = 1
      golden_device = a + b
      result = proxy.add(a, b)
      self.assertEqual(golden_device, result, "%d + %d must equal %d" % (a, b, golden_device))

    proxy.close()

  def test_string_method_call(self):
    print 'test_string_method_call'
    proxy = QAMProxy(hostname=self.amqp_hostname,
                     port=self.amqp_port,
                     username=self.amqp_user,
                     password=self.amqp_pwd,
                     vhost=self.amqp_vhost,
                     server_id='testqamserver',
                     client_id='testqamclient2'
                     )

    str = 'Teststring'
    golden_device = 'Hello Teststring'
    result = proxy.hello(str)
    self.assertEqual(golden_device, result, "Golden Device %s must equal result %s" % (golden_device, result))
    proxy.close()



  def test_multiple_clients(self):
    print 'test_multiple_clients'
    class TestClientThread(Thread):
      def __init__(self, client_id, test):
        Thread.__init__(self)
        self.client_id = client_id
        self.failed = False
        self.test = test
      def run(self):
        proxy = QAMProxy(hostname=self.test.amqp_hostname,
                         port=self.test.amqp_port,
                         username=self.test.amqp_user,
                         password=self.test.amqp_pwd,
                         vhost=self.test.amqp_vhost,
                         server_id='testqamserver',
                         client_id=self.client_id
                         )

        for i in range(50):

          str = self.client_id + '_%d' % i
          golden_device = 'Hello ' + str
          result = proxy.hello(str)
          #logger.debug('GD: ' + golden_device + ';  Result: ' + result)
          if result != golden_device:
            #logger.debug(golden_device + ' !=  ' + result)
            self.failed = True
        proxy.close()

    thread1 = TestClientThread('thread1', self)
    thread2 = TestClientThread('thread2', self)
    thread3 = TestClientThread('thread3', self)

    thread1.start()
    thread2.start()
    thread3.start()

    thread1.join()
    thread2.join()
    thread3.join()

    self.assertFalse(thread1.failed, "Thread1 failed")
    self.assertFalse(thread2.failed, "Thread1 failed")
    




  def test_multiple_method_threads(self):
    print 'test_multiple_method_threads'
    proxy = QAMProxy(hostname=self.amqp_hostname,
                     port=self.amqp_port,
                     username=self.amqp_user,
                     password=self.amqp_pwd,
                     vhost=self.amqp_vhost,
                     server_id='testqamserver',
                     client_id='testthreadedclient'
                     )

    class TestClientThread(Thread):
      def __init__(self, client_id, proxy):
        Thread.__init__(self)
        self.proxy = proxy
        self.failed = False
        self.client_id = client_id
      
      def run(self):
        for i in range(50):

          str = self.client_id + '_%d' % i
          golden_device = 'Hello ' + str
          result = self.proxy.hello(str)
          #logger.debug('GD: ' + golden_device + ';  Result: ' + result)
          if result != golden_device:
            logger.debug(golden_device + ' !=  ' + result)
            self.failed = True

    thread1 = TestClientThread('thread1', proxy)
    thread2 = TestClientThread('thread2', proxy)
    thread3 = TestClientThread('thread3', proxy)

    thread1.start()
    thread2.start()
    thread3.start()

    thread1.join()
    thread2.join()
    thread3.join()

    self.assertFalse(thread1.failed, "Thread1 failed")
    self.assertFalse(thread2.failed, "Thread2 failed")
    self.assertFalse(thread3.failed, "Thread3 failed")
    proxy.close()


  

  def test_exception_method_call(self):
    print 'test_exception_method_call'
    proxy = QAMProxy(hostname=self.amqp_hostname,
                     port=self.amqp_port,
                     username=self.amqp_user,
                     password=self.amqp_pwd,
                     vhost=self.amqp_vhost,
                     server_id='testqamserver',
                     client_id='testexception '
                     )

    golden_device = 'Help'
    gd2 =24
    try:
      proxy.excp_method(golden_device,gd2)
    except Exception as e:
      arg = e.args[0]
      self.assertEqual(arg, golden_device, 'Exception Argument1 is not equal')
      arg = e.args[1]
      self.assertEqual(arg, gd2, 'Exception Argument2 is not equal')

    else:
      self.fail('Exception need to be raised to pass the test')
    proxy.close()

  def test_zzcallback_method_call(self):
    print 'test_callback_method_call'
    proxy = QAMProxy(hostname=self.amqp_hostname,
                     port=self.amqp_port,
                     username=self.amqp_user,
                     password=self.amqp_pwd,
                     vhost=self.amqp_vhost,
                     server_id='testqamserver',
                     client_id='testexception'
                     )


    def success(arg):
      #time.sleep(1)
      print arg
    def error(arg):
      print 'error:'+arg
    uid = proxy.callback(success, error).callback_test_method("test")
    print 'UID: ' + uid

    old_state = -1
    while True:
      state  = proxy.get_callback_state(uid)
      if state == 0 and old_state != 0: print "state: Waiting"
      if state == 1 and old_state != 1: print "state: Processing"
      if state == 2 :
        print "state: Finished"
        break
      old_state = state

      #time.sleep(0.1)
    proxy.close()

  def test_register_class_method_call(self):
    print 'test_register_class_method_call'
    proxy = QAMProxy(hostname=self.amqp_hostname,
                     port=self.amqp_port,
                     username=self.amqp_user,
                     password=self.amqp_pwd,
                     vhost=self.amqp_vhost,
                     server_id='testqamserver',
                     client_id='testexception '
                     )
    a = 1
    b = 2
    gd = a + b
    result = proxy.testclass.test_method(a,b)
    self.assertEqual(result,gd,'sums must be the same')
    proxy.close()

  def test_method_not_found(self):
    print 'test_method_not_found'
    proxy = QAMProxy(hostname=self.amqp_hostname,
                     port=self.amqp_port,
                     username=self.amqp_user,
                     password=self.amqp_pwd,
                     vhost=self.amqp_vhost,
                     server_id='testqamserver',
                     client_id='testexception '
                     )
    a = 1
    b = 2
    gd = a + b
    try:
      result = proxy.testclass.asdf(a,b)
      #self.assertEqual(result,gd,'sums must be the same')

    except QAMMethodNotFoundException, e:
      print e
      pass
    else:
      self.fail("method should not be found")

    finally:
      proxy.close()

  def test_callback_exception_method_not_found(self):
    print 'test_callback_exception_method_not_found'
    proxy = QAMProxy(hostname=self.amqp_hostname,
                     port=self.amqp_port,
                     username=self.amqp_user,
                     password=self.amqp_pwd,
                     vhost=self.amqp_vhost,
                     server_id='testqamserver',
                     client_id='testexception'
                     )

    def success(arg):
      print arg
      print "ERROR"

    def error(arg):
      if isinstance(arg[0],QAMException):
        print 'QAMException:'+ repr(arg)
      else:
        print 'No QAMException: '+repr(arg)
      print "SUCCESSFUL"
      
    uid = proxy.callback(success, error).asdf("test")

    old_state = -1
    while True:
      state  = proxy.get_callback_state(uid)
      if state == 0 and old_state != 0: print "state: Waiting"
      if state == 1 and old_state != 1: print "state: Processing"
      if state == 2 :
        print "state: Finished"
        break
      old_state = state

      #time.sleep(0.1)
    proxy.close()

  def test_callback_exception_method_call(self):
    print 'test_callback_exception_method_call'
    proxy = QAMProxy(hostname=self.amqp_hostname,
                     port=self.amqp_port,
                     username=self.amqp_user,
                     password=self.amqp_pwd,
                     vhost=self.amqp_vhost,
                     server_id='testqamserver',
                     client_id='testexception'
                     )

    def success(arg):
      print arg
      print "ERROR"

    def error(arg):
      if isinstance(arg[0],QAMException):
        print 'QAMException:'+ repr(arg)
      else:
        print 'No QAMException '+repr(arg)
        
      print "SUCCESSFUL"

    uid = proxy.callback(success, error).callback_exception("test")

    old_state = -1
    while True:
      state  = proxy.get_callback_state(uid)
      if state == 0 and old_state != 0: print "state: Waiting"
      if state == 1 and old_state != 1: print "state: Processing"
      if state == 2 :
        print "state: Finished"
        break
      old_state = state

      #time.sleep(0.1)
    proxy.close()
    
  def test_callback_exception_instance_call(self):
    print 'test_callback_exception_instance_call'
    proxy = QAMProxy(hostname=self.amqp_hostname,
                     port=self.amqp_port,
                     username=self.amqp_user,
                     password=self.amqp_pwd,
                     vhost=self.amqp_vhost,
                     server_id='testqamserver',
                     client_id='testexception'
                     )

    def success(arg):
      print arg
      print "SUCCESSFUL"

    def error(arg):
      if isinstance(arg[0],QAMException):
        print 'QAMException:'+ repr(arg)
      else:
        print 'No QAMException '+repr(arg)
        
      print "ERROR"
    a = 1
    b = 2
    uid = proxy.callback(success, error).testclass.test_method(a,b)

    old_state = -1
    while True:
      state  = proxy.get_callback_state(uid)
      if state == 0 and old_state != 0: print "state: Waiting"
      if state == 1 and old_state != 1: print "state: Processing"
      if state == 2 :
        print "state: Finished"
        break
      old_state = state

      #time.sleep(0.1)
    proxy.close()

if __name__ == '__main__':
  unittest.main()
#  result = unittest.TestResult()
#  test = QamTestCase('test_callback_exception_method_call')
#  test.run(result)
#  if len(result.failures) != 0: print "=============== Failures ==========================="
#  print "".join("%s = %s" % (a, b) for a, b in result.failures)
#  if len(result.errors) != 0: print "=============== Errors ============================="
#  print "".join("%s = %s" % (a, b) for a, b in result.errors)
#  print "===================================================="
#  if result.wasSuccessful(): print 'Successfully passed all Tests'
#  else: print "Failed - Details see above."
