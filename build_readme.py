import feedparser
import pathlib
import re
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
from time import strftime

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
    entries = feedparser.parse('http://vool.ie/feed/')['entries']
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

if __name__ == '__main__':

    readme_path = root / 'README.md'
    readme = readme_path.open().read()
    entries, entry_count = fetch_writing()
    moon_count = calc_moons()
    print(f'Recent 6: {entries}, Total count: {entry_count}, Total moons: {moon_count}')

    entries_md = '\n'.join(
        ['* [{title}]({url}) - {published}'.format(**entry) for entry in entries]
    )

    # Update entries
    rewritten_entries = replace_writing(readme, 'writing', entries_md)
    readme_path.open('w').write(rewritten_entries)

    # Update count
    readme = readme_path.open().read()  # Need to read again with updated entries
    rewritten_count = replace_writing(readme, 'writing_count', entry_count, inline=True)
    readme_path.open('w').write(rewritten_count)

    # Update moons
    readme = readme_path.open().read()  # Need to read again with updated entries
    rewritten_count = replace_writing(readme, 'writing_moons', moon_count, inline=True)
    readme_path.open('w').write(rewritten_count)