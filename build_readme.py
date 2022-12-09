import feedparser
import pathlib
import re
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
from time import strftime
import tweepy
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


def fetch_tweet_count():
    # Twitter credentials
    CONSUMER_KEY = os.environ['TWITTER_CONSUMER_KEY']
    CONSUMER_SECRET = os.environ['TWITTER_CONSUMER_SECRET']
    ACCESS_TOKEN = os.environ['TWITTER_ACCESS_TOKEN']
    ACCESS_TOKEN_SECRET = os.environ['TWITTER_ACCESS_TOKEN_SECRET']

    client = tweepy.Client(
        consumer_key=CONSUMER_KEY,
        consumer_secret=CONSUMER_SECRET,
        access_token=ACCESS_TOKEN,
        access_token_secret=ACCESS_TOKEN_SECRET
    )

    response = client.get_me(user_fields=["public_metrics"])

    metrics = response.data.public_metrics

    return metrics['tweet_count']

if __name__ == '__main__':
    readme_path = root / 'README.md'
    readme = readme_path.open().read()
    entries, entry_count = fetch_writing()
    moon_count = calc_moons()
    tweet_count = fetch_tweet_count()
    print(f'Recent 6: {entries}, Total count: {entry_count}, Total moons: {moon_count}, Tweet counts: {tweet_count}')

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

    # Update moons
    readme = readme_path.open().read()  # Need to read again with updated entries
    rewritten_count = replace_writing(readme, 'writing_tweets', tweet_count, inline=True)
    readme_path.open('w').write(rewritten_count)
