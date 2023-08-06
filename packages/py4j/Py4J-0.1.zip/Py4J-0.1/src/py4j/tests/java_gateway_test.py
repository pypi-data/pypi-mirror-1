'''
Created on Dec 10, 2009

@author: barthelemy
'''
from IN import AF_INET, SOCK_STREAM
from multiprocessing.process import Process
from py4j.java_gateway import JavaGateway, Py4JError
from socket import socket
import subprocess
import time
import unittest

SERVER_PORT = 25333
TEST_PORT = 25332

def start_echo_server():
    subprocess.call(["java","-cp", "../../../../py4j/bin/","py4j.EchoServer"])
    
    
def start_echo_server_process():
    # XXX DO NOT FORGET TO KILL THE PROCESS IF THE TEST DOES NOT SUCCEED
    p = Process(target=start_echo_server)
    p.start()
    return p

def get_test_socket():
    testSocket = socket(AF_INET, SOCK_STREAM)
    testSocket.connect(('localhost', TEST_PORT))
    return testSocket

class TestCommChannel(object):
    """Communication Channel that does nothing. Useful for testing."""
    
    def __init__(self, return_message='yro0'):
        self.return_message = return_message
        pass
    
    def start(self):
        pass
    
    def stop(self):
        pass
    
    def send_command(self, command):
        self.last_message = command
        return self.return_message

class ProtocolTest(unittest.TestCase):
    def testProtocolSend(self):
        testChannel = TestCommChannel()
        gateway = JavaGateway(testChannel, True)
        e = gateway.getExample()
        self.assertEqual('c\ng\ngetExample\ne\n',testChannel.last_message)
        e.method1(1,True,'Hello\nWorld',e,None,1.5)
        self.assertEqual('c\no0\nmethod1\ni1\nbTrue\nsHello\\nWorld\nro0\nn\nd1.5\ne\n',testChannel.last_message)
    
    def testProtocolReceive(self):
        p = start_echo_server_process()
        time.sleep(1)
        try:
            testSocket = get_test_socket()
            testSocket.sendall('yro0\n'.encode('utf-8'))
            testSocket.sendall('ysHello World\n'.encode('utf-8'))
            testSocket.sendall('yi123\n'.encode('utf-8'))
            testSocket.sendall('yd1.25\n'.encode('utf-8'))
            testSocket.sendall('yn\n'.encode('utf-8'))
            testSocket.sendall('ybTrue\n'.encode('utf-8'))
            testSocket.close()
            time.sleep(1)
            
            gateway = JavaGateway()
            ex = gateway.getNewExample()
            self.assertEqual('Hello World',ex.method3(1, True))
            self.assertEqual(123,ex.method3())
            self.assertAlmostEqual(1.25,ex.method3())
            self.assertTrue(ex.method2() == None)
            self.assertTrue(ex.method4())
            gateway.comm_channel.stop()
            
        except Exception as e:
            print('Error has occurred', e)
        p.join()

class IntegrationTest(unittest.TestCase):

    def setUp(self):
        self.p = start_echo_server_process()
        # This is to ensure that the server is started before connecting to it!
        time.sleep(1)

    def tearDown(self):
        self.p.join()

    def testIntegration(self):
        try:
            testSocket = get_test_socket()
            testSocket.sendall('yro0\n'.encode('utf-8'))
            testSocket.sendall('ysHello World\n'.encode('utf-8'))
            testSocket.close()
        
            gateway = JavaGateway()
            ex = gateway.getNewExample()
            response = ex.method3(1, True)
            print(response)
            self.assertEqual('Hello World',response)
            gateway.comm_channel.stop()
        except Exception as e:
            print('Error has occurred', e)
            
    def testException(self):
        try:
            testSocket = get_test_socket()
            testSocket.sendall('yro0\n'.encode('utf-8'))
            testSocket.sendall('x\n')
            testSocket.close()
            
            gateway = JavaGateway()
            ex = gateway.getNewExample()
                
            try:
                ex.method3(1, True)
                self.fail('Should have failed!')
            except Py4JError:
                self.assertTrue(True)
            
            gateway.comm_channel.stop()
            
        except Exception as e:
            print('Error has occurred', e)   
    
    


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testGateway']
#    logger = logging.getLogger("py4j")
#    logger.setLevel(logging.DEBUG)
#    logger.addHandler(logging.StreamHandler())
    unittest.main()
