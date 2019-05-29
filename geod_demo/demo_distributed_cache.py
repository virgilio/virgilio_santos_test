""" Demo distributed cache """
from random import randint
from geod_lrucache import DistributedLRUCache
from geocoder import ip

def distributed_cache_demo():
    """ Method creates 3 cache instances and runs 50 samples prints two
    retrieval (a hit and a miss) and a proximity report  """
    servers = [
        (5, [{'url': 'localhost', 'port': 5122, 'latlng': (41.49008, -71.312796)},
             {'url': 'localhost', 'port': 5123, 'latlng': (41.499498, -81.695391)},
             {'url': 'localhost', 'port': 5124, 'latlng': (52.5094982, 13.3765983)}], 5122),
        (5, [{'url': 'localhost', 'port': 5122, 'latlng': (41.499498, -81.695391)},
             {'url': 'localhost', 'port': 5123, 'latlng': (41.49008, -71.312796)},
             {'url': 'localhost', 'port': 5124, 'latlng': (52.5094982, 13.3765983)}], 5123),
        (5, [{'url': 'localhost', 'port': 5122, 'latlng': (52.5094982, 13.3765983)},
             {'url': 'localhost', 'port': 5123, 'latlng': (41.499498, -81.695391)},
             {'url': 'localhost', 'port': 5124, 'latlng': (41.49008, -71.312796)}], 5124),
    ]

    cache = []
    for _td in servers:
        cache.append(DistributedLRUCache(*_td))
    for _sd in range(50):
        cache[randint(0, 2)].set('sample-{}'.format(_sd),
                                 'Sample data #{}'.format(_sd))
    for instance in cache:
        instance.print()

    for instance in cache:
        location = ip('201.17.101.45')
        print(instance.get('sample-49'))
        print(instance.get('sample-2'))
        print(instance.closest_server(location))

if __name__ == '__main__':
    distributed_cache_demo()
