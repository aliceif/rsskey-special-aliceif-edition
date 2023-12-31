# rsskey special aliceif edition

# changes from mainline rsskey
- venv gitignored
- fix missing token pass
- configuration for visibility
- configuration for how far to go back when fetching new posts (if unlimited (as was originally) adding a new feed will spam you!)
- handling of misskey and mastodon rss feed formats (e.g. you want to take a user on misskey or a hashtag on mastodon and republish their posts)

# rsskey

rsskey is a simple script for mirroring [RSS] or [Atom] feeds on [Misskey].
It splits original posts into paragraphs or sentences to fit an instance's
character limit and checks for previous notes before creating.

## Installation

rsskey depends on [feedparser], [httpx], [loca], [markdownify] and [trio].
Install the dependencies, then execute `src/rsskey.py`.

## Usage

In rsskey's [user configuration directory][loca],
declare the mirroring jobs in `jobs.conf`, for example:

```ini
[rms@birb.space]
; Format of the rss feed
; - blog: ordinary blogs - should usually work.
; - misskey: misskey profile feed - has special parsing to preserve the CW field.
; - mastodon: mastodon rss feed - has special parsing for format idiosyncrasies.
format = blog
; Numbers of days to look back when querying for new posts - default is 1 day.
lookback = 14
; URL to RSS/Atom feed source
source = https://stallman.org/rss/rss.xml
; URL to destination Misskey instance's API
dest = https://birb.space/api
; Note character limit of the Misskey instance - usually 3000 but you may want to keep it low for various reasons.
text = 420
; Content warning character limit of the Misskey instance
cw = 69
; Visibility
; - home (everyone who visits the profile but only sent to followers)
; - followers (only followers will see)
visibility = home
; Misskey user ID for searching previous notes
user = 8rt4sahf1j
; Access token with permission to compose notes
token = 7h4753cur3r4nd0m57r1n61764v3y0u
```

In order to run rsskey chronically, set up a systemd timer or something.

## Contributing

This is a private fork for my own usage of the original project at [original-repo-url]. I have no desire to maintain this for anyone else, but I am curious about any ways this project may get extended.

## Copying

![AGPLv3](https://www.gnu.org/graphics/agplv3-155x51.png)

rsskey is free software: you can redistribute it and/or modify it
under the terms of the GNU [Affero General Public License][agplv3] as
published by the Free Software Foundation, either version 3 of the License,
or (at your option) any later version.

[RSS]: https://www.rssboard.org/rss-specification
[Atom]: https://tools.ietf.org/html/rfc5023
[Misskey]: https://join.misskey.page
[feedparser]: https://feedparser.readthedocs.io
[httpx]: https://www.python-httpx.org
[loca]: https://pypi.org/project/loca
[markdownify]: https://pypi.org/project/markdownify
[trio]: https://trio.readthedocs.io
[~cnx/misc@lists.sr.ht]: https://lists.sr.ht/~cnx/misc
[git send-email]: https://git-send-email.io
[agplv3]: https://www.gnu.org/licenses/agpl-3.0.html
[original-repo-url]: https://sr.ht/~cnx/rsskey/
