import json
from flask import Flask, request
from flask_restful import Resource, Api

from geod_lrucache import DistributedLRUCache

app = Flask(__name__)
api = Api(app)

cache = DistributedLRUCache(5, [
    {'url': 'localhost', 'port': 5122, 'latlng': (41.49008, -71.312796)},
    {'url': 'localhost', 'port': 5123, 'latlng': (41.499498, -81.695391)},
    {'url': 'localhost', 'port': 5124, 'latlng': (52.5094982, 13.3765983)}
])

class Cache(Resource):
    def get(self, key):
        page = cache.get(key)
        return page if page else {key: False}

    def put(self, key):
        cache.set(key, request.form['data'])
        return {key: ''}

api.add_resource(Cache, '/cache/<string:key>')

class CacheDashboard(Resource):
    def get(self):
        return cache.print()

api.add_resource(CacheDashboard, '/')

if __name__ == '__main__':
    app.run(debug=True)
