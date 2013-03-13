import shelve
import requests
import time
from itertools import product
import pprint


def _encode(somelist):
    return "|".join([
        item.replace(' ', '+') for item in somelist
    ])


def _query(fromlist, tolist):

    api = "http://maps.googleapis.com/maps/api/distancematrix/json"
    api += "?origins=" + _encode(fromlist)
    api += "&destinations=" + _encode(tolist)
    api += "&sensor=false"
    print " ** Querying %r" % api

    # Google requires that we ... wait for a while.
    time.sleep(11)

    return requests.get(api).json()


def chunk(somelist, step=9):
    for i in range(0, len(somelist), step):
        yield somelist[i:i+step]


class DistanceCache(object):
    def __init__(self):
        self.lookup = shelve.open("distance-cache.db")

    def update(self, rows):
        addresses = [row['formatted_address'] for row in rows]
        new_addrs = [a for a in addresses if a not in self.lookup]

        print "Found %r new addrs not in the distance lookup" % len(new_addrs)

        if not new_addrs:
            return

        for o_chunk, d_chunk in product(chunk(new_addrs), chunk(addresses)):
            results = _query(o_chunk, d_chunk)
            if not results['rows']:
                raise ValueError(results['status'])
            assert results['origin_addresses']
            assert results['destination_addresses']
            for i, origin in enumerate(o_chunk):
                self.lookup[origin] = {}
                for j, dest in enumerate(d_chunk):
                    self.lookup[origin][dest] = \
                            results['rows'][i]['elements'][j]['duration']['value']

        # Reverse direction
        for o_chunk, d_chunk in product(chunk(addresses), chunk(new_addrs)):
            results = _query(o_chunk, d_chunk)
            if not results['rows']:
                raise ValueError(results['status'])
            assert results['origin_addresses']
            assert results['destination_addresses']
            for i, origin in enumerate(o_chunk):
                for j, dest in enumerate(d_chunk):
                    assert dest not in self.lookup[origin]
                    self.lookup[origin][dest] = \
                            results['rows'][i]['elements'][j]['duration']['value']

        self.lookup.sync()

    def __getitem__(self, key):
        return self.lookup[key]
