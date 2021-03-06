import os
import threading
from multiprocessing import Barrier

import pika

class RabbitConnectionExample:
    """
    RabbitMQ operations
    """

    def __init__(self):
        """
        Initializes the class
        """
        self._url = os.environ['RABBITMQ_URL']
        self._barrier = Barrier(2, timeout=120)

    def connection_callback(self, conn):
        """
        Run on connecting to the server

        :param conn: The connection created in the previous step
        """
        self._connection.channel(on_open_callback=self.channel_callback)

    def channel_callback(self, ch):
        """
        Publish on the channel. You can use other methods with callbacks but only the channel
        creation method provides a channel. Other methods provide a frame you can choose to
        discard.

        :param ch: The channel established
        """
        properties = pika.BasicProperties(content_type='application/json')
        ch.basic_publish(exchange='test_exchange',
                                    routing_key='tests',
                                    properties=properties,
                                    body='Hello CloudAMQP!')
        self._barrier.wait(timeout=1)
        ch.close()
        self._connection.close()

    def run(self):
        """
        Runs the example
        """
        print("Running")
        def run_io_loop(conn):
            conn.ioloop.start()

        params = pika.URLParameters(self._url)
        self._connection = pika.SelectConnection(
            params, on_open_callback=self.connection_callback)
        if self._connection:
            t = threading.Thread(target=run_io_loop, args=(self._connection, ))
            t.start()
            self._barrier.wait(timeout=30)
            print("Waiting on Barrier")
            self._connection.ioloop.stop()
        else:
            raise ValueError

RabbitConnectionExample().run()
