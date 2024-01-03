#!/usr/bin/env python
# RSS feed mirror on Misskey
# Copyright (C) 2021  Nguyễn Gia Phong
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

from configparser import ConfigParser
from contextlib import AsyncExitStack
from functools import partial
from re import split, sub

from datetime import datetime
from datetime import timedelta

from feedparser import parse
from httpx import AsyncClient, Limits
from loca import Loca
from markdownify import markdownify as md
from trio import open_nursery, run


def truncate(string, length, end='…'):
    """Return string truncated to length, ending with given character."""
    if len(string) <= length: return string
    return string[:length-len(end)] + end


async def create(client, **note):
    """Create the given note and return its ID."""
    if len(note['cw']) == 0:
        del note['cw']
    response = await client.post('notes/create', json=note)
    return response.json()['createdNote']['id']


async def post(job, client, link, title, summary):
    """Post the given entry to Misskey.

    In case the link was already posted, the entry shall be skipped.
    """
    visibility = job.get('visibility', 'home')
    search = await client.post('notes/search', json={'query': link,
                                                     'userId': job['user'],
                                                     'i': job['token']})
    if search.json(): return

    note = partial(create, client, i=job['token'], visibility=visibility,
                   cw=truncate(title, job.getint('cw')))
    original = f'Original: {link}'
    rest = '\n\n'.join((*map(partial(sub, r'\s+', ' '),
                             split(r'\s*\n{2,}\s*', md(summary).strip())),
                        original))
    limit = job.getint('text')
    parent = None

    while len(rest) > limit:
        index = rest.rfind('\n\n', 0, limit+2)  # split paragraphs
        if index < 0:
            index = rest.rfind('. ', 0, limit+1)  # split sentences
            if index < 0:
                parent = await note(text=original, replyId=parent)
                return
            first, rest = rest[:index+1], rest[index+2:]
        else:
            first, rest = rest[:index], rest[index+2:]
        parent = await note(text=first, replyId=parent)
    parent = await note(text=rest, replyId=parent)


async def mirror(nursery, job, client):
    """Perform the given mirror job."""
    lookback = job.getint('lookback', 1)
    feed = await client.get(job['source'])
    for entry in parse(feed.text)['entries']:
        entry_published = entry.published_parsed if 'published_parse' in entry else entry.updated_parsed
        entry_datetime = datetime(*(entry_published[0:6]))
        if (datetime.now() - entry_datetime) <= timedelta(days=lookback):
            format = job.get('format')
            cw = 'no title'
            body = 'no body'
            if format == 'blog':
                cw = entry['title']
                body = entry['summary']
            elif format == 'misskey':
                if 'summary_detail' in entry:
                    cw = entry['summary']
                else:
                    cw = 'no description'
                body = entry['content']
            elif format == 'mastodon':
                cw = ''
                body = entry['summary']
            else:
                if 'title' in entry:
                    cw = entry['title']
                body = entry['summary']
            nursery.start_soon(post, job, client, entry['link'],
                               cw, body)


async def main():
    """Parse and run jobs."""
    config = ConfigParser()
    config.read(Loca().user.config()/'rsskey'/'jobs.conf')
    async with AsyncExitStack() as stack, open_nursery() as nursery:
        for section in config:
            if section == 'DEFAULT': continue
            job = config[section]
            client = AsyncClient(base_url=job['dest'],
                                 limits=Limits(max_connections=16))
            await stack.enter_async_context(client)
            nursery.start_soon(mirror, nursery, job, client)


if __name__ == '__main__': run(main)
