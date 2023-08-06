# To change this template, choose Tools | Templates
# and open the template in the editor.

import logging
import logging.handlers
import os
import sys
from threading import Thread
import time
import unittest


sys.path.insert(0, os.pardir + '/src')
sys.path.append(os.getcwd())


from qam.qam_proxy import   QAMProxy, \
                            QAMMethodNotFoundException, \
                            QAMException, \
                            QAMTimeoutException
from qamtestserver import QAMTestServer

from custom_exception import CustomException

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


class ComplexTest:
    def __init__(self):
        self.var = 'hallo'


class  QamTestCase(unittest.TestCase):

 

    def setUp(self):
        print "Init Testing..."
        self.amqp_hostname = "localhost"
        self.amqp_port = 5672
        self.amqp_user = 'guest'
        self.amqp_pwd = 'guest'
        self.amqp_vhost = '/'

        self.server = QAMTestServer(server_id='testqamserver',serializer='json')
        self.server.setDaemon(True)
        self.server.start()

        self.server_pickle = QAMTestServer(server_id='testqamserverpickle')
        self.server_pickle.setDaemon(True)
        self.server_pickle.start()
    

    def tearDown(self):
        self.server.close()
        self.server_pickle.close()
        
    #    self.foo.dispose()
    #    self.foo = None


#    def test_long_non_load_test(self):
#        print 'long_non_load_test'
#        proxy = QAMProxy(hostname=self.amqp_hostname,
#                         port=self.amqp_port,
#                         username=self.amqp_user,
#                         password=self.amqp_pwd,
#                         vhost=self.amqp_vhost,
#                         server_id='testqamserver',
#                         client_id='testqamclient1',
#                         serializer='json'
#                         )
#
#        for i in range(3):
#            time.sleep(5)
#            a = i
#            b = 1
#            golden_device = a + b
#            result = proxy.add(a, b)
#            self.assertEqual(golden_device, result, "%d + %d must equal %d" % (a, b, golden_device))
#
#        proxy.close()

    def test_connect_no_server(self):
        print 'test_connect_no_server'
        try:
            proxy = QAMProxy(hostname=self.amqp_hostname+"_",
                         port=self.amqp_port,
                         username=self.amqp_user,
                         password=self.amqp_pwd,
                         vhost=self.amqp_vhost,
                         server_id='testqamserver',
                         client_id='testqamclient1',
                         serializer='json'
                         )
            proxy.close()
            
        except Exception:
            print 'Successfully catched ConnectionErrorException'
            
        

    def test_basic_method_call(self):
        print 'test_basic_method_call'
        proxy = QAMProxy(hostname=self.amqp_hostname,
                         port=self.amqp_port,
                         username=self.amqp_user,
                         password=self.amqp_pwd,
                         vhost=self.amqp_vhost,
                         server_id='testqamserver',
                         client_id='testqamclient1',
                         serializer='json',
                         ssl=False
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
                         client_id='testqamclient2',
                         serializer='json'

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
                                 client_id=self.client_id,
                                 serializer='json'
                                 )

                for i in range(10):

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
                         client_id='testthreadedclient',
                         serializer='json'
                         )

        class TestClientThread(Thread):
            def __init__(self, client_id, proxy):
                Thread.__init__(self)
                self.proxy = proxy
                self.failed = False
                self.client_id = client_id
      
            def run(self):
                for i in range(10):

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
                         client_id='testexception ',
                         serializer='json'
                         )

        golden_device = 'Help'
        gd2 = 24
        try:
            proxy.excp_method(golden_device, gd2)
        except Exception as e:
            arg = e.args[0]
            print repr(e)
            self.assertEqual(arg, golden_device, 'Exception Argument1 is not equal')
            arg = e.args[1]
            self.assertEqual(arg, gd2, 'Exception Argument2 is not equal')

        else:
            self.fail('Exception need to be raised to pass the test')
        proxy.close()

    def test_callback_method_call(self):
        print 'test_callback_method_call'
        proxy = QAMProxy(hostname=self.amqp_hostname,
                         port=self.amqp_port,
                         username=self.amqp_user,
                         password=self.amqp_pwd,
                         vhost=self.amqp_vhost,
                         server_id='testqamserver',
                         client_id='testexception',
                         serializer='json'
                         )

        class CallbackTest():
            (STATE_UNKNOWN, STATE_SUCCESS, STATE_ERROR) = range(3)
            def __init__(self):
                self.state = CallbackTest.STATE_UNKNOWN

            def success(self, arg):
                #time.sleep(1)
                self.state = CallbackTest.STATE_SUCCESS
                print arg
            def error(self, arg):
                self.state = CallbackTest.STATE_ERROR
                print 'error:' + repr(arg)


        callback_test = CallbackTest()
        uid = proxy.callback(callback_test.success, callback_test.error).callback_test_method("test")
        print 'UID: ' + uid

        old_state = -1
        while True:
            state  = proxy.get_callback_state(uid)
            if state == 0 and old_state != 0: print "state: Waiting"
            if state == 1 and old_state != 1: print "state: Processing"
            if state == 2:
                print "state: Finished"
                break
            old_state = state

        self.assertEqual(CallbackTest.STATE_SUCCESS, callback_test.state, "Callback must be successfull, but it isn't")
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
                         client_id='testexception ',
                         serializer='json'
                         )
        a = 1
        b = 2
        gd = a + b
        result = proxy.testclass.test_method(a, b)
        self.assertEqual(result, gd, 'sums must be the same')
        proxy.close()

    def test_method_not_found(self):
        print 'test_method_not_found'
        proxy = QAMProxy(hostname=self.amqp_hostname,
                         port=self.amqp_port,
                         username=self.amqp_user,
                         password=self.amqp_pwd,
                         vhost=self.amqp_vhost,
                         server_id='testqamserver',
                         client_id='testexception ',
                         serializer='json'
                         )
        a = 1
        b = 2
        gd = a + b
        try:
            result = proxy.testclass.asdf(a, b)
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
                         client_id='testexception',
                         serializer='json'
                         )



        class CallbackTest():
            (STATE_UNKNOWN, STATE_SUCCESS, STATE_ERROR) = range(3)
            def __init__(self):
                self.state = CallbackTest.STATE_UNKNOWN

            def success(self, arg):
                print arg
                print "ERROR"

            def error(self, arg):
                if isinstance(arg, QAMException):
                    self.state = CallbackTest.STATE_SUCCESS
                    print 'QAMException:' + repr(arg)
                else:
                    self.state = CallbackTest.STATE_ERROR
                    print 'No QAMException: ' + repr(arg)
                

        callback_test = CallbackTest()
        uid = proxy.callback(callback_test.success, callback_test.error).asdf("test")

        old_state = -1
        while True:
            state  = proxy.get_callback_state(uid)
            if state == 0 and old_state != 0: print "state: Waiting"
            if state == 1 and old_state != 1: print "state: Processing"
            if state == 2:
                print "state: Finished"
                break
            old_state = state
        self.assertEqual(CallbackTest.STATE_SUCCESS, callback_test.state,
                         "Must return a QAM Exception because the method is not defined on the server")
        proxy.close()

    def test_callback_timedout(self):
        print 'test_callback_timedout'
        proxy = QAMProxy(hostname=self.amqp_hostname,
                         port=self.amqp_port,
                         username=self.amqp_user,
                         password=self.amqp_pwd,
                         vhost=self.amqp_vhost,
                         server_id='testqamserver',
                         client_id='testexception',
                         serializer='json'
                         )



        class CallbackTest():
            (STATE_UNKNOWN, STATE_SUCCESS, STATE_ERROR) = range(3)
            def __init__(self):
                self.state = CallbackTest.STATE_UNKNOWN

            def success(self, arg):
                print arg
                self.state = CallbackTest.STATE_ERROR
                print "ERROR"

            def error(self, arg):
                if isinstance(arg, QAMTimeoutException):
                    self.state = CallbackTest.STATE_SUCCESS
                    print 'QAMException:' + repr(arg)
                else:
                    self.state = CallbackTest.STATE_ERROR
                    print 'No QAMException: ' + repr(arg)


        callback_test = CallbackTest()
        uid = proxy.callback(callback_test.success, callback_test.error) \
                .set_timeout(1) \
                .looong_lasting_method()

        old_state = -1
        while True:
            state  = proxy.get_callback_state(uid)
            if state == 0 and old_state != 0: print "state: Waiting"
            if state == 1 and old_state != 1: print "state: Processing"
            if state == 2:
                print "state: Finished"
                break
            old_state = state
        self.assertEqual(CallbackTest.STATE_SUCCESS, callback_test.state,
                         "Must return a QAMTimeoutException because the \
                          method needs too much time to return result")
        proxy.close()

    def test_callback_exception_method_call(self):
        print 'test_callback_exception_method_call'
        proxy = QAMProxy(hostname=self.amqp_hostname,
                         port=self.amqp_port,
                         username=self.amqp_user,
                         password=self.amqp_pwd,
                         vhost=self.amqp_vhost,
                         server_id='testqamserver',
                         client_id='testexception',
                         serializer='json'
                         )

        class CallbackTest():
            (STATE_UNKNOWN, STATE_SUCCESS, STATE_ERROR) = range(3)
            def __init__(self):
                self.state = CallbackTest.STATE_UNKNOWN

            def success(self, arg):
                print arg
                print "ERROR"

            def error(self, arg):
                if isinstance(arg, QAMException):
                    self.state = CallbackTest.STATE_ERROR
                    print 'QAMException:' + repr(arg)
                else:
                    self.state = CallbackTest.STATE_SUCCESS
                    print 'No QAMException: ' + repr(arg)
                    

        callback_test = CallbackTest()
        uid = proxy.callback(callback_test.success, callback_test.error).callback_exception("test")

        old_state = -1
        while True:
            state  = proxy.get_callback_state(uid)
            if state == 0 and old_state != 0: print "state: Waiting"
            if state == 1 and old_state != 1: print "state: Processing"
            if state == 2:
                print "state: Finished"
                break
            old_state = state

        self.assertEqual(CallbackTest.STATE_SUCCESS, callback_test.state,
                 "Must return a User defined Exception to succeed.")
        proxy.close()
    
    def test_callback_instance_call(self):
        print 'test_callback_instance_call'
        proxy = QAMProxy(hostname=self.amqp_hostname,
                         port=self.amqp_port,
                         username=self.amqp_user,
                         password=self.amqp_pwd,
                         vhost=self.amqp_vhost,
                         server_id='testqamserver',
                         client_id='testexception',
                         serializer='json'
                         )

        class CallbackTest():
            (STATE_UNKNOWN, STATE_SUCCESS, STATE_ERROR) = range(3)
            def __init__(self):
                self.state = CallbackTest.STATE_UNKNOWN
                self.result = 0

            def success(self, arg):
                print arg
                self.result = arg
                self.state = CallbackTest.STATE_SUCCESS

            def error(self, arg):
                if isinstance(arg, QAMException):
                    self.state = CallbackTest.STATE_ERROR
                    print 'QAMException:' + repr(arg)
                else:
                    self.state = CallbackTest.STATE_ERROR
                    print 'No QAMException: ' + repr(arg)


        a = 1
        b = 2
        callback_test = CallbackTest()
        uid = proxy.callback(callback_test.success, callback_test.error) \
                .testclass.test_method(a, b)

        old_state = -1
        while True:
            state  = proxy.get_callback_state(uid)
            if state == 0 and old_state != 0: print "state: Waiting"
            if state == 1 and old_state != 1: print "state: Processing"
            if state == 2:
                print "state: Finished"
                break
            old_state = state

        self.assertEqual(CallbackTest.STATE_SUCCESS, callback_test.state,
                 "Must call the success method NOT the error method.")
        self.assertEqual(a+b, callback_test.result,
                 "Result does not match.")
        proxy.close()

    def test_callback_exception_method_not_found_in_instance(self):
        print 'test_callback_exception_method_not_found_in_instance'
        proxy = QAMProxy(hostname=self.amqp_hostname,
                         port=self.amqp_port,
                         username=self.amqp_user,
                         password=self.amqp_pwd,
                         vhost=self.amqp_vhost,
                         server_id='testqamserver',
                         client_id='testexception',
                         serializer='json'
                         )



        class CallbackTest():
            (STATE_UNKNOWN, STATE_SUCCESS, STATE_ERROR) = range(3)
            def __init__(self):
                self.state = CallbackTest.STATE_UNKNOWN

            def success(self, arg):
                print arg
                print "ERROR"

            def error(self, arg):
                if isinstance(arg, QAMException):
                    self.state = CallbackTest.STATE_SUCCESS
                    print 'QAMException:' + repr(arg)
                else:
                    self.state = CallbackTest.STATE_ERROR
                    print 'No QAMException: ' + repr(arg)


        callback_test = CallbackTest()
        uid = proxy.callback(callback_test.success, callback_test.error).testclass.asdf("test")

        old_state = -1
        while True:
            state  = proxy.get_callback_state(uid)
            if state == 0 and old_state != 0: print "state: Waiting"
            if state == 1 and old_state != 1: print "state: Processing"
            if state == 2:
                print "state: Finished"
                break
            old_state = state
        self.assertEqual(CallbackTest.STATE_SUCCESS, callback_test.state,
                         "Must return a QAM Exception because the method is not defined on the server")
        proxy.close()

    def test_synchronous_timedout_method_call(self):
        print 'test_synchronous_timedout_method_call'
        proxy = QAMProxy(hostname=self.amqp_hostname,
                         port=self.amqp_port,
                         username=self.amqp_user,
                         password=self.amqp_pwd,
                         vhost=self.amqp_vhost,
                         server_id='testqamserver',
                         client_id='testqamclient1',
                         serializer='json'
                         )

        success = False
        try:
            result = proxy.set_timeout(1).looong_lasting_method()
        except QAMTimeoutException:
            success = True


        self.assertTrue(success, "QAMTimoutException must be raised.")

        proxy.close()

    def test_serialize_pickle_class(self):
        print 'test_serialize_pickle'
        proxy = QAMProxy(hostname=self.amqp_hostname,
                         port=self.amqp_port,
                         username=self.amqp_user,
                         password=self.amqp_pwd,
                         vhost=self.amqp_vhost,
                         server_id='testqamserverpickle',
                         client_id='testqamclient1',
                         serializer='pickle'
                         )

        test_complex = ComplexTest()
        result = proxy.complex_type_method(test_complex)



        self.assertEqual(result, test_complex.var, "The result must be the same as TestComplex.var.")

        proxy.close()

    def test_serialize_pickle_exception(self):
        print 'test_serialize_pickle'
        proxy = QAMProxy(hostname=self.amqp_hostname,
                         port=self.amqp_port,
                         username=self.amqp_user,
                         password=self.amqp_pwd,
                         vhost=self.amqp_vhost,
                         server_id='testqamserverpickle',
                         client_id='testqamclient1',
                         serializer='pickle'
                         )

        exception = Exception("hallo")
        result = proxy.complex_method_exception(exception)



        self.assertEqual(result, exception[0], "The result must be the same as TestComplex.var.")

        proxy.close()

    def test_serialize_pickle_custom_exception(self):
        print 'test_serialize_pickle_custom_exception'
        proxy = QAMProxy(hostname=self.amqp_hostname,
                         port=self.amqp_port,
                         username=self.amqp_user,
                         password=self.amqp_pwd,
                         vhost=self.amqp_vhost,
                         server_id='testqamserverpickle',
                         client_id='testqamclient1',
                         serializer='pickle'
                         )

     
        success = False
        try:
            print "before call"
            result = proxy.complex_method_custom_exception()
        except Exception, e:
            if isinstance(e, CustomException):
                success = True



        self.assertTrue(success, "A CustomException must be thrown.")

        proxy.close()
        
    def test_callback_exception_method_call_pickle(self):
        print 'test_callback_exception_method_call_pickle'
        proxy = QAMProxy(hostname=self.amqp_hostname,
                         port=self.amqp_port,
                         username=self.amqp_user,
                         password=self.amqp_pwd,
                         vhost=self.amqp_vhost,
                         server_id='testqamserverpickle',
                         client_id='testexception',
                         serializer='pickle'
                         )

        class CallbackTest():
            (STATE_UNKNOWN, STATE_SUCCESS, STATE_ERROR) = range(3)
            def __init__(self):
                self.state = CallbackTest.STATE_UNKNOWN

            def success(self, arg):
                print arg
                print "ERROR"
                self.state = CallbackTest.STATE_ERROR

            def error(self, arg):
                if isinstance(arg, CustomException):
                    self.state = CallbackTest.STATE_SUCCESS
                    print 'CustomException:' + repr(arg)
                else:
                    self.state = CallbackTest.STATE_ERROR
                    print 'No CustomException: ' + repr(arg)


        callback_test = CallbackTest()
        uid = proxy.callback(callback_test.success, callback_test.error).complex_method_custom_exception()

        old_state = -1
        while True:
            state  = proxy.get_callback_state(uid)
            if state == 0 and old_state != 0: print "state: Waiting"
            if state == 1 and old_state != 1: print "state: Processing"
            if state == 2:
                print "state: Finished"
                break
            old_state = state

        self.assertEqual(CallbackTest.STATE_SUCCESS, callback_test.state,
                 "Must return a User defined Exception to succeed.")
        proxy.close()

    def test_asynchronous_timedout_method_call_pickle(self):
        print 'test_synchronous_timedout_method_call'
        proxy = QAMProxy(hostname=self.amqp_hostname,
                         port=self.amqp_port,
                         username=self.amqp_user,
                         password=self.amqp_pwd,
                         vhost=self.amqp_vhost,
                         server_id='testqamserverpickle',
                         client_id='testqamclient1',
                         serializer='pickle'
                         )

        class CallbackTest():
            (STATE_UNKNOWN, STATE_SUCCESS, STATE_ERROR) = range(3)
            def __init__(self):
                self.state = CallbackTest.STATE_UNKNOWN

            def success(self, arg):
                print arg
                print "ERROR"
                self.state = CallbackTest.STATE_ERROR

            def error(self, arg):
                if isinstance(arg, QAMTimeoutException):
                    self.state = CallbackTest.STATE_SUCCESS
                    print 'CustomException:' + repr(arg)
                else:
                    self.state = CallbackTest.STATE_ERROR
                    print 'No CustomException: ' + repr(arg)


        callback_test = CallbackTest()
        uid = proxy.callback(callback_test.success, callback_test.error).set_timeout(1).delayed_exception_method()

        old_state = -1
        while True:
            state  = proxy.get_callback_state(uid)
            if state == 0 and old_state != 0: print "state: Waiting"
            if state == 1 and old_state != 1: print "state: Processing"
            if state == 2:
                print "state: Finished"
                break
            old_state = state

        self.assertEqual(CallbackTest.STATE_SUCCESS, callback_test.state,
                 "Must return a User defined Exception to succeed.")
        proxy.close()


if __name__ == '__main__':
    unittest.main()
#    result = unittest.TestResult()
#    test = QamTestCase('test_basic_method_call')
#    test.run(result)
#    if len(result.failures) != 0: print "=============== Failures ==========================="
#    print "".join("%s = %s" % (a, b) for a, b in result.failures)
#    if len(result.errors) != 0: print "=============== Errors ============================="
#    print "".join("%s = %s" % (a, b) for a, b in result.errors)
#    print "===================================================="
#    if result.wasSuccessful(): print 'Successfully passed all Tests'
#    else: print "Failed - Details see above."
