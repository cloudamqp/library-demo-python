import os
import pika

conn_str = os.environ["AMQP_URI"]
params = pika.URLParameters(conn_str)
connection = pika.BlockingConnection(params)
channel = connection.channel()

#declare the alternate exchange and queue
channel.exchange_declare("alt_exchange", "fanout")
channel.queue_declare("alt_queue")
channel.queue_bind("alt_queue", "alt_exchange")

# declare the primary exchange and a queue
args = {"alternate-exchange": "alt_exchange"}
channel.exchange_declare("primary_exchange", "direct", arguments=args)
channel.queue_declare(queue='test_queue')
channel.queue_bind("test_queue", "primary_exchange", "test_key")
channel.basic_publish(exchange='primary_exchange',
                      routing_key='test_key',
                      body="Hello CloudAMQP!")
channel.basic_publish(exchange='primary_exchange',
                      routing_key='bad_key',
                      body="Hello Alternate Exchange!")
channel.close()
connection.close()
