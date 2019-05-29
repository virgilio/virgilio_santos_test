import json
from os import environ
from flask import Flask, request
from flask_restful import Resource, Api
from geocoder import ip

from geod_lrucache import DistributedLRUCache

app = Flask(__name__)
api = Api(app)

def get_lat_lng(location: str):
    return tuple([float(x) for x in location.strip('()').split(', ')])

def get_server(server: str):
    return tuple(server.split(':'))

def filter_env(search: str):
    return list(filter(lambda s: s.startswith(search), environ.keys()))

def get_server_info():
    _servers = [get_server(environ[s]) for s in filter_env('SERVER_')]
    _latlngs = [get_lat_lng(environ[l]) for l in filter_env('LATLNG_')]

    _servers = [_servers[i] + _latlngs[i] for i in range(len(_servers))]
    return [{'url': s[0], 'port': int(s[1]), 'latlng': s[2]} for s in _servers]

publisher_port = int(environ['PUB_PORT'])
cache_size = int(environ['CACHE_SIZE'])
cache = DistributedLRUCache(cache_size, get_server_info(), publisher_port)

class Cache(Resource):
    def get(self, key):
        page = cache.get(key)
        return page.data if page else {key: False}

    def put(self, key):
        cache.set(key, request.form['data'])
        return {key: json.loads(str(cache))}

api.add_resource(Cache, '/cache/<string:key>')

class CacheDashboard(Resource):
    def get(self):
        location = ip(request.environ['REMOTE_ADDR'])
        return {
            'closest_server': cache.closest_server(location),
            'cache_state': json.loads(str(cache))
        }

api.add_resource(CacheDashboard, '/')

if __name__ == '__main__':
    app.run(host='localhost', debug=True)
