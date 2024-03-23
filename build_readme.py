from dateutil.relativedelta import relativedelta
from datetime import datetime, date
from urllib.request import urlopen
from time import strftime
import feedparser
import pathlib
import json
import re
import os

root = pathlib.Path(__file__).parent.resolve()


def replace_writing(content, marker, chunk, inline=False):
    r = re.compile(
        r'<!\-\- {} starts \-\->.*<!\-\- {} ends \-\->'.format(marker, marker),
        re.DOTALL,
    )
    if not inline:
        chunk = '\n{}\n'.format(chunk)
    chunk = '<!-- {} starts -->{}<!-- {} ends -->'.format(marker, chunk, marker)
    return r.sub(chunk, content)


def fetch_writing():
    entries = feedparser.parse('https://vool.ie/feed/')['entries']
    top5_entries = entries[:6]

    entry_count = len(entries)

    return [
               {
                   'title': entry['title'],
                   'url': entry['link'].split('#')[0],
                   'published': strftime("%B %Y", entry['published_parsed'])
               }
               for entry in top5_entries
           ], entry_count


def calc_moons():
    diff = relativedelta(datetime(year=1977, month=4, day=1), date.today())
    return abs(diff.years * 12 + diff.months)


def fetch_toot_count():
    url = "https://mastodon.ie/api/v1/accounts/lookup?acct=@phelan"
    res = urlopen(url)
    data_json = json.loads(res.read())
    return data_json['statuses_count']

def fetch_reading():
    ol_base_url='https://openlibrary.org'
    url = "https://openlibrary.org/people/{}/books/currently-reading.json".format(os.environ['OPENLIBRARY_USER'])
    ol_cover_url = "https://covers.openlibrary.org/b/olid/{}-M.jpg"
    response = urlopen(url)
    data_json = json.loads(response.read())
    books = data_json['reading_log_entries']

    return [
               {
                   'title': entry['work']['title'],
                   'url': ol_base_url+entry['work']['key'],
                   'cover_url': ol_cover_url.format(entry['work']['cover_edition_key']),
                   'author': entry['work']['author_names'][0],
                   'author_url': ol_base_url+entry['work']['author_keys'][0],
               }
               for entry in books
           ]

if __name__ == '__main__':
    readme_path = root / 'README.md'
    readme = readme_path.open().read()
    entries, entry_count = fetch_writing()
    moon_count = calc_moons()
    toot_count = fetch_toot_count()
    reading = fetch_reading()
    print(f'Recent 6: {entries}, Total count: {entry_count}, Total moons: {moon_count}, Toot counts: {toot_count}')

    entries_md = '\n'.join(
        ['* [{title}]({url}) - {published}'.format(**entry) for entry in entries]
    )

    reading_md = '\n'.join(
        ['* ![{title}]({cover_url}) [{title}]({url}) - [{author}]({author_url})'.format(**book) for book in reading]
    )

    # Update entries
    rewritten_entries = replace_writing(readme, 'writing', entries_md)
    readme_path.open('w').write(rewritten_entries)

    # Update count
    readme = readme_path.open().read()
    rewritten_count = replace_writing(readme, 'writing_count', entry_count, inline=True)
    readme_path.open('w').write(rewritten_count)

    # Update moons
    readme = readme_path.open().read()
    rewritten_count = replace_writing(readme, 'writing_moons', moon_count, inline=True)
    readme_path.open('w').write(rewritten_count)

    # Update toots
    readme = readme_path.open().read()
    rewritten_count = replace_writing(readme, 'writing_toots', toot_count, inline=True)
    readme_path.open('w').write(rewritten_count)

    # Update reading
    readme = readme_path.open().read()
    rewritten_reading = replace_writing(readme, 'reading', reading_md)
    readme_path.open('w').write(rewritten_reading)
