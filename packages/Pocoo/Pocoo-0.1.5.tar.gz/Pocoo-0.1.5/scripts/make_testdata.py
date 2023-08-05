#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    make_testdata
    ~~~~~~~~~~~~~

    Fill the database in instance/ with test data.

    :copyright: 2006 by Georg Brandl.
    :license: GNU GPL, see LICENSE for more details.
"""

leadins = """To characterize a linguistic level L,
    On the other hand,
    This suggests that
    It appears that
    Furthermore,
    We will bring evidence in favor of the following thesis:
    To provide a constituent structure for T(Z,K),
    From C1, it follows that
    For any transformation which is diversified in application to be of any interest,
    Analogously,
    Clearly,
    Note that
    Of course,
    Suppose, for instance, that
    Thus
    With this clarification,
    Conversely,
    We have already seen that
    By combining adjunctions and certain deformations,
    I suggested that these results would follow from the assumption that
    If the position of the trace in (99c) were only relatively inaccessible to movement,
    However, this assumption is not correct, since
    Comparing these examples with their parasitic gap counterparts, we see that
    In the discussion of resumptive pronouns following (81),
    So far,
    Nevertheless,
    For one thing,
    Summarizing, then, we assume that
    A consequence of the approach just outlined is that
    Presumably,
    On our assumptions,
    It may be, then, that
    It must be emphasized, once again, that
    Let us continue to suppose that
    Notice, incidentally, that """

subjects = """ the notion of level of grammaticalness
    a case of semigrammaticalness of a different sort
    most of the methodological work in modern linguistics
    a subset of English sentences interesting on quite independent grounds
    the natural general principle that will subsume this case
    an important property of these three types of EC
    any associated supporting element
    the appearance of parasitic gaps in domains relatively inaccessible to extraction
    the speaker-hearer's linguistic intuition
    the descriptive power of the base component
    the earlier discussion of deviance
    this analysis of a formative as a pair of sets of features
    this selectionally introduced ctxual feature
    a descriptively adequate grammar
    the fundamental error of regarding functional notions as categorial
    relational information
    the systematic use of complex symbols
    the theory of syntactic features developed earlier"""

verbs = """can be defined in such a way as to impose
    delimits
    suffices to account for
    cannot be arbitrary in
    is not subject to
    does not readily tolerate
    raises serious doubts about
    is not quite equivalent to
    does not affect the structure of
    may remedy and, at the same time, eliminate
    is not to be considered in determining
    is to be regarded as
    is unspecified with respect to
    is, apparently, determined by
    is necessary to impose an interpretation on
    appears to correlate rather closely with
    is rather different from"""

objects = """ problems of phonemic and morphological analysis.
    a corpus of tokens upon which conformity has been defined by the utterance test.
    the traditional practice of grammarians.
    the levels of acceptability from fairly high (e.g. (99a)) to virtual gibberish.
    a stipulation to place the constructions into these various categories.
    a descriptive fact of scriptless alertness: <script>alert("Gotcha");</script>.
    a parasitic gap construction.
    the extended c-command discussed in connection with (34).
    the ultimate standard that determines the accuracy of any proposed grammar.
    the system of base rules exclusive of the lexicon.
    irrelevant intervening ctxs in selectional rules.
    nondistinctness in the sense of distinctive feature theory.
    a general convention regarding the forms of the grammar.
    an abstract underlying order of <blink>blinking quarks</blink>.
    an important distinction in language use.
    the requirement that branching is tolerated within the dominance scope of a symbol.
    the strong generative capacity of the theory."""

import random
import sys, os, math
from datetime import datetime, timedelta
from os.path import abspath, dirname, join
from itertools import chain, islice, izip

# Utility functions

def chomsky(times=1, line_length=72):
    parts = []
    for part in (leadins, subjects, verbs, objects):
        phraselist = map(str.strip, part.splitlines())
        random.shuffle(phraselist)
        parts.append(phraselist)
        if random.randint(0, 3) == 0:
            parts.append("\n\n")
    output = chain(*islice(izip(*parts), 0, times))
    return ' '.join(output)


def visibleprogress(list, interval):
    max = len(list)
    msw = len(str(max))
    ttw = 2*len(str(max)) + 4
    sys.stdout.write(" "*ttw)
    for i, item in enumerate(list):
        if (i+1) % interval == 0:
            sys.stdout.write("\b"*ttw + "%*d/%*d..." % (msw, i+1, msw, max))
            sys.stdout.flush()
        yield item
    print


last_time = datetime(2002, 1, 1)
def get_time():
    global last_time
    last_time += timedelta(seconds=random.randrange(10, 4000))
    return last_time

last_forum_position = -10
def get_forum_position():
    global last_forum_position
    last_forum_position += 10
    return last_forum_position


usernames = """xorBxBx whitebird eichenfeld ModelEight
Bad-Barty zehjot ThomasWiesenmann lumatic xRiver BeeWee
<script>alert("XSS");</script>""".split()

from pocoo.context import ApplicationContext

root = os.environ.get('POCOO_ROOT', '')
if not root:
    root = join(dirname(__file__), '..', 'instance')
ctx = ApplicationContext(abspath(root), is_cgi=True)

# don't echo all insertions
ctx.cfg.set('database', 'debug', False)

# create the tables if they don't exist
ctx.create_tables()

print "Created tables."

from pocoo.db import meta
from pocoo.pkg.core.db import forums, posts, users, EVERYBODY_GROUP_ID, \
     REGISTERED_GROUP_ID
from pocoo.pkg.core.user import Group
from pocoo.pkg.core.forum import do_recount
from pocoo.pkg.core.textfmt import parse

groups = [Group(ctx, EVERYBODY_GROUP_ID), Group(ctx, REGISTERED_GROUP_ID)]

try:
    number = int(sys.argv[1])
except:
    number = 8
maxwid = len(str(number))

sys.stdout.write("Creating users...\n")

user_list = []
forum_list = []
thread_list = []

for un in usernames:
    u = ctx.engine.execute(users.insert(),
        username=un,
        pwhash=u'',
        register_date=None,
        email="%s@pocoo.org" % un).last_inserted_ids()[-1]
    user_list.append(u)

sys.stdout.write("Adding users to default groups...\n")
for group in groups:
    for user in user_list:
        group.add_member(user)
    group.save()

print "Creating forum ",

pf = None

def create_post(conn, pid, fid, root_id, depth, num):
    if not root_id:
        title = "Forum %s, Thread %s" % (fid, num)
    else:
        title = "Subpost %s in depth %s" % (num, depth)
    text_len = random.randint(0, 10) or 40
    text = chomsky(text_len)
    p = conn.execute(posts.insert(),
        title=title,
        text=chomsky(text_len),
        parsed_text=parse(ctx, text),
        parent_id=pid,
        forum_id=fid,
        timestamp=get_time(),
        deleted=False,
        locked=False,
        author_id=random.choice(user_list),
        root_post_id = root_id).last_inserted_ids()[-1]
    # i hate that but we need it
    if pid is None:
        thread_list.append(p)
        conn.execute(posts.update(posts.c.post_id == p),
            root_post_id = p
        )

    # create posts in the same depth
    if num == 0 and depth < random.randint(0, 6) and root_id:
        for z in range(random.randint(0, 6)):
            create_post(conn, p, fid, root_id, depth, z)

    # create deeper post
    if depth < random.randint(0, 4):
        create_post(conn, p, fid, root_id or p, depth + 1, 0)

for i in visibleprogress(range(number), 1):
    def do(conn):
        global pf
        if not pf or random.randint(0, 5) == 5:
            # make a category
            f = conn.execute(forums.insert(),
                name="Category %s"%i,
                description=chomsky(1),
                position=get_forum_position(),
                parent_id = None).last_inserted_ids()[-1]
            pf = f
            forum_list.append(f)
        else:
            f = conn.execute(forums.insert(),
                name="Forum %s"%i,
                description=chomsky(1),
                position=get_forum_position(),
                parent_id = pf).last_inserted_ids()[-1]
            forum_list.append(f)

        for j in range(i):
            create_post(conn, None, f, None, 0, j)
    ctx.engine.transaction(do)

print 'Updating User post_count and timestamps ',
for uid in visibleprogress(user_list, 1):
    def do(conn):
        r = conn.execute(meta.select([meta.func.count(posts.c.post_id)],
            posts.c.author_id == uid))
        conn.execute(users.update(users.c.user_id == uid),
            post_count = r.fetchone()[0],
            register_date = get_time()
        )
    ctx.engine.transaction(do)

print 'Update last_post_id column for all forums and count threads/posts ',
for fid in visibleprogress(forum_list, 1):
    def do(conn):
        row = conn.execute(meta.select([posts.c.post_id, posts.c.root_post_id],
            posts.c.forum_id == fid,
            order_by=[meta.desc(posts.c.post_id)],
            limit=1
        )).fetchone()
        last_post_id = None
        if row:
            last_post_id = row[0]
        else:
            last_post_id = None
        conn.execute(forums.update(forums.c.forum_id == fid),
            last_post_id = last_post_id
        )
        do_recount(conn, fid)
    ctx.engine.transaction(do)

print 'Update post_count for all threads ',
for tid in visibleprogress(thread_list, 10):
    def do(conn):
        row = conn.execute(meta.select([meta.func.count(posts.c.post_id)],
            posts.c.root_post_id == tid
        )).fetchone()
        if row is not None:
            post_count = row[0]
        else:
            post_count = 1
        conn.execute(posts.update(posts.c.post_id == tid),
            post_count = post_count,
            view_count = 0
        )
    ctx.engine.transaction(do)

print "\nCreated %s forums with threads and posts." % number
