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
    """ """

    def __init__(self, size: int, servers, port):
        super().__init__(size)
        self.servers = servers
        self.publisher = ZMQPublisher(port)
        self.start(servers)

    def buffer_operation(self, op, key: str, data=None):
        message = json.dumps({
            'op': op,
            'key': key,
            'data': data
        })
        self.publisher.send(message)

    def get(self, key: str):
        if key in self.pages:
            self.buffer_operation(OP_UPDATE, key)
            return self.pages[key]
        else:
            return False

    def set(self, key: str, data):
        self.buffer_operation(OP_SET, key, data=data)

    def handle_operation(self, data):
        message = json.loads(data.decode())
        if message['op'] == OP_SET:
            self.set_local(message['key'], message['data'])
        else:
            self.update_cache(message['key'])

    def handle_expiration(self):
        self.evict_expired(time.time(), EXPIRATION_TIME)

    def start(self, servers):
        self.subscriber_thread = ZMQSubscriber(servers, EXPIRATION_TIME, self)
        self.subscriber_thread.start()

    def destroy(self):
        self.publisher.close()
        self.subscriber_thread.destroy()

    def closest_server(self, location):
        distances = [
            {
                'server': server,
                'distance': distance(location.latlng, server['latlng'])
            } for server in self.servers
        ]
        return min(distances, key=lambda s: s['distance'])
