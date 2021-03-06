import csv
import sys


def read_in_addresses(filename):
    results = []
    with open(filename, 'r') as csvfile:
        reader = csv.reader(csvfile)
        rows = [row for row in reader]
        headers, rows = rows[0], rows[1:]
        results.extend([dict(zip(headers, row)) for row in rows])

    return [row['formatted_address'] for row in results]


def make_map_query(filename):
    results = read_in_addresses(filename)

    print
    print " ** Map URL for", filename
    print " ** Copy and paste this into your browser."
    print
    query = "from: " + " to: ".join(results)
    url = "https://maps.google.com/maps?q=" + query.replace(' ', '+')
    print url


if __name__ == '__main__':
    make_map_query(sys.argv[-1])
