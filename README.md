# Ormuco Test

## Objectives
This repository is intendend to provide access to Ormuco in order to evaluate
tests given

## Design
* The first question was written as a simple function inside a util module. It uses the idea that a line be seen as a set of points and whenever its set has a intersection of another one set, it means it overlaps each other
* The second one as a class inside the util module that implements Python magic methods so you can have a clean work and compare versions like Version('1.2') > Version('1.1') or even aliases like v('1.2') >= v('2.9'). It uses SemVer as reference of versioning
* The last challenge is implemented as a full, ready to deploy library that can grow as it gets more features. For that I've used a implementation that considers a one way data flow using a Publisher/Subscriber pattern. All servers read from a local cache but only writes based on all events on the overall cache scenario. The expiration is handled locally while operations are not being handled.

## Getting Started
* To quickly use the code, download it where it can be seen by your application then
```python
from util.util import is_overlapped, Version as v

is_overlapped((1,5), (2,6))
v('1.2') > v('1.3')
```
```bash
 ~/virgilio_santos_test $ pip install -r geod_demo/requirements.txt ./geod_lrucache/
```
```python
    from geocoder import ip
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

    _cache = cache[0]
    data = _cache.get('sample-data'):
    if not data:
        data = _cache.set('sample-data', 'Data data data!')
    me = ip('me')
    closest_server = _cache.closest_server(me)
    ## ... ###

```

## Organization
The repo is organized in the following way:
1. A util directory with a simple python package where Question A and B of the test are implemented inside a util.py file and can be tested using test_util.py file
 ```bash
 ~/virgilio_santos_test $ cd util/
 ~/virgilio_santos_test/util $ nosetests test_util.py
 ```
 For implementation details, please read the functions doc strings.

2. A geod_lrucache directory which contains a full structured python lib to be installed with a package manager like pip. It's based on cookiecutter `audreyr/cookiecutter-pypackage` template and ready to grow as a robust piece of code. Checkout [geod_lrucache/README.rst](https://github.com/virgilio/virgilio_santos_test/blob/master/geod_lrucache/README.rst) for more information about the library itself and implementation design details.
**For the test specific purposes** please look into: `virgilio_santos_test/geod_lrucache/geod_lrucache/geod_lrucache.py` file

3. A geod_demo directory with 2 demos that should show how to integrate the library to your code easily.

* for `geod_demo/demo_distributed_cache.py`, you need to:
``` ~/virgilio_santos_test $ # initialize a python3 environment of your preference
 ~/virgilio_santos_test $ cd geod_demo && virtualenv env
 ~/virgilio_santos_test $ . env/bin/activate
 ~/virgilio_santos_test $ pip install -r requirements.txt
 ~/virgilio_santos_test $ pip install ../geod_lrucache/
 ~/virgilio_santos_test $ python demo_distributed_cache.py
```

* for `geod_demo/demo_http_cache_server.py` you have to use docker and docker-compose:
```bash
~/virgilio_santos_test $ cd geod_demo/http_cache_server/
~/virgilio_santos_test $ docker-compose up
```
You will have available 3 servers (`localhost:{5000,5001,5002}`) with 3 base url:
  * `GET /cache/<key>` to add a item to a cache
  * `PUT /cache/<key>` body should have `data` either Json `{"data": "sample data"}` or url `data=sample data`
  * `GET /` to see a overall state of the cache

in the same directory you can find `load.py` that should load data inside this three server so you can verify the consistency of the cache synchronization process

## Further info
For more information please contact author through `virgilio.santos` at `gmail.com`

## Next steps
1. Unit tests for the library classes and methods
2. Submit code to QA/CI and coverage services
3. Create a autodiscover service so one can add and remove servers on the fly based on
4. Better requirement handling
5. Benchmark the Cache library

## References
1. https://memcached.org/blog/modern-lru
2. https://en.wikipedia.org/wiki/Cache_replacement_policies
3. https://www.quora.com/What-is-the-best-way-to-Implement-an-LRU-Cache
