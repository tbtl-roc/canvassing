import csv
import math

mary = dict(
    latitude=43.184189,
    longitude=-77.620369,
)

def gather_rows():
    with open('foreclosures-2013-02-13.csv', 'rb') as csvfile:
        reader = csv.reader(csvfile, delimiter="|")
        rows = [row for row in reader]
        headers, rows = rows[0], rows[1:]
        return [dict(zip(headers, row)) for row in rows]

def write_csv(rows):
    headers = ['formatted_address', 'grantee', 'grantor', 'filing_date', 'assessed_value', 'latitude', 'longitude']
    rows = [headers] + [[row[key] for key in headers] for row in rows]
    with open('output.csv', 'w') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows(rows)

def f(entry):
    return math.sqrt(
        (float(entry['latitude']) - mary['latitude'])**2 +
        (float(entry['longitude']) - mary['longitude'])**2
    )


def for_today():
    rows = gather_rows()
    rows = [row for row in rows if '14621' in row['formatted_address']]
    rows = sorted(rows, lambda b, a: cmp(a['filing_date'], b['filing_date']))
    rows = rows[:100]
    rows = sorted(rows, lambda a, b: cmp(f(a), f(b)))
    write_csv(rows)

for_today()
