# -*- coding: utf-8 -*-

""" Queue actor for pattern publisher/subscriber """

import time
import threading
import zmq

class ZMQPublisher:
    """ Queue publisher """
    def __init__(self, port):
        context = zmq.Context()
        self.publisher = context.socket(zmq.PUB)
        self.publisher.bind("tcp://*:%s" % port)

    def send(self, message):
        """ Publish message to the queue """
        poller = zmq.Poller()
        poller.register(self.publisher, zmq.POLLOUT)
        sock_map = poller.poll(50)
        assert len(sock_map) == 1
        self.publisher.send(message.encode())
        time.sleep(0.01)

    def close(self):
        """ Close socket """
        self.publisher.close()


class ZMQSubscriber(threading.Thread):
    """ Queue Listener (Subscriber) """
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
        """ Closes socket """
        self.subscriber.close()
