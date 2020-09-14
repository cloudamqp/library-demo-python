"""
Test a blocking connection to RabbitMQ from Python

Usage:
    test_blocking_connection <host> <port> <vhost> <user> <password>

Options:
    -h --help     Show this screen.
    --version     Show the version
"""

import sys

import pika
import unittest

from docopt import docopt

RECEIVED_HELLO = False


def consumer_callback(ch, method, properties, body):
    """
    Callback used when the consumer is created

    :param method:  AMQP method
    :param properties: AMQP message properties
    :param body: message body
    """
    msg = body.decode('utf-8')
    print(msg)
    if msg in "Hello CloudAMQP!":
        global RECEIVED_HELLO
        RECEIVED_HELLO = True
    else:
        print("RECEIVED UNEXPECTED MESSAGE")
    ch.close()

class BlockingConnectionTests(unittest.TestCase):
    """
    Tests using blocking connection in RabbitMQ
    """

    def get_args(self):
        """
        Gets the hostname, port, vhost, username, and password for our connection

        :return: A tuple containing the parameters
        """
        host = sys.argv[0]
        port = sys.argv[1]
        vhost = sys.argv[2]
        user = sys.argv[3]
        pwd = sys.argv[4]
        return (host, port, vhost, user, pwd)

    def test_1_should_connect(self):
        """
        Test connecting to the broker
        """
        (host, port, vhost, user, pwd) = self.get_args()
        conn_str = "amqp://{}:{}@{}:{}/{}".format(user, pwd, host, port, vhost)
        params = pika.URLParameters(conn_str)
        connection = pika.BlockingConnection(params)
        channel = connection.channel()
        channel.close()
        connection.close()

    def test_2_should_send_message(self):
        """
        Test send a message
        """
        (host, port, vhost, user, pwd) = self.get_args()
        conn_str = "amqp://{}:{}@{}:{}/{}".format(user, pwd, host, port, vhost)
        params = pika.URLParameters(conn_str)
        connection = pika.BlockingConnection(params)
        channel = connection.channel()
        channel.queue_declare(queue='test_queue')
        channel.queue_bind("test_queue", "test_exchange", "tests")
        channel.basic_publish(exchange='test_exchange',
                              routing_key='tests',
                              body="Hello CloudAMQP!")
        channel.close()
        connection.close()
    def test_3_should_create_consumer(self):
            """
            Test creating a consumer
            """
            (host, port, vhost, user, pwd) = self.get_args()
            conn_str = "amqp://{}:{}@{}:{}/{}".format(user, pwd, host, port, vhost)
            params = pika.URLParameters(conn_str)
            connection = pika.BlockingConnection(params)
            channel = connection.channel()
            # send a message
            channel.queue_declare(queue='test_queue')
            channel.basic_publish(exchange='',
                                  routing_key='test_queue',
                                  body="Hello CloudAMQP!")
            channel.basic_consume('test_queue', consumer_callback, auto_ack=True)
            channel.start_consuming()
            connection.close()
            assert RECEIVED_HELLO

if __name__ == "__main__":
    arguments = docopt(__doc__, version='Test AWS Connection 1.0')
    host = arguments["<host>"]
    port = arguments["<port>"]
    vhost = arguments['<vhost>']
    user = arguments['<user>']
    pwd = arguments['<password>']
    args = [host, port, vhost, user, pwd]
    sys.argv = args
    suite = unittest.TestLoader().loadTestsFromTestCase(BlockingConnectionTests)
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)



