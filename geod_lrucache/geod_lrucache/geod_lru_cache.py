import time
import threading
import json
import zmq

from geocoder import ip
from geopy.distance import distance

class Node():
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

OP_SET = 'SET'
OP_UPDATE = 'UPDATE'
EXPIRATION_TIME = 60

class LRUCache():
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


class ZMQPublisher:
    def __init__(self, port):
        context = zmq.Context()
        self.publisher = context.socket(zmq.PUB)
        self.publisher.bind("tcp://*:%s" % port)

    def send(self, message):
        poller = zmq.Poller()
        poller.register(self.publisher, zmq.POLLOUT)
        sock_map = poller.poll(50)
        assert len(sock_map) == 1
        self.publisher.send(message.encode())
        time.sleep(0.01)

    def close(self):
        self.publisher.close()


class ZMQSubscriber(threading.Thread):
    def __init__(self, servers, expiration_time, handler):
        super().__init__()
        context = zmq.Context()
        self.subscriber = context.socket(zmq.SUB)
        self.handler = handler
        self.expiration_time = expiration_time
        for server in servers:
            self.subscriber.connect('tcp://{}:{}'.format(server['url'],
                                                         server['port']))
        self.subscriber.setsockopt(zmq.SUBSCRIBE, b'')

    def run(self):
        start_time = time.time()
        self.subscriber.RCVTIMEO = 50
        while True:
            try:
                data = self.subscriber.recv()
                self.handler.handle_operation(data)
            except zmq.error.Again:
                if time.time() - start_time > self.expiration_time:
                    self.handler.handle_expiration()
                    start_time = time.time()

    def destroy(self):
        self.subscriber.close()


class DistributedLRUCache(LRUCache):
    def __init__(self, size: int, servers, server=None):
        super().__init__(size)
        self.server = self.closest_server(servers) if not server else server
        self.publisher = ZMQPublisher(self.server['port'])
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

    @staticmethod
    def closest_server(servers):
        me = ip('me')
        distances = [
            {
                'port': server['port'],
                'distance': distance(me.latlng, server['latlng'])
            } for server in servers
        ]
        return min(distances, key=lambda s: s['distance'])
