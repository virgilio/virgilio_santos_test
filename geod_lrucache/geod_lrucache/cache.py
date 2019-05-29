# -*- coding: utf-8 -*-

""" Geo Distributed LRU Cache Library """

import time
import json

OP_SET = 'SET'
OP_UPDATE = 'UPDATE'
EXPIRATION_TIME = 60

#pylint: disable=too-few-public-methods
class Node():
    """ Doubly Linked List node """

    def __init__(self, key: str, data, _next=None, _prev=None):
        self.key = key
        self.next = _next
        self.prev = _prev
        self.data = data
        self.time = time.time()

    def __str__(self):
        return json.dumps({
            'key': self.key,
            'data': self.data,
            'updated': self.time
        })


class LRUCache():
    """ Base LRUCache class that operates locally """

    def __init__(self, size: int):
        self.size = size
        self.curr_length = 0
        self.head = None
        self.tail = None
        self.pages = {}

    def set_local(self, key: str, data):
        """ Set a item in local cache """
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
        """ Update a cache when it hits """
        if key in self.pages:
            node = self.pages[key]
            self._move_to_top(node)

    def evict_expired(self, snap_time, delta):
        """ Handle expired nodes """
        pages = list(self.pages.keys())
        for page in pages:
            if snap_time - self.pages[page].time > delta:
                self._evict_page(self.pages[page])

    def _evict_page(self, node: Node):
        """ Destroy a cache page """
        self._remove_item(node)
        del self.pages[node.key]

    def _create_page(self, node: Node):
        """ Create a cache page """
        self._add_item(node)
        self.pages[node.key] = node

    def _move_to_top(self, node: Node):
        """ Move an existent item to top of the list """
        if not self.head == node:
            self._remove_item(node)
            self._add_item(node)
        node.time = time.time()

    def _remove_item(self, node: Node):
        """ Removes a specific node """
        if node == self.tail and node == self.head:
            self.head = self.tail = None
        elif node == self.tail:
            self.tail = node.prev if node.prev else None
        elif node == self.head:
            self.head = node.next if node.next else None
        else:
            node.prev.next = node.next
            node.next.prev = node.prev
        node.next = None
        node.prev = None

    def _add_item(self, node: Node):
        """ Add an item to top of the List """
        if self.head:
            self.head.prev = node
            node.next = self.head
            self.head = node
        else:
            self.head = node
            self.tail = node

    def __str__(self):
        head = self.head
        items = []
        while head:
            items.append(json.loads(str(head)))
            head = head.next
        return json.dumps(items)

    def print(self):
        """ Print the Cache state to the screen """
        print(str(self))
