# -*- coding: utf-8 -*-

""" Geo Distributed LRU Cache Library """

import time
import json

from geocoder import ip
from geopy.distance import distance

from .queue import ZMQPublisher, ZMQSubscriber

OP_SET = 'SET'
OP_UPDATE = 'UPDATE'
EXPIRATION_TIME = 60


class Node():
    """ """

    def __init__(self, key: str, data, _next=None, _prev=None):
        self.key = key
        self._next = _next
        self._prev = _prev
        self.data = data
        self.time = time.time()

    def __str__(self):
        return json.dumps({
            'key': self.key,
            'data': self.data,
            'updated': self.time
        })


class LRUCache():
    """ """

    def __init__(self, size: int):
        self.size = size
        self.curr_length = 0
        self.head = None
        self.tail = None
        self.pages = {}

    def set_local(self, key: str, data):
        if key in self.pages:
            node = self.pages[key]
            if not node.data == data:
                self.pages[key].data = data
            self._move_to_top(node)
        else:
            node = Node(key, data)
            if not len(self.pages) < self.size:
                self._evict_page(self.tail)
            self._create_page(node)

    def update_cache(self, key: str):
        if key in self.pages:
            node = self.pages[key]
            self._move_to_top(node)

    def evict_expired(self, snap_time, delta):
        pages = list(self.pages.keys())
        for page in pages:
            if snap_time - self.pages[page].time > delta:
                self._evict_page(self.pages[page])

    def _evict_page(self, node):
        self._remove_item(node)
        del self.pages[node.key]

    def _create_page(self, node):
        self._add_item(node)
        self.pages[node.key] = node

    def _move_to_top(self, node: Node):
        if not self.head == node:
            self._remove_item(node)
            self._add_item(node)
        node.time = time.time()

    def _remove_item(self, node: Node):
        if node == self.tail and node == self.head:
            self.head = self.tail = None
        elif node == self.tail:
            self.tail = node._prev if node._prev else None
        elif node == self.head:
            self.head = node._next if node._next else None
        else:
            node._prev._next = node._next
            node._next._prev = node._prev
        node._next = None
        node._prev = None

    def _add_item(self, node: Node):
        if self.head:
            self.head._prev = node
            node._next = self.head
            self.head = node
        else:
            self.head = node
            self.tail = node

    def print(self):
        head = self.head
        items = []
        while head:
            items.append(json.loads(str(head)))
            head = head._next
        print(items)
        return items

