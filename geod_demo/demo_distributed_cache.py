""" Demo distributed cache """
from random import randint
from geod_lru_cache import DistributedLRUCache


def distributed_cache_demo():
    servers = [
        (5, [{'url': 'localhost', 'port': 5122, 'latlng': (41.49008, -71.312796)},
             {'url': 'localhost', 'port': 5123, 'latlng': (41.499498, -81.695391)},
             {'url': 'localhost', 'port': 5124, 'latlng': (52.5094982, 13.3765983)}]),
        (5, [{'url': 'localhost', 'port': 5122, 'latlng': (41.499498, -81.695391)},
             {'url': 'localhost', 'port': 5123, 'latlng': (41.49008, -71.312796)},
             {'url': 'localhost', 'port': 5124, 'latlng': (52.5094982, 13.3765983)}]),
        (5, [{'url': 'localhost', 'port': 5122, 'latlng': (52.5094982, 13.3765983)},
             {'url': 'localhost', 'port': 5123, 'latlng': (41.499498, -81.695391)},
             {'url': 'localhost', 'port': 5124, 'latlng': (41.49008, -71.312796)}]),
    ]

    cache = []
    for td in servers:
        cache.append(DistributedLRUCache(*td))
    for n in range(50):
        cache[randint(0, 2)].set('sample-{}'.format(n),
                                 'Sample data #{}'.format(n))
    for c in cache:
        c.print()

    for c in cache:
        print(c.get('sample-49'))
        print(c.get('sample-2'))

if __name__ == '__main__':
    distributed_cache_demo()
