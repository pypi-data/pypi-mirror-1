# -*- coding: utf-8 -*-
"""
    pocoo.pkg.core.forum
    ~~~~~~~~~~~~~~~~~~~~

    Forum Utilities.

    :copyright: 2006 by Armin Ronacher, Benjamin Wiegand.
    :license: GNU GPL, see LICENSE for more details.
"""
from datetime import datetime
from math import ceil

from pocoo import Component
from pocoo.db import meta, DatabaseModel, lazy_column, \
     set_column_value, get_column_value, get_initial_column_value
from pocoo.pkg.core.user import User
from pocoo.pkg.core.db import forums, posts, users, ANONYMOUS_USER_ID
from pocoo.pkg.core.template import Pagination, LazyPagination
from pocoo.pkg.core.textfmt import quote_text, parse, render, parse_and_render
from pocoo.utils.uri import urlencode
from pocoo.utils.iterators import inciter

# for default arguments in Thread
_missing = object()


class PostProcessor(Component):
    """
    Process a posting before it is stored in the database.
    """

    def process_post(self, text, title, reason):
        """
        Process a posting.

        :param text: Text of the posting, possibly changed by
                     another PostProcessor.
        :param title: The subject of the posting
        :param reason: Can be ``'new'`` or ``'edit'``.

        :returns:
            * ``True``: store the posting as-is, or
            * ``False``: refuse to store the posting, or
            * a string: use as the new posting text, or
            * a tuple: (text, title) for the posting
        """
        return True


def apply_post_processors(ctx, text, title, reason):
    """
    Apply all `PostProcessor` components to the posting.

    Return (``text``, ``title``) tuple.
    """
    for comp in ctx.get_components(PostProcessor):
        rv = comp.process_post(text, title, 'new')
        if not rv:
            raise ValueError('creation of posting denied')
        elif isinstance(rv, basestring):
            text = unicode(rv)
        elif isinstance(rv, tuple):
            text = unicode(rv[0])
            title = unicode(rv[1])
    return text, title


def get_forum_index(req):
    """
    Return a list of dicts with forum information so that
    the template can use it.

    If the request object has an identified user object attached
    the returned dict will include status information. (read,
    unread)
    """
    ctx = req.ctx
    f = forums.c
    p = posts.c
    u = users.c
    columns = [f.forum_id, f.description, f.name, f.link, f.post_count,
               f.thread_count]

    categories = []
    def do(con):
        for category in con.execute(meta.select(columns,
                                    f.parent_id == None,
                                    order_by=[meta.asc(f.position)])):
            category = dict(category)
            category['is_external_link'] = bool(category.pop('link'))
            category['url'] = ctx.make_url('forum', category['forum_id'])
            forums = []
            for forum in con.execute(meta.select(columns + [f.last_post_id],
                                     f.parent_id == category['forum_id'],
                                     order_by=[meta.asc(f.position)])):
                forum = dict(forum)
                forum['is_external_link'] = bool(forum.pop('link'))
                forum['url'] = ctx.make_url('forum', forum['forum_id'])
                # get last post
                last_post_id = forum.pop('last_post_id')
                if last_post_id is not None:
                    result = con.execute(meta.select([u.user_id, u.username,
                                                      p.post_id, p.title,
                                                      p.timestamp,
                                                      p.username.label('guestname')],
                        (p.post_id == last_post_id) &
                        (p.post_id != None) &
                        (u.user_id == p.author_id)
                    ))
                    last_post = dict(result.fetchone())
                    username = urlencode(last_post['username'])
                    last_post['author'] = {
                        'user_id':      last_post['user_id'],
                        'registered':   last_post.pop('user_id') > 0,
                        'username':     last_post.pop('guestname') or\
                                        last_post.pop('username'),
                        'url':          ctx.make_url('users', username)
                    }
                    last_post['url'] = ctx.make_url('post', last_post['post_id'])
                else:
                    last_post = None
                forum['last_post'] = last_post
                subforums = []
                for sf in con.execute(meta.select([f.forum_id, f.name, f.link],
                                      f.parent_id == forum['forum_id'],
                                      order_by=[meta.asc(f.position)])):
                    sf = dict(sf)
                    sf['is_external_url'] = bool(sf['forum_id'])
                    sf['url'] = ctx.make_url('forum', sf.pop('forum_id'))
                    subforums.append(sf)
                forum['subforums'] = subforums
                forums.append(forum)
            category['forums'] = forums
            categories.append(category)
    ctx.engine.transaction(do)
    return categories


def get_forum(req, forum_id, page=1):
    """
    Return a list of dicts so that the template can use it.

    Return ``None`` if the forum does not exist.
    """
    ctx = req.ctx
    f = forums.c
    p = posts.c
    u = users.c
    columns = [f.forum_id, f.description, f.name, f.link, f.post_count,
               f.thread_count, f.local_thread_count]
    forum_columns = [f.forum_id, f.name, f.description, f.link,
                     f.post_count, f.thread_count, f.last_post_id]
    sf_columns = [f.forum_id, f.name, f.link]
    thread_columns = [p.post_id, p.title, p.timestamp, u.user_id, u.username,
                      p.post_count, p.view_count, p.username.label('guestname')]
    def do(con):
        category = con.execute(meta.select(columns,
            f.forum_id == forum_id,
        order_by=[meta.asc(f.position)])).fetchone()
        if category is None:
            return
        category = dict(category)
        category['url'] = ctx.make_url('forum', category['forum_id'])
        # wo don't pop link here so that the ForumPage request handler
        # can use the link key for redirecting. That means we don't
        # need a second query. But template designers shouldn't
        # ever access {{ forum.link }}
        category['is_external_url'] = bool(category['link'])
        forums = []
        for forum in con.execute(meta.select(forum_columns,
                f.parent_id == category['forum_id'],
                order_by=[meta.asc(f.position)])):
            forum = dict(forum)
            forum['url'] = ctx.make_url('forum', forum['forum_id'])
            # wo don't pop that here so that the ForumPage request handler
            # can use the link key for redirecting. That means we don't
            # need a second query. But template designers shouldn't
            # ever access {{ forum.link }}
            forum['is_external_link'] = bool(forum.pop('link'))
            subforums = []
            for sf in con.execute(meta.select(sf_columns,
                    f.parent_id == forum['forum_id'],
                    order_by=[meta.asc(f.position)])):
                sf = dict(sf)
                sf['is_external_link'] = bool(sf.pop('link'))
                sf['url'] = ctx.make_url('forum', sf['forum_id'])
                subforums.append(sf)
            forum['subforums'] = subforums
            # get last post
            last_post_id = forum.pop('last_post_id')
            if last_post_id is not None:
                result = con.execute(meta.select([u.user_id, u.username,
                                                  p.post_id, p.title,
                                                  p.username.label('guestname'),
                                                  p.timestamp],
                    (p.post_id == last_post_id) &
                    (p.post_id != None) &
                    (u.user_id == p.author_id)
                ))
                last_post = result.fetchone()
                last_post = dict(last_post)
                username = urlencode(last_post['username'])
                last_post['author'] = {
                    'registered':   last_post['user_id'] > 0,
                    'user_id':      last_post.pop('user_id'),
                    'username':     last_post.pop('guestname') or\
                                    last_post.pop('username'),
                    'url':          ctx.make_url('users', username),
                }
                last_post['url'] = ctx.make_url('post', last_post['post_id'])
            else:
                last_post = None
            forum['last_post'] = last_post
            forums.append(forum)
        category['forums'] = forums

        # pagination
        def get_page_link(number):
            link = 'forum/%d' % forum_id
            if number > 1:
                link += '?page=%d' % number
            return link
        threads_per_page = get_threads_per_page(req)
        page_count = int(ceil(category['local_thread_count'] / (threads_per_page * 1.0)))
        pagination = LazyPagination(req, page, threads_per_page, page_count,
                                    get_page_link)

        threads = []
        for thread in con.execute(meta.select(thread_columns,
                (p.forum_id == category['forum_id']) &
                (p.parent_id == None) &
                (u.user_id == p.author_id),
                order_by=[meta.desc(p.post_id)],
                limit=threads_per_page,
                offset=threads_per_page * (page - 1)
            )):
            thread = dict(thread)
            thread['url'] = ctx.make_url('post', thread['post_id'])
            thread['author'] = {
                'registered':   thread['user_id'] > 0,
                'user_id':      thread.pop('user_id'),
                'username':     thread.pop('guestname') or thread['username'],
                'url':          ctx.make_url('users', urlencode(thread.pop('username')))
            }
            # get last post
            result = con.execute(meta.select([u.user_id, u.username, p.post_id,
                                              p.title, p.timestamp,
                                              p.username.label('guestname')],
                (p.root_post_id == thread['post_id']) &
                (u.user_id == p.author_id),
                order_by=[meta.desc(p.post_id)],
                limit=1
            ))
            last_post = result.fetchone()
            if last_post is not None:
                last_post = dict(last_post)
                username = last_post.pop('username')
                last_post['author'] = {
                    'registered':   last_post['user_id'] > 0,
                    'user_id':      last_post.pop('user_id'),
                    'username':     last_post.pop('guestname') or username,
                    'url':          ctx.make_url('users', urlencode(username)),
                }
                last_post['url'] = ctx.make_url('post', last_post['post_id'])
            thread['last_post'] = last_post
            threads.append(thread)
        category['threads'] = threads
        category['pagination'] = pagination
        return category
    return ctx.engine.transaction(do)


def get_forum_pathbar(ctx, forum_id):
    """Return the pathbar for a given forum."""
    f = forums.c
    pathbar = []
    def do(con, fid=None):
        if fid is None:
            fid = forum_id
        row = con.execute(meta.select([f.parent_id, f.name],
            forums.c.forum_id == fid
        )).fetchone()
        if row is not None:
            l = 'forum/%d' % fid
            pathbar.append({
                'url':      ctx.make_url(l),
                'forum_id': fid,
                'name':     row['name']
            })
            if row['parent_id'] is not None:
                do(con, row['parent_id'])
    ctx.engine.transaction(do)
    pathbar.reverse()
    return pathbar


def get_post_pathbar(ctx, post_id):
    """Returns the pathbar for a given post including all forums and subforums"""
    thread = Thread.by_child(ctx, post_id)
    pathbar = get_forum_pathbar(ctx, thread.forum_id)
    post_list = [ thread.root_post_id ]
    p = posts.c

    if thread.root_post_id != int(post_id):
        post_list.append(post_id)

    def do(con):
        for id in post_list:
            row = con.execute(meta.select([p.title],
                p.post_id == id
            )).fetchone()
            pathbar.append({
                'url': ctx.make_url('post/%s' % id),
                'name': row["title"]
            })
    ctx.engine.transaction(do)
    return pathbar


def get_post_tree(req, post_id, inc_view_count=True):
    """
    Return a dict with the thread information and a tree of posts.

    Per default it will increment the view counter of the
    thread requested. If you don't want that set ``inc_view_count``
    to ``False``.
    """
    ctx = req.ctx
    p = posts.c
    u = users.c
    f = forums.c

    # load the post requested and lookup root_post_id
    result = ctx.engine.execute(meta.select([p.root_post_id, p.post_id, p.title,
                                             p.text, p.parsed_text, p.timestamp,
                                             p.deleted, u.user_id, u.register_date,
                                             u.username, u.profile, u.post_count,
                                             p.username.label('guestname')],
        (p.post_id == post_id) &
        (u.user_id == p.author_id)
    ))
    row = result.fetchone()
    if row is None:
        # XXX: raise error here
        return
    post = dict(row)
    post['url'] = ctx.make_url('post', row['post_id'])
    post['author'] = {
        'user_id':       post['user_id'],
        'username':      post.pop('guestname') or post['username'],
        'self':          req.user.user_id == post['user_id'],
        'registered':    post.pop('user_id') > 0,
        'register_date': post.pop('register_date'),
        'url':           ctx.make_url('users', urlencode(post.pop('username'))),
        'profile':       post.pop('profile'),
        'post_count':    post.pop('post_count'),
    }
    signature = None
    if post['author']['profile'].get('signature'):
        signature = parse_and_render(req, post['author']['profile']['signature'],
                                        signature=True)
    post['author']['signature'] = signature

    # if the post was deleted we remove the text from the return value
    # so that templates don't display them by chance
    if post['deleted']:
        post['text'] = post['parsed_text'] = u''
    else:
        post['parsed_text'] = render(req, post['parsed_text'])
    root_post_id = post.pop('root_post_id')

    result = ctx.engine.execute(meta.select([p.post_id, p.root_post_id, p.title,
                                             p.deleted, p.parent_id, p.timestamp,
                                             u.username, u.user_id,
                                             p.username.label('guestname')],
        (p.root_post_id == root_post_id) &
        (u.user_id == p.author_id)
    ))

    def prepare(row):
        d = dict(row)
        d['author'] = {
            'user_id':          d['user_id'],
            'username':         d.pop('guestname') or d['username'],
            'self':             req.user.user_id == d['user_id'],
            'registered':       d.pop('user_id') > 0,
            'url':              ctx.make_url('users', urlencode(d.pop('username'))),
        }
        d['active'] = d['post_id'] == post_id
        d['url'] = ctx.make_url('post', row['post_id'])
        return d

    # map threads by their parents and prepare the context
    mapping = {}
    flat_posts = []
    for row in result:
        tmp = prepare(row)
        mapping.setdefault(row['parent_id'], []).append(tmp)
        flat_posts.append(tmp)
    root = mapping.pop(None, None)
    if root is None:
        return
    assert len(root) == 1, 'something went seriously wrong'

    # reassamble thread
    def reassamble(nodes):
        for node in nodes:
            node['children'] = n = mapping.pop(node['post_id'], [])
            reassamble(n)
    reassamble(root)

    # increment view_count
    if inc_view_count:
        ctx.engine.execute(posts.update(p.post_id == root_post_id,
            values={'view_count': p.view_count + 1}
        ))

    # fetch overall information for whole thread
    row = ctx.engine.execute(meta.select([p.post_id, p.title, p.forum_id, p.locked,
                                          p.timestamp, u.user_id, u.username,
                                          f.name, p.username.label('guestname')],
        (p.post_id == root_post_id) &
        (u.user_id == p.author_id) &
        (f.forum_id == p.forum_id)
    )).fetchone()
    return {
        'post_id':      row['post_id'],
        'url':          ctx.make_url('post', row['post_id']),
        'title':        row['title'],
        'timestamp':    row['timestamp'],
        'locked':       row['locked'],
        'forum': {
            'forum_id':     row['forum_id'],
            'name':         row['name'],
            'url':          ctx.make_url('forum', row['forum_id']),
        },
        'author': {
            'user_id':     row['user_id'],
            'registered':  row['user_id'] > 0,
            'username':    row['guestname'] or row['username'],
            'url':         ctx.make_url('users', urlencode(row['username'])),
        },
        'posts':        root,
        'post':         post
    }


def get_post(req, post_id):
    """
    Return exactly one post. If the post does not exist the result
    will be ``None``.
    """
    ctx = req.ctx
    p = posts.c
    u = users.c

    row = ctx.engine.execute(meta.select([p.post_id, p.title, p.text, p.deleted,
                                          p.parsed_text, p.timestamp,
                                          u.user_id, u.username, u.profile,
                                          u.register_date, u.post_count,
                                          p.username.label('guestname')],
        (p.post_id == post_id) &
        (u.user_id == p.author_id)
    )).fetchone()
    if row is None:
        return
    post = dict(row)
    post['url'] = ctx.make_url('post', post['post_id'])
    post['author'] = {
        'user_id':       post['user_id'],
        'username':      post.pop('guestname') or post['username'],
        'self':          req.user.user_id == post['user_id'],
        'registered':    post.pop('user_id') > 0,
        'register_date': post.pop('register_date'),
        'url':           ctx.make_url('users', urlencode(post.pop('username'))),
        'profile':       post.pop('profile'),
        'post_count':    post.pop('post_count')
    }
    signature = None
    if post['author']['profile'].get('signature'):
        signature = parse_and_render(req, post['author']['profile']['signature'])
    post['author']['signature'] = signature

    # if the post was deleted we remove the text from the return value
    # so that templates don't display them by chance
    if post['deleted']:
        post['text'] = post['parsed_text'] = u''
    else:
        post['parsed_text'] = render(req, post['parsed_text'])
    return post


def get_last_posts(req, root_post_id, n=1, offset=0):
    """
    Returns a flat view of the n latest posts that are
    children of root_post_id.
    """
    p = posts.c
    u = users.c
    result = req.ctx.engine.execute(meta.select([p.post_id, p.title, p.text, p.deleted,
                                                 p.parsed_text, p.timestamp,
                                                 u.username, u.user_id, u.profile,
                                                 u.post_count, u.register_date,
                                                 p.username.label('guestname')],
                (p.root_post_id == root_post_id) &
                (u.user_id == p.author_id),
                order_by=[meta.desc(p.post_id)],
                limit=n,
                offset=offset
    ))

    def prepare(row):
        d = dict(row)
        user_id = d.pop('user_id')
        d['url'] = req.ctx.make_url('post', row['post_id'])
        d['author'] = {
            'user_id':       user_id,
            'registered':    user_id > 0,
            'username':      d.pop('guestname') or d.pop('username'),
            'self':          req.user.user_id == user_id,
            'profile':       d.pop('profile'),
            'post_count':    d.pop('post_count'),
            'register_date': d.pop('register_date'),
            'url':           req.ctx.make_url('users', urlencode(row['username'])),
        }
        signature = None
        if d['author']['profile'].get('signature'):
            signature = parse_and_render(req, d['author']['profile']['signature'],
                                            signature=True)
        d['author']['signature'] = signature

        # if the post was deleted we remove the text from the return value
        # so that templates don't display them by chance
        if d['deleted']:
            d['text'] = d['parsed_text'] = u''
        else:
            d['parsed_text'] = render(req, d['parsed_text'])
        return d
    return [prepare(row) for row in result]


def get_flat_view(req, post_id, inc_view_count=True, order='asc'):
    """
    Returns the flat view of an post and the next n posts so
    that the template can render a page. n is the number of
    posts per page defined in either the user settings or the
    global forum configuration.

    Per default it will increment the view counter of the
    thread requested. If you don't want that set ``inc_view_count``
    to ``False``.

    If you want to get the latest post first, set ``order``
    to ``'desc'``.
    """
    ctx = req.ctx
    p = posts.c
    f = forums.c
    u = users.c

    # find root_post_id
    result = ctx.engine.execute(meta.select([p.root_post_id],
        p.post_id == post_id
    ))

    # XXX: This raises TypeError on failure.
    root_post_id = result.fetchone()[0]

    # select all post ids to calculate the position of the post on a page
    # the purpose of this calculation is to find the first and last post
    # on the page if the post_id given the function
    result = ctx.engine.execute(meta.select([p.post_id],
        p.root_post_id == root_post_id
    ))
    posts_per_page = get_posts_per_page(req)
    postlist = [row[0] for row in result]
    post_index = postlist.index(post_id)
    page = post_index // posts_per_page
    page_start = page * posts_per_page
    post_range_low = postlist[page_start]
    post_range_high = postlist[page_start:page_start + posts_per_page][-1]

    pagination = Pagination(req, postlist, page_start, posts_per_page,
                            lambda x: 'post/%d' % x)

    orderfunc = (order == 'desc' and meta.desc or meta.asc)

    # select matching posts
    result = ctx.engine.execute(meta.select([p.post_id, p.root_post_id, p.title,
                                             p.forum_id, p.parent_id, p.text,
                                             p.parsed_text, p.timestamp, p.deleted,
                                             u.username, u.user_id, u.profile,
                                             u.post_count, u.register_date,
                                             p.username.label('guestname')],
        (p.root_post_id == root_post_id) &
        (p.post_id >= post_range_low) &
        (p.post_id <= post_range_high) &
        (u.user_id == p.author_id),
        order_by=[orderfunc(p.post_id)]
    ))

    def prepare(number, row):
        d = dict(row)
        user_id = d.pop('user_id')
        d['post_number'] = number
        d['url'] = ctx.make_url('post', row['post_id'])
        d['author'] = {
            'user_id':       user_id,
            'registered':    user_id > 0,
            'username':      d.pop('guestname') or d.pop('username'),
            'self':          req.user.user_id == user_id,
            'profile':       d.pop('profile'),
            'post_count':    d.pop('post_count'),
            'register_date': d.pop('register_date'),
            'url':           ctx.make_url('users', urlencode(row['username'])),
        }
        signature = None
        if d['author']['profile'].get('signature'):
            signature = parse_and_render(req, d['author']['profile']['signature'],
                                            signature=True)
        d['author']['signature'] = signature

        # if the post was deleted we remove the text from the return value
        # so that templates don't display them by chance
        if d['deleted']:
            d['text'] = d['parsed_text'] = u''
        else:
            d['parsed_text'] = render(req, d['parsed_text'])
        return d
    real_posts = [prepare(num, row) for num, row in inciter(result, page_start)]

    # increment view_count
    if inc_view_count:
        ctx.engine.execute(posts.update(p.post_id == root_post_id,
            values={'view_count': p.view_count + 1}
        ))

    # and another query for the overview page
    row = ctx.engine.execute(meta.select([p.post_id, p.title, p.forum_id, p.locked,
                                          p.timestamp, u.user_id, u.username,
                                          f.name, p.username.label('guestname')],
        (p.post_id == root_post_id) &
        (u.user_id == p.author_id) &
        (f.forum_id == p.forum_id)
    )).fetchone()
    return {
        'post_id':      row['post_id'],
        'url':          ctx.make_url('post', row['post_id']),
        'title':        row['title'],
        'timestamp':    row['timestamp'],
        'locked':       row['locked'],
        'forum': {
            'forum_id':     row['forum_id'],
            'name':         row['name'],
            'url':          ctx.make_url('forum', row['forum_id']),
        },
        'author': {
            'user_id':      row['user_id'],
            'username':     row['guestname'] or row['username'],
            'url':          ctx.make_url('users', urlencode(row['username'])),
        },
        'pagination':   pagination,
        'posts':        real_posts
    }


def get_last_thread_change(req, post_id):
    """
    Return the timestamp of the last change in the thread.
    ``post_id`` must be the root_post_id, there is no further
    check done.

    Return ``None`` if something in the query went wrong (eg.
    no thread with the requested root_post_id exists)
    """
    #XXX: doesn't cover edits
    row = req.ctx.engine.execute(meta.select([posts.c.timestamp],
        posts.c.root_post_id == post_id,
        order_by=[meta.desc(posts.c.post_id)],
        limit=1
    )).fetchone()
    if row is None:
        return
    return row[0]


def get_posts_per_page(req):
    """
    Return the number of posts a user wishes to display on the
    flat view page.
    """
    return req.user.settings.get('posts_per_page') or \
           req.ctx.cfg.get_int('board', 'posts_per_page', 15)


def get_threads_per_page(req):
    """
    Return the number of posts a users whishes to display on the
    viewforum page.
    """
    return req.user.settings.get('threads_per_page') or \
           req.ctx.cfg.get_int('board', 'threads_per_page', 20)


def get_view_mode(req):
    """
    Return the display mode a user has defined in the user settings
    or fall back to the default mode from the pocoo.conf.

    :return: either ``'flat'`` or ``'threaded'``.
    """
    val = req.user.settings.get('view_mode')
    if val in ('flat', 'threaded'):
        return val
    val = req.ctx.cfg.get('board', 'default_view', None)
    return (val in ('flat', 'threaded')) and val or 'threaded'


def quote_post(req, post_id):
    """
    Return a tuple in the form ``(text, title)`` which is useful
    for replying and quoting existing posts. The title is
    prefixed with a local representation of 'Re:' and the text
    is quoted with the selected markup.
    """
    p = posts.c
    u = users.c
    _ = req.gettext

    row = req.ctx.engine.execute(meta.select([p.title, p.deleted,
                                              p.text, u.username],
        (p.post_id == post_id) &
        (u.user_id == p.author_id)
    )).fetchone()
    if row is None:
        # XXX: ValueError?
        raise ValueError('post %s does not exist')

    suffix = _('Re:')
    title = row['title']
    if not title.startswith(suffix):
        title = u'%s %s' % (suffix, title)
    if row['deleted']:
        text = u''
    else:
        text = quote_text(req, row['text'], row['username'])
    return text, title


def edit_post(req, post_id):
    """
    Return a tuple in the form (``text``, ``title``, ``username``)
    for the edit view.

    :see: `quote_post`
    """
    p = posts.c
    result = req.ctx.engine.execute(meta.select([p.text, p.title, p.username],
        (p.post_id == post_id)
    ))
    row = result.fetchone()
    if row is None:
        # XXX: ValueError?
        raise ValueError('post %s does not exist')
    return tuple(row)


def do_recount(con, forum_id):
    """
    Recount a forum. This function is for example used by the `Forum` model.
    Pass it an connection object (or engine) and the `forum_id` to trigger
    the recount process. It returns the post and thread count as tuple in
    the form ``(post_count, thread_count, local_thread_count)``.

    This method also updates the ``local_thread_count`` column which is helds
    the number of threads in the current forum excluding subforums. It's
    used for generating the pagination of a forum page.
    """
    affected_forums = [forum_id]
    def find_child_forums(forum_id):
        for row in con.execute(meta.select([forums.c.forum_id],
                               forums.c.parent_id == forum_id)):
            affected_forums.append(row[0])
            find_child_forums(row[0])
    find_child_forums(forum_id)

    post_count = con.execute(meta.select([meta.func.count(posts.c.post_id)],
        posts.c.forum_id.in_(*affected_forums)
    )).fetchone()[0]
    thread_count = con.execute(meta.select([meta.func.count(posts.c.post_id)],
        (posts.c.forum_id.in_(*affected_forums)) &
        (posts.c.root_post_id == posts.c.post_id)
    )).fetchone()[0]
    local_thread_count = con.execute(meta.select([meta.func.count(posts.c.post_id)],
        (posts.c.forum_id == forum_id) &
        (posts.c.root_post_id == posts.c.post_id)
    )).fetchone()[0]
    con.execute(forums.update(forums.c.forum_id == forum_id),
        post_count=post_count,
        thread_count=thread_count,
        local_thread_count=local_thread_count
    )
    return post_count, thread_count, local_thread_count


def sync_last_post_column(con, forum_id):
    """
    Sync the `last_post_id` column for the given forum.
    """
    # find all subforums of this forum, we look for posts
    # there too
    affected_forums = [forum_id]
    def find_child_forums(forum_id):
        for row in con.execute(meta.select([forums.c.forum_id],
                               forums.c.parent_id == forum_id)):
            affected_forums.append(row[0])
            find_child_forums(row[0])
    find_child_forums(forum_id)

    # find the last post
    row = con.execute(meta.select([posts.c.post_id],
        (posts.c.forum_id.in_(*affected_forums)) &
        (posts.c.post_id == posts.c.root_post_id),
        order_by=[meta.desc(posts.c.timestamp)],
        limit=1
    )).fetchone()

    # update the columns
    con.execute(forums.update(forums.c.forum_id == forum_id),
        last_post_id=row and row[0] or None
    )


class Forum(DatabaseModel):
    """
    This class represents one forum. Don't pass instances of this
    class to templates, therefore there are some other functions
    in this module.

    The main purpose of this class is the creation and management
    of forums. You can also use this class for the ACL functions.
    """

    def __init__(self, ctx, forum_id):
        self.ctx = ctx
        self.forum_id = forum_id
        self._old_parent_id = None
        super(Forum, self).__init__(ctx, forums, 'forum_id')

    parent_id = lazy_column('parent_id')
    object_id = lazy_column('object_id')
    name = lazy_column('name')
    description = lazy_column('description')
    position = lazy_column('position')
    link = lazy_column('link')
    last_post_id = lazy_column('last_post_id')
    post_count = lazy_column('post_count')
    thread_count = lazy_column('thread_count')
    local_thread_count = lazy_column('local_thread_count')

    @staticmethod
    def create(ctx, name, description='', parent=None, position=None, link=None):
        """Create a new forum."""
        if isinstance(parent, Forum):
            parent = parent.forum_id
        result = ctx.engine.execute(forums.insert(),
            parent_id=parent,
            name=name,
            description=description,
            position=position,
            link=link,
            post_count=0,
            thread_count=0
        )
        return Forum(ctx, result.last_inserted_ids()[0])

    def delete(self):
        """Deletes a forum with all the subfourms and posts in it."""
        def do(con):
            """
            This method is called by the transaction system of the
            context engine. It deletes a forum with all it's subforums
            and posts stored inside of itself or one of it's subforums.
            """
            parent_forums = set()

            def find_parent_forums(con, forum_id):
                """find all parent forums and add them to the list"""
                row = con.execute(meta.select([forums.c.parent_id],
                                  forums.c.forum_id == forum_id)).fetchone()
                if row and row[0]:
                    parent_forums.add(row[0])
                    find_parent_forums(con, row[0])

            def delete_forum(con, forum_id):
                """look for subforums and delete them"""
                for subforum in con.execute(meta.select([forums.c.forum_id],
                                            forums.c.parent_id == forum_id)):
                    delete_forum(con, subforum.forum_id)
                # delete posts
                con.execute(posts.delete(posts.c.forum_id == forum_id))
                # delete the forum itself
                con.execute(forums.delete(forums.c.forum_id == forum_id))

            find_parent_forums(con, self.forum_id)
            delete_forum(con, self.forum_id)

            # recount all posts and threads in the parent forums
            for forum_id in parent_forums:
                do_recount(con, forum_id)

        self.ctx.engine.transaction(do)

    def save(self, con=None):
        """Updates the post count / thread count of old and new parent
        forums recursively if the parent was changed."""
        def do(con):
            # check if the parent id
            old_parent = get_initial_column_value(self, 'parent_id', con)
            new_parent = self.parent_id
            affected_forums = set([old_parent, new_parent])

            # do plain column updating
            super(Forum, self).save(con)

            def find_parent_forums(forum_id):
                """find all parent forums and add them to the list"""
                for row in con.execute(meta.select([forums.c.forum_id],
                                       forums.c.parent_id == forum_id)):
                    affected_forums.add(row[0])
                    find_parent_forums(row[0])

            # if the parent changed, recount posts and threads
            # in all affected forums (old parent, new parent)
            # and update the last post columns
            if old_parent != new_parent:
                find_parent_forums(new_parent)
                find_parent_forums(old_parent)
                for forum_id in affected_forums:
                    do_recount(con, forum_id)
                    sync_last_post_column(con, forum_id)

        self.ctx.engine.transaction(do)

    def move(self, forum):
        """
        Move a forum to a new parent forum. Or `None` to make it a category
        on the top level. You can also use the `parent` property to do so.
        `value` must be a valid forum, forum_id or `None`.
        """
        if forum is None:
            self.parent_id = None
        elif isinstance(forum, Forum):
            self.parent_id = forum.forum_id
        elif isinstance(forum, (int, long)):
            self.parent_id = forum

    parent = property(lambda s: Forum(s.ctx, s.parent_id), move)

    def __repr__(self):
        return '<%s %d: %r>' % (
            self.__class__.__name__,
            self.forum_id,
            self.name
        )


class Thread(DatabaseModel):
    """
    This class represents a root post with all of its children.
    You can use this class to manage a thread, add a new reply
    or edit one of its children.
    """

    def __init__(self, ctx, root_post_id):
        self.ctx = ctx
        self.post_id = root_post_id
        super(Thread, self).__init__(ctx, posts, 'post_id',
            posts.c.parent_id == None
        )

    forum_id = lazy_column('forum_id')
    parent_id = lazy_column('parent_id')
    root_post_id = lazy_column('root_post_id')
    object_id = lazy_column('object_id')
    author_id = lazy_column('author_id')
    title = lazy_column('title')
    text = lazy_column('text')
    locked = lazy_column('locked')
    timestamp = lazy_column('timestamp')

    @staticmethod
    def create(ctx, forum, author, title, text, timestamp=None):
        """Create a new thread.
        If author is a string it will be an anonymous posting."""
        username = None
        if isinstance(forum, Forum):
            forum = forum.forum_id
        if isinstance(author, User):
            author = author.user_id
        elif isinstance(author, basestring):
            username = author
            author = ANONYMOUS_USER_ID
        if timestamp is None:
            timestamp = datetime.utcnow()

        def do(con):
            """
            This method is used as all in one transaction for creating
            a new thread. This transaction does the following queries:

            -   add new post to the database
            -   increment author post count
            -   lookup all forums that held thread/post count information
            -   update the thread/post count columns of all affected
                forums.
            -   update the root_post_id of the newly created post so
                that it points to itself.
            """
            # insert the new thread into the thread table
            result = con.execute(posts.insert(),
                forum_id=forum,
                author_id=author,
                username=username,
                title=title,
                text=text,
                parsed_text=parse(ctx, text),
                timestamp=timestamp,
                post_count=1,
                view_count=0,
                deleted=False,
                locked=False
            )
            thread_id = result.last_inserted_ids()[-1]

            # increment author post count
            if author > -1:
                con.execute(users.update(users.c.user_id == author,
                    values={'post_count': users.c.post_count + 1}
                ))

            # look up all parent forums and update the `last_post_id`,
            # `thread_count` and `post_count` columns
            affected_forums = [forum]

            def find_parent_forums(forum_id):
                """find all parent forums and add them to the list"""
                row = con.execute(meta.select([forums.c.parent_id],
                                  forums.c.forum_id == forum_id)).fetchone()
                if row and row[0]:
                    affected_forums.append(row[0])
                    find_parent_forums(row[0])
            find_parent_forums(forum)

            # iterate through the list of found forums and update the
            # columns
            for forum_id in affected_forums:
                con.execute(forums.update(forums.c.forum_id == forum_id,
                    values={
                        'post_count':           forums.c.post_count + 1,
                        'thread_count':         forums.c.thread_count + 1,
                        'local_thread_count':   forums.c.local_thread_count + 1
                    }),
                    last_post_id=thread_id
                )

            # now update the root post id
            con.execute(posts.update(posts.c.post_id == thread_id),
                root_post_id=thread_id
            )
            return thread_id

        # start the query and return a new thread object for the
        # requested data.
        return Thread(ctx, ctx.engine.transaction(do))

    @staticmethod
    def by_child(ctx, post_id):
        """
        Return the thread of a given `post_id`.
        """
        result = ctx.engine.execute(meta.select([posts.c.root_post_id],
            (posts.c.post_id == post_id)
        ))
        row = result.fetchone()
        if row is None:
            # XXX: ValueError?
            raise ValueError('post %s does not exist' % post_id)
        return Thread(ctx, row[0])

    def lock(self):
        """Lock the thread."""
        self.locked = True

    def unlock(self):
        """Unlock the thread."""
        self.locked = False

    def save(self, con=None):
        """Update the post count / thread count if the thread was moved."""

        def do(con):
            # get initial data
            old_forum = get_initial_column_value(self, 'forum_id', con)
            new_forum = self.forum_id
            old_text = get_initial_column_value(self, 'text', con)
            new_text = self.text
            affected_forums = set([old_forum, new_forum])

            # reparse text if wanted
            if old_text != new_text:
                parsed_text = parse(self.ctx, new_text)
                set_column_value(self, 'parsed_text', parsed_text)

            # do plain column updateing
            super(Thread, self).save(con)

            def find_parent_forums(forum_id):
                """find all parent forums and add them to the list"""
                row = con.execute(meta.select([forums.c.parent_id],
                                  forums.c.forum_id == forum_id)).fetchone()
                if row and row[0]:
                    affected_forums.add(row[0])
                    find_parent_forums(row[0])

            # if something changed, find the affected forums
            # and update columns
            if old_forum != self.forum_id:
                find_parent_forums(new_forum)
                find_parent_forums(old_forum)
                for forum_id in affected_forums:
                    do_recount(con, forum_id)
                    sync_last_post_column(con, forum_id)

        self.ctx.engine.transaction(do)

    def delete(self):
        """
        Delete a thread with all of it's subposts.
        """
        def do(con):
            # lookup all forums this thread is a member of
            affected_forums = set([self.forum_id])

            def find_parent_forums(forum_id):
                """find all parent forums and add them to the list"""
                row = con.execute(meta.select([forums.c.parent_id],
                                  forums.c.forum_id == forum_id)).fetchone()
                if row and row[0]:
                    affected_forums.add(row[0])
                    find_parent_forums(row[0])

            find_parent_forums(self.forum_id)

            # delete thread with all posts
            con.execute(posts.delete(
                (posts.c.post_id == self.post_id) |
                (posts.c.root_post_id == self.post_id)
            ))

            # recount all affected forums
            for forum_id in affected_forums:
                do_recount(con, forum_id)
                sync_last_post_column(con, forum_id)
        self.ctx.engine.transaction(do)

    def reply(self, post_id, author, title, text, timestamp=None,
              no_processor=False):
        """
        Reply to post `post_id` which is a child of the thread.
        Return the id of the new post.

        If `author` is a string it will be an anonymous posting.
        """
        username = None
        if post_id is None:
            post_id = self.post_id
        if isinstance(author, User):
            author = author.user_id
        elif isinstance(author, basestring):
            username = author
            author = ANONYMOUS_USER_ID
        if timestamp is None:
            timestamp = datetime.utcnow()
        if not no_processor:
            text, title = apply_post_processors(self.ctx, text,
                                                title, 'new')

        def do(con):
            result = con.execute(meta.select([posts.c.root_post_id],
                posts.c.post_id == post_id
            ))
            row = result.fetchone()
            if row is None or row[0] != int(self.post_id):
                # XXX: ValueError?
                raise ValueError('The post either does not exist or does not '
                                 'belong to this thread')
            new_post_id = con.execute(posts.insert(),
                forum_id=self.forum_id,
                parent_id=post_id,
                root_post_id=self.post_id,
                author_id=author,
                username=username,
                title=title,
                text=text,
                deleted=False,
                locked=False,
                parsed_text=parse(self.ctx, text),
                timestamp = timestamp
            ).last_inserted_ids()[0]

            # increment author post count
            if author > -1:
                con.execute(users.update(users.c.user_id == author,
                    values={'post_count': users.c.post_count + 1}
                ))

            # increment forum post count and update last_post_id
            con.execute(forums.update(forums.c.forum_id == self.forum_id,
                values={'post_count': forums.c.post_count + 1}),
                last_post_id=new_post_id
            )

            # increment thread post count
            con.execute(posts.update(posts.c.post_id == self.post_id,
                values={'post_count': posts.c.post_count + 1}
            ))
            return new_post_id
        return self.ctx.engine.transaction(do)

    def edit_reply(self, post_id, author=_missing, title=_missing,
                   text=_missing, timestamp=_missing,
                   no_processor=False):
        """Edit a reply."""
        d = {}
        if author is not _missing:
            if isinstance(author, User):
                d['author_id'] = author.user_id   # pylint: disable-msg=E1101
            else:
                d['author_id'] = author
        if title is not _missing:
            d['title'] = title
        if text is not _missing:
            d['text'] = text
            d['parsed_text'] = parse(self.ctx, text)
        if timestamp is not _missing:
            d['timestamp'] = timestamp
        if not no_processor and 'title' in d and 'text' in d:
            rv = apply_post_processors(self.ctx, d['text'], d['title'], 'edit')
            d['text'], d['title'] = rv
        self.ctx.engine.execute(posts.update(posts.c.post_id == post_id), **d)

    def delete_reply(self, post_id):
        """Mark a reply as deleted."""
        self.ctx.engine.execute(posts.update(posts.c.post_id == post_id),
            deleted = True
        )

    def has_child(self, post_id):
        """Check if a post_id is a child of this thread."""
        result = self.ctx.engine.execute(meta.select([posts.c.root_post_id],
            posts.c.post_id == post_id
        ))
        row = result.fetchone()
        return row is not None and row['root_post_id'] == self.post_id

    def get_post_list(self):
        """
        Return a flat list of all posts in this thread sorted by their post_id.
        """
        result = self.ctx.engine.execute(posts.select(
            posts.c.root_post_id == self.post_id
        ))
        return map(dict, result)

    def count_children(self):
        """
        Return the number of direct or indirect children of this thread.
        """
        p = posts.c
        result = self.ctx.engine.execute(meta.select([meta.func.count(p.post_id)],
            p.root_post_id == self.post_id
        ))
        return result.fetchone()[0]

    __len__ = count_children

    def forum_get(self):
        if self.forum_id is not None:
            return Forum(self.ctx, self.forum_id)
    def forum_set(self, value):
        if not isinstance(value, Forum):
            raise TypeError('Can only set Forum instances')
        self.forum_id = value.forum_id
    forum = property(forum_get, forum_set)
    del forum_get, forum_set

    def __eq__(self, other):
        return self.post_id == other.post_id

    def __ne__(self, other):
        return not self.__eq__(other)

    def __repr__(self):
        return '<%s %d: %r>' % (
            self.__class__.__name__,
            self.post_id,
            self.title
        )
