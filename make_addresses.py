""" This is the main script for producing "walk sheets" for weekly canvassing.

It takes the full list of foreclosures as its input.  You can get that file
(on Linux) with the following command.

    $ wget http://monroe-threebean.rhcloud.com/export.csv

It also requires another file "alltime-knowledge.csv" which is just a list of
addresses and our notes about them.. "should we canvas this house again?
should we not?""

As it stands now, this program does the following things (in order):

    - Read in all the foreclosures.
    - Read in a database of our notes about addresses (i.e.)

      - Merge our notes in with the latest foreclosure dump from the cloud.
      - Mark new foreclosures we haven't seen before as "unvisited"

    - Sort the foreclosures, newest ones first.
    - Discard all foreclosures not in the 14621 zip code.
    - Discard everything but the latest 100 foreclosures (in 14621).
    - Break those latest foreclosures up amongst N teams (like 3 or 4 teams)

      - Do that by drawing a circle around the central house we're focusing on.
        Divide that circle up like pie slices (triangle wedges).  If we have 3
        teams, then three equal slices.  Four teams, then four equal slices.
      - All the addresses that fall into each slice are assigned to the
        different teams.

    - Finally, for each team's new list.  Sort those by "travelling salesman"
      logic.
    - Write those lists out to files in an ``output/`` directory.  Name each
      team's file including the week of the year (so we can keep track of them
      over time).  They're named something like
      ``output/week-10-2013-team-0.csv`` and ``output/week-10-2013-team-1.csv``

"""

import csv
import math
import datetime
import os
import sys

from lib.greedy_tsp import solve_tsp

mary = dict(
    longitude=-77.620369,
    latitude=43.184189,
)

origin = mary

MAXIMUM_TEAM_SIZE = 25


def gather_rows():
    results = []
    fname = 'foreclosures-%s.csv' % datetime.datetime.now().strftime("%F")
    if not os.path.exists(fname):
        print fname, "does not exist.  Try:"
        print "", "wget http://monroe-threebean.rhcloud.com/export.csv -O", fname
        sys.exit(1)

    with open(fname, 'rb') as csvfile:
        reader = csv.reader(csvfile, delimiter="|")
        rows = [row for row in reader]
        headers, rows = rows[0], rows[1:]
        results.extend([dict(zip(headers, row)) for row in rows])

        for row in results:
            row['longitude'] = float(row['longitude'])
            row['latitude'] = float(row['latitude'])

    with open('alltime-knowledge.csv', 'rb') as csvfile:
        reader = csv.reader(csvfile, delimiter=",")
        rows = [row for row in reader]
        rows = [row[0:2] for row in rows]
        headers, rows = rows[0], rows[1:]
        knowledge = dict(rows)

    for row in results:
        row['code'] = knowledge.get(row['formatted_address'], 'unvisited')

    return results


def write_csv(rows, suffix):
    headers = [
        'code', 'formatted_address', 'grantee', 'grantor', 'filing_date',
        'assessed_value', 'latitude', 'longitude']
    rows = [headers] + [[row[key] for key in headers] for row in rows]

    week_number = datetime.datetime.now().isocalendar()[1]
    year = datetime.datetime.now().year
    fname = 'output/week-%02i-%s-%s.csv' % (week_number, year, suffix)
    print "  Writing", fname
    with open(fname, 'w') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows(rows)


def distance(a, b):
    """ Oldschool """
    return math.sqrt(
        (a['longitude'] - b['longitude'])**2 +
        (a['latitude'] - b['latitude'])**2
    )


def as_the_crow_flies(entry):
    """ This returns the arial distance of an address from our epicenter """
    return distance(entry, origin)


def _quadrant_fudge(row):
    # http://www.mathsisfun.com/polar-cartesian-coordinates.html
    if row['normalized_latitude'] > 0:
        if row['normalized_longitude'] > 0:
            return 0  # Quadrant I
        else:
            return math.pi  # Quadrant II
    else:
        if row['normalized_longitude'] > 0:
            return math.pi  # Quadrant III
        else:
            return 2 * math.pi  # Quadrant IV


def split_into_groups_by_polar_coordinates(rows, N=1):
    """ Take a list of rows, and split it into N groups.

    Like slices of a pie or a pizza.
    """

    results = [list() for i in range(N)]
    for row in rows:
        # normalize each row
        row['normalized_longitude'] = row['longitude'] - origin['longitude']
        row['normalized_latitude'] = row['latitude'] - origin['latitude']

        # convert lat/lon to polar coordinates
        row['r'] = math.sqrt(
            row['normalized_longitude']**2 +
            row['normalized_latitude']**2
        )
        row['theta'] = math.atan(
            row['normalized_latitude'] / row['normalized_longitude']
        )

        row['theta'] = row['theta'] + _quadrant_fudge(row)
        while row['theta'] > (2 * math.pi):
            row['theta'] -= (2 * math.pi)

        # Use theta to put each row in one of N buckets
        i = int(row['theta'] / (2 * math.pi) * N)
        results[i].append(row)

    print "Split into groups like:", map(len, results)

    return results

def split_into_groups_by_k_means(rows, N=1):
    """ Split into groups by kmeans clustering.  Smart. """

    print "Splitting into %r groups with kmeans clustering." % N

    import numpy
    import scipy.cluster.vq

    data = numpy.matrix([
        (row['latitude'], row['longitude']) for row in rows
    ]).getA()

    centroids, idx = scipy.cluster.vq.kmeans2(data, N)

    teams = [[] for i in range(N)]
    for i, index in enumerate(idx):
        teams[index].append(rows[i])

    return teams

metric = as_the_crow_flies
#split_into_groups = split_into_groups_by_polar_coordinates
split_into_groups = split_into_groups_by_k_means


def sort_with_tsp(sublist):
    """ Sort a shortlist of addresses with travelling salesman logic """

    # Sort dumbly first to help out.
    sublist = sorted(sublist, lambda a, b: cmp(metric(a), metric(b)))

    # First, build a square matrix of the distances between all addrs.
    G = [[
        distance(sublist[i], sublist[j]) for j in range(len(sublist))
    ] for i in range(len(sublist))]

    # tsp that.
    indices = solve_tsp(G)

    # Nasty!
    return map(sublist.__getitem__, indices)


def merge_smallest_into_second_smallest(list_of_lists):
    """ Take the smallest team and merge it into the second smallest team. """

    lengths = map(len, list_of_lists)
    index_of_first_smallest = lengths.index(min(lengths))
    lengths.pop(index_of_first_smallest)
    index_of_second_smallest = lengths.index(min(lengths))

    smallest = list_of_lists.pop(index_of_first_smallest)
    list_of_lists[index_of_second_smallest] += smallest
    return list_of_lists


def should_be_included(row):
    """ Criteria for whether or not we should canvas an address """
    return all([
        # All of these must be true
        '14621' in row['formatted_address']
    ]) and any([
        # At least one of these must be true
        'unvisited' == row['code'],
        'should return' in row['code'],
    ])


def main():
    """ Main entry point.  Read, organize, write. """

    # expect there to be this many teams
    N = 10

    rows = gather_rows()
    rows = sorted(rows, lambda b, a: cmp(a['filing_date'], b['filing_date']))

    # Throw out rows that are not "unvisited" or whatever.
    rows = filter(should_be_included, rows)

    # Take only the first 100 properties
    rows = rows[:100]

    # Break into N teams
    list_of_lists = split_into_groups(rows, N)
    list_of_lists = [lst for lst in list_of_lists if lst]
    print " * Down to", len(list_of_lists), "lists"

    # Just get rid of our smallest N teams.
    num_merges = 0
    for i in range(num_merges):
        list_of_lists = merge_smallest_into_second_smallest(list_of_lists)

    # Sort each team's list travelling salesman style.
    list_of_lists = map(sort_with_tsp, list_of_lists)

    # Also limit the teams to *at most* N addresses.
    list_of_lists = [lst[:MAXIMUM_TEAM_SIZE] for lst in list_of_lists]

    print "Limited to groups like:", map(len, list_of_lists)

    for i, sublist in enumerate(list_of_lists):
        write_csv(sublist, suffix="team-%i" % i)

if __name__ == '__main__':
    main()
