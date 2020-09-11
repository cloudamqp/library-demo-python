"""
Creates and tests the select connection

Usage:
    test_select_connection <host> <port> <vhost> <user> <password>

Options:
    -h --help     Show this screen.
    --version     Show the version
"""

import sys
import threading
import unittest
from threading import Barrier

import pika
from docopt import docopt

def run_io_loop(conn):
    """
    Task that waits on io loop
    :param loop: Waits on io loop
    """
    conn.ioloop.start()


class RabbitConnectionExample:
    """
    RabbitMQ operations
    """

    def __init__(self, host, port, vhost, username, pwd):
        """
        Initializes the class

        :param host: Hostname for the connection
        :param port: Port to connect on
        :param vhost: Virtual host for the connection
        :param username: Username for the connection
        :param pwd: Password for the connection
        """
        self._host = host
        self._port = port
        self._vhost = vhost
        self._user = username
        self._pwd = pwd
        self._channel = None
        self._barrier = Barrier(2, timeout=120)
    def connection_callback(self, conn):
        """
        Run on connecting to the server

        :param conn: The connection created
        """
        print("Open channel")
        self.open_channel()

    def channel_callback(self, ch):
        """
        Create a channel callback.

        :param ch: The channel established
        """
        print("Channel created")
        self._channel = ch
        self._channel.exchange_declare("test_exchange", callback=self.exchange_declare_callback)

    def exchange_declare_callback(self, _unused_frame):
        """
        Declares an exchange

        :param _unused_frame: Unused frame
        """
        print("Exchange Declared")
        self._channel.queue_declare("test_queue", callback=self.queue_declare_callback)

    def queue_declare_callback(self, _unused_frame):
        """
        Binds the queue when declaration is ok

        :param _unused_frame:  The unused and returned frame
        """
        print("Queue Declared")
        print("Bound queue to exchange")
        self._channel.queue_bind("test_queue", "test_exchange", "tests", callback=self.queue_bind_callback)
        
    def queue_bind_callback(self, _unused_frame):
        """
        A queue bind callback

        :param _unused_frame: The unused and returned frame
        """
        print("Publish a messages")
        properties = pika.BasicProperties(app_id='rabbitmq_tutorial',
                                          content_type='application/json')
        self._channel.basic_publish(exchange='test_exchange',
                                    routing_key='tests',
                                    properties=properties,
                                    body="Hello CloudAMQP!",
                                    mandatory=True)
        print("Message published")
        try:
            self._barrier.wait(timeout=1)
            print("Acquired Barrier")
            if self._channel:
                self._channel.close()
            if self._connection:
                self._connection.close()
            print("Closed Connection and Channel")
        except Exception as e:
            print(sys.exc_info()[0])

    def open_channel(self):
        """
        Opens a channel on the provided channel.
        :param conn:  The connection
        """
        self._connection.channel(on_open_callback=self.channel_callback)

    def run(self):
        """
        Runs the example
        """
        conn_str = "amqp://{}:{}@{}:{}/{}".format(
            self._user, self._pwd, self._host, self._port, self._vhost)
        params = pika.URLParameters(conn_str)
        self._connection = pika.SelectConnection(
            params, on_open_callback=self.connection_callback)
        if self._connection:
            print("\nConnection Established")
            t = threading.Thread(target=run_io_loop, args=(self._connection, ))
            t.start()
            print("Waiting on Barrier")
            self._barrier.wait(timeout=30)
            print("Final Barrier Acquired")
            self._connection.ioloop.stop()
            

class SelectConnectionTests(unittest.TestCase):
    """
    Tests using the select connection in RabbitMQ
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

    def test_should_connect_and_send_message(self):
        """
        Test connecting to the broker
        """
        (host, port, vhost, user, pwd) = self.get_args()
        rmq_conn = RabbitConnectionExample(host, port, vhost, user, pwd)
        rmq_conn.run()


if __name__ == "__main__":
    arguments = docopt(__doc__, version='Test AWS Connection 1.0')
    host = arguments["<host>"]
    port = arguments["<port>"]
    vhost = arguments['<vhost>']
    user = arguments['<user>']
    pwd = arguments['<password>']
    args = [host, port, vhost, user, pwd]
    sys.argv = args
    suite = unittest.TestLoader().loadTestsFromTestCase(SelectConnectionTests)
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)

       
