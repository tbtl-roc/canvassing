""" Script for producing "walk sheets" for weekly canvassing. """

import csv
import math

mary = dict(
    longitude=-77.620369,
    latitude=43.184189,
)

origin = mary


def gather_rows():
    with open('foreclosures-2013-02-13.csv', 'rb') as csvfile:
        reader = csv.reader(csvfile, delimiter="|")
        rows = [row for row in reader]
        headers, rows = rows[0], rows[1:]
        results = [dict(zip(headers, row)) for row in rows]

        for row in results:
            row['longitude'] = float(row['longitude'])
            row['latitude'] = float(row['latitude'])

        return results


def write_csv(rows, suffix):
    headers = [
        'formatted_address', 'grantee', 'grantor', 'filing_date',
        'assessed_value', 'latitude', 'longitude']
    rows = [headers] + [[row[key] for key in headers] for row in rows]

    with open('output-%s.csv' % suffix, 'w') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows(rows)


def as_the_crow_flies(entry):
    """ The distance formula is oldschool. """
    return math.sqrt(
        (entry['longitude'] - origin['longitude'])**2 +
        (entry['latitude'] - origin['latitude'])**2
    )


def split_into_groups_by_polar_coordinates(rows, N=1):
    """ Take a list of rows, and split it into N groups. """
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

        # Use theta to put each row in one of N buckets
        i = int(row['theta'] / (2 * math.pi) * N)
        results[i].append(row)
        print "(%f, %f) -> (%f, %f)" % (
            row['normalized_longitude'],
            row['normalized_latitude'],
            row['r'],
            row['theta']
        )

    print "Split into groups like:", map(len, results)
    return results

metric = as_the_crow_flies
split_into_groups = split_into_groups_by_polar_coordinates


def for_today():
    # expect there to be this many teams
    N = 4

    rows = gather_rows()
    rows = [row for row in rows if '14621' in row['formatted_address']]
    rows = sorted(rows, lambda b, a: cmp(a['filing_date'], b['filing_date']))
    rows = rows[:100]

    # Break into N teams
    list_of_lists = split_into_groups(rows, N)

    # Sort each team's list by distance from the origin location.
    list_of_lists = [
        sorted(sublist, lambda a, b: cmp(metric(a), metric(b)))
        for sublist in list_of_lists
    ]
    for i, sublist in enumerate(list_of_lists):
        write_csv(rows, suffix="team-%i" % i)

for_today()