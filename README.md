# Concept

Each month, a new "Who's Hiring?" thread pops up on Hacker News.
At least in theory, these are a good place to look for tech jobs.
But, the threads quickly accumulate hundreds of comments spanning several pages,
and reviewing them in a web browser is tedious and fragile. You can
collapse threads to keep track of which ones you've dismissed, but if
your browser ever crashes or restarts, or if you click between pages,
you lose that state.
There are some existing tools that ingest the posts in these threads and
make them searchable, but I find they don't really give me the workflow
that I want.

My goal was to be able to _quickly_ flip through all the posts in a thread,
and for each one mark it as rejected (irrelevant tech, bad company, distant
location, etc) or save it for further consideration.

With an emphasis on "quickly": the review tool itself is built using `dearpygui`,
which in turn is built on Dear ImGui, the immediate-mode GUI framework for C++.
The UI is _very_ fast, far faster than 99.9% of web interfaces. Though it is in
theory possible to make a suitably fast web UI using the right techniques, I hate
web UI stuff (can't CSS my way out of a wet paper bag), and I wanted an excuse
to play with `dearpygui`.


## Usage

(Quick caveat: I made this entirely for myself, it definitely works on my machine, so these instructions are a bit half-assed...)

This project uses Poetry, and includes an appropriate `pyproject.toml`. The declared Python version is 3.9
because that's what I used, but 3.7+ ought to work. You will need the SQLite .dll/.so, which is not _always_
included with Python.

First, get scraped

`python scrape.py --url "https://news.ycombinator.com/item?id=28719320" --output-dir foo`

Then extract the data

`python parse.py --input-dir foo --output-file bar.json`

Now get clickin'

`python review.py --json-file bar.json --db-file whatever.db`

Your progress is saved automatically, exit any time. When resuming later, the JSON
file is no longer necessary.

`python review.py --db-file whatever.db`

The db file is a SQLite database with a single table and can be manipulated with
any appropriate tools.


## It's ugly!

Beauty is in the eye of the beholder.


## The _code_ is ugly!

Without a doubt.
