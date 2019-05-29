# -*- coding: utf-8 -*-

"""Top-level package for Geo Distributed LRU Cache."""

__author__ = """Virgilio Santos"""
__email__ = 'virgilio.santos@gmail.com'
__version__ = '0.1.0'

import time
import threading
import json
import zmq

from geopy.distance import distance

from .cache import LRUCache
from .queue import ZMQPublisher, ZMQSubscriber

OP_SET = 'SET'
OP_UPDATE = 'UPDATE'
EXPIRATION_TIME = 60

class DistributedLRUCache(LRUCache):
    """ Implements the Distributed Cache with LRU Strategy using ZMQ
    Queue to handle messages among servers"""

    def __init__(self, size: int, servers, port):
        super().__init__(size)
        self.servers = servers
        self.publisher = ZMQPublisher(port)
        self.start(servers)

    def buffer_operation(self, _op, key: str, data=None):
        """ Send operation to buffer """
        message = json.dumps({
            'op': _op,
            'key': key,
            'data': data
        })
        self.publisher.send(message)

    def get(self, key: str):
        """ Try to get a page by key, returns the data or False for a miss """
        if key in self.pages:
            self.buffer_operation(OP_UPDATE, key)
            return self.pages[key]
        return False

    def set(self, key: str, data):
        """ Set page """
        self.buffer_operation(OP_SET, key, data=data)

    def handle_operation(self, data):
        """ Operation Handler """
        message = json.loads(data.decode())
        if message['op'] == OP_SET:
            self.set_local(message['key'], message['data'])
        else:
            self.update_cache(message['key'])

    def handle_expiration(self):
        """ Expiration handler """
        self.evict_expired(time.time(), EXPIRATION_TIME)

    def start(self, servers):
        """ Start the subscriber Thread """
        self.subscriber_thread = ZMQSubscriber(servers, EXPIRATION_TIME, self)
        self.subscriber_thread.start()

    def destroy(self):
        """ Destroy all sockets """
        self.publisher.close()
        self.subscriber_thread.destroy()

    def closest_server(self, location):
        """ Calculates the closest server """
        distances = [
            {
                'server': server,
                'distance': distance(location.latlng, server['latlng']).m
            } for server in self.servers
        ]
        return min(distances, key=lambda s: s['distance'])
