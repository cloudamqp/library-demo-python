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
