""" Flask application to serve a HTTP base cache using geod_lrucache """
import json
from os import environ
from flask import Flask, request
from flask_restful import Resource, Api
from geocoder import ip

from geod_lrucache import DistributedLRUCache

APP = Flask(__name__)
API = Api(APP)

def get_lat_lng(location: str):
    """ returns a tuple based on a string representation """
    return tuple([float(x) for x in location.strip('()').split(', ')])

def get_server(server: str):
    """ return the server data """
    return tuple(server.split(':'))

def filter_env(search: str):
    """ filter the enviroment keys looking for search key """
    return list(filter(lambda s: s.startswith(search), environ.keys()))

def get_server_info():
    """ process enviroment variables to retrieve server information """
    _servers = [get_server(environ[s]) for s in filter_env('SERVER_')]
    _latlngs = [get_lat_lng(environ[l]) for l in filter_env('LATLNG_')]

    _servers = [_servers[i] + _latlngs[i] for i in range(len(_servers))]
    return [{'url': s[0], 'port': int(s[1]), 'latlng': s[2]} for s in _servers]

CACHE = DistributedLRUCache(int(environ['CACHE_SIZE']),
                            get_server_info(), int(environ['PUB_PORT']))

#pylint: disable=no-self-use
class Cache(Resource):
    """ Cache api resource """
    def get(self, key):
        """ get request handler """
        page = CACHE.get(key)
        return page.data if page else {key: False}

    def put(self, key):
        """ put request handler """
        CACHE.set(key, request.form['data'])
        return {key: json.loads(str(CACHE))}

API.add_resource(Cache, '/cache/<string:key>')

class CacheDashboard(Resource):
    """ Dashboard api Resource """
    def get(self):
        """ get request handler """
        location = ip(request.environ['REMOTE_ADDR'])
        return {
            'closest_server': CACHE.closest_server(location),
            'cache_state': json.loads(str(CACHE))
        }

API.add_resource(CacheDashboard, '/')

if __name__ == '__main__':
    APP.run(host='localhost', debug=True)
