# -*- coding: utf-8 -*-
"""
    pocoo.pkg.core.pages
    ~~~~~~~~~~~~~~~~~~~~

    Pocoo core pages.

    :copyright: 2006 by Armin Ronacher, Benjamin Wiegand.
    :license: GNU GPL, see LICENSE for more details.
"""

from pocoo.http import Response, HttpRedirect, TemplateResponse, \
     AccessDeniedResponse, PageNotFound
from pocoo.settings import cfg
from pocoo.template import PagePublisher, render_template
from pocoo.application import RequestHandler

from pocoo.utils.mail import Email
from pocoo.utils.net import make_url_context_external
from pocoo.utils.form import Form, TextField, TextArea, SelectBox
from pocoo.utils.validators import isNotEmpty, isSameValue, isEmail, \
     checkTextLength, isOneLetter, mayEmpty
from pocoo.utils.json import parse_datetime

from pocoo.pkg.core.remotecall import RemoteCallable, export
from pocoo.pkg.core.validators import isAvailableUsername, isStrongPassword, \
     isExistingUsername, isAnonymousUsername
from pocoo.pkg.core.usersettings import UserSettingsPage
from pocoo.pkg.core.db import users
from pocoo.pkg.core.forum import get_forum_index, get_forum, get_post_tree, \
     get_forum_pathbar, get_view_mode, get_flat_view, quote_post, edit_post, \
     get_post, Thread, get_last_posts, get_last_thread_change, get_post_pathbar
from pocoo.pkg.core.user import User, get_user_list, \
     get_user, get_user_avatar, reset_password
from pocoo.pkg.core.session import get_active_sessions
from pocoo.pkg.core.textfmt import parse_and_translate, get_editor

_ = lambda x: x


class IndexPage(RequestHandler, PagePublisher, RemoteCallable):
    page_name = 'index'
    relative_url = ''
    handler_regexes = [u'$']

    def handle_request(self, req):
        return TemplateResponse('index.html',
            categories=get_forum_index(req),
            feed_url=self.ctx.make_url('feeds/recent.xml')
        )


class ForumPage(RequestHandler):
    handler_regexes = [r'forum/(?P<forum_id>\d+)$']

    def handle_request(self, req, forum_id):
        forum_id = int(forum_id)
        try:
            page = int(req.args.get('page'))
        except (TypeError, ValueError):
            page = 1
        forum = get_forum(req, forum_id, page)
        if forum is None:
            return PageNotFound()
        # Redirect if the forum is a link
        if forum['is_external_url']:
            return HttpRedirect(forum['link'], local=False)
        return TemplateResponse('viewforum.html',
            forum=forum,
            pathbar=get_forum_pathbar(self.ctx, forum_id),
            feed_url=self.ctx.make_url('feeds/forum/%d.xml' % forum_id)
        )


class PostPage(RequestHandler, RemoteCallable):
    handler_regexes = [r'post/(?P<post_id>\d+)$']

    def handle_request(self, req, post_id):
        view = get_view_mode(req)
        if view == 'flat':
            return self._flat_view(req, int(post_id))
        else:
            return self._threaded_view(req, int(post_id))

    def _flat_view(self, req, post_id):
        topic = get_flat_view(req, post_id)
        if topic is None:
            return PageNotFound()
        return TemplateResponse('viewtopic.html',
            topic=topic,
            pathbar=get_post_pathbar(self.ctx, topic['posts'][0]['post_id']),
            feed_url=self.ctx.make_url('feeds/thread/%d.xml' % post_id)
        )

    def _threaded_view(self, req, post_id):
        thread = get_post_tree(req, post_id)
        if thread is None:
            return PageNotFound()
        return TemplateResponse('viewthread.html',
            thread=thread,
            pathbar=get_post_pathbar(self.ctx, thread['posts'][0]['post_id']),
            feed_url=self.ctx.make_url('feeds/thread/%d.xml' % post_id)
        )

    @export('thread.get_post')
    def _get_post(self, req, post_id):
        post = get_post(req, post_id)
        if post is None:
            return
        return render_template(req, 'partial/post.html', {
            'post':     post
        })

    @export('thread.tree_requires_update')
    def _tree_requires_update(self, req, post_id, last_update):
        last_update = parse_datetime(last_update)
        last_thread_change = get_last_thread_change(req, post_id)
        print last_thread_change, last_update
        return last_thread_change is not None and\
               last_thread_change > last_update

    @export('thread.get_tree')
    def _get_tree(self, req, post_id):
        return render_template(req, 'partial/tree.html', {
            'posts':    get_post_tree(req, post_id)['posts']
        })


class LoginPage(RequestHandler, PagePublisher):
    page_name = 'login'
    relative_url = 'login'
    handler_regexes = ['^login$']

    def handle_request(self, req):
        next = req.values.get('next', None)
        if next is None:
            next = req.environ.get('HTTP_REFERER')
        if not next:
            next = u''
        _ = req.gettext
        msg = u''
        if req.user.identified:
            return HttpRedirect(next)
        form = Form(req, self, 'POST',
            TextField('username', validator=isNotEmpty()),
            TextField('password', validator=isNotEmpty())
        )
        if req.method == 'POST':
            form.update(req.form, prefix='f_')
            if not form.has_errors:
                d = form.to_dict()
                login = req.auth.do_login(d['username'], d['password'])
                if login:
                    if isinstance(login, Response):
                        return login
                    return TemplateResponse('messages/login.html',
                        username=d['username'],
                        next=next
                    )
                else:
                    msg = _('Login failed. You may have entered an invalid '
                            'username or password or your account is not '
                            'activated yet.')
        return TemplateResponse('login.html',
            msg=msg,
            form=form.generate(prefix='f_'),
            next=next
        )


class LogoutPage(RequestHandler, PagePublisher):
    page_name = 'logout'
    relative_url = 'logout'
    handler_regexes = [r'logout$']

    def handle_request(self, req):
        back = req.environ.get('HTTP_REFERER', u'')
        try:
            back = make_url_context_external(self.ctx, back)
        except ValueError:
            back = None
        username = req.user.username
        req.auth.do_logout()
        return TemplateResponse('messages/logout.html',
            username=username,
            back=back
        )


class RegisterPage(RequestHandler, PagePublisher):
    page_name = 'register'
    relative_url = 'register'
    handler_regexes = ['register$']

    def handle_request(self, req):
        if req.user.identified:
            return HttpRedirect('')
        if 'activate' in req.args and 'user' in req.args:
            return self.activation(req)
        _ = req.gettext
        form = Form(req, self, 'POST',
            TextField('username', validator=isAvailableUsername()),
            TextField('password', validator=isStrongPassword()),
            TextField('password2', validator=isSameValue('password',
                      _('The passwords don\'t match.'))),
            TextField('email', validator=isEmail())
        )
        if req.method == 'POST':
            form.update(req.form, prefix='f_')
            if not form.has_errors:
                d = form.to_dict()
                requires_activation = req.ctx.cfg.get_bool('board', 'email_verification')
                user = User.create(req.ctx,
                    d['username'],
                    d['password'],
                    d['email'],
                    requires_activation
                )
                if requires_activation:
                    link = self.ctx.make_external_url('register?user=%s&key%s' %
                                                      (user.user_id, user.act_key))
                    txt = render_template(req, 'mails/welcome_verification.txt', {
                        'username':       d['username'],
                        'password':       d['password'],
                        'forum_name':     req.ctx.cfg.get('board', 'title'),
                        'activate_link':  link
                    })
                    mail = Email(req.ctx, _('Welcome to the %s') %
                                 req.ctx.cfg.get('board', 'title'),
                                 d['email'], txt)
                    mail.send()
                return TemplateResponse('messages/register.html',
                    requires_activation=requires_activation,
                    username=d['username'],
                    email=d['email']
                )
        return TemplateResponse('register.html',
            form=form.generate(prefix='f_')
        )

    def activation(self, req):
        _ = req.gettext
        uid = int(req.args['user'])
        activated = False
        username = u''
        try:
            user = User(req.ctx, uid)
            key = user.act_key
        except KeyError:
            pass
        else:
            if not user.active and req.args['activate'] == key:
                user.activate()
                activated = True
                username = user.username
        return TemplateResponse('messages/activation.html',
            username=username,
            activated=activated
        )


class NewPostPage(RequestHandler, RemoteCallable):
    handler_regexes = [
        (r'post/(?P<post_id>\d+)/reply$',
         {'action':'reply'}),
        (r'post/(?P<post_id>\d+)/quote$',
         {'action':'quote'}),
        (r'post/(?P<post_id>\d+)/edit$',
         {'action':'edit'})
    ]

    def handle_request(self, req, action, post_id):
        try:
            thread = Thread.by_child(self.ctx, post_id)
        except ValueError:
            return PageNotFound()
        _ = req.gettext

        # note: quote_post can raise a ValueError when a post does
        # not exist. but since we check for that by calling
        # Thread.by_child this shouldn't happen.
        username = _('anonymous')
        if action == 'reply':
            mode = 'reply'
            if not req.user.acl.can_access('REPLY_POST', thread):
                return AccessDeniedResponse()
            text = u''
            _, title = quote_post(req, post_id)
        elif action == 'quote':
            mode = 'reply'
            #XXX: maybe we could use REPLY_POST here too
            if not req.user.acl.can_access('QUOTE_POST', thread):
                return AccessDeniedResponse()
            text, title = quote_post(req, post_id)
        else:
            mode = 'edit'
            if not req.user.acl.can_access('EDIT_POST', thread):
                return AccessDeniedResponse()
            text, title, username = edit_post(req, post_id)

        form = Form(req, req.environ['APPLICATION_REQUEST'], 'POST',
            TextField('username', validator=isAnonymousUsername(),
                      default=username),
            TextField('title', validator=checkTextLength(3, 60),
                      default=title),
            TextArea('text', validator=checkTextLength(3, 10000),
                     default=text)
        )
        if req.method == 'POST':
            form.update(req.form, prefix='f_')
            if not form.has_errors:
                d = form.to_dict()
                if req.user.identified:
                    author = req.user.user_id
                else:
                    author = d['username']
                if action in ('quote', 'reply'):
                    new_post_id = thread.reply(
                        post_id = int(post_id),
                        author = author,
                        title = d['title'],
                        text = d['text']
                    )
                elif action == 'edit':
                    new_post_id = int(post_id)
                    thread.edit_reply(
                        post_id = new_post_id,
                        author = author,
                        title = d['title'],
                        text = d['text']
                    )
                return TemplateResponse('messages/post.html',
                    mode = mode,
                    post = {
                        'id':     new_post_id,
                        'title':  d['title'],
                        'url':    self.ctx.make_url('post', new_post_id),
                    }
                )
        js, options = get_editor(req)
        return TemplateResponse('newpost.html',
            mode = mode,
            form = form.generate(prefix='f_'),
            show_username_entry = not req.user.identified,
            editor_options = options,
            editor_javascript = js,
            post_id = thread.root_post_id,
            pathbar=get_post_pathbar(req.ctx, post_id)
        )

    @export("newpost.preview")
    def preview(self, req, text):
        return parse_and_translate(req, text)

    @export("newpost.get_latest_posts")
    def get_latest_posts(self, req, root_post_id):
        post_list = get_last_posts(req, root_post_id, 15)
        return {
            'html': render_template(req, 'latestposts.html', {'posts': post_list}),
            'last_post': post_list[0]["post_id"]
        }

    @export("newpost.check_new_posts")
    def check_new_posts(self, req, root_post_id, latest_post):
        post = get_last_posts(req, root_post_id, 1)[0]
        if latest_post != post["post_id"]:
            post_list = []
            z = 1
            while post["post_id"] != latest_post:
                post_list.append(post)
                post = get_last_posts(req, root_post_id, 1, z)[0]
                z += 1
            return {
                'html': render_template(req, 'latestposts.html', {'posts': post_list}),
                'last_post': post_list[0]["post_id"]
            }
        else:
            return False


class NewThreadPage(RequestHandler):
    handler_regexes = [r'forum/(?P<forum_id>\d+)/new$']

    def handle_request(self, req, forum_id):
        # TODO: Check whether user is allowed to do this
        _ = req.gettext
        forum_id = int(forum_id)
        form = Form(req, req.environ['APPLICATION_REQUEST'], 'POST',
            TextField('username', validator=isAnonymousUsername(),
                      default=_('anonymous')),
            TextField('title', validator=checkTextLength(3, 60)),
            TextArea('text', validator=checkTextLength(3, 10000))
        )
        if req.method == 'POST':
            form.update(req.form, prefix='f_')
            if not form.has_errors:
                d = form.to_dict()
                if req.user.identified:
                    author = req.user.user_id
                else:
                    author = d['username']
                thread = Thread.create(req.ctx, forum_id, author,
                                       d['title'], d['text'])
                return TemplateResponse('messages/thread.html',
                    thread = {
                        'title': thread.title,
                        'url':   req.ctx.make_url('post', thread.root_post_id),
                    }
                )

        js, options = get_editor(req)
        return TemplateResponse('newthread.html',
            form = form.generate(prefix='f_'),
            show_username_entry = not req.user.identified,
            editor_options = options,
            editor_javascript = js,
            pathbar = get_forum_pathbar(self.ctx, forum_id)
        )


class MemberListPage(RequestHandler, PagePublisher):
    page_name = 'memberlist'
    relative_url = 'users/'
    handler_regexes = [r'users/$']

    def handle_request(self, req):
        _ = req.gettext
        generate = False

        form = Form(req, self, 'GET',
            TextField('letter', validator=mayEmpty(isOneLetter())),
            SelectBox('order_by', [
                ('user_id',         _('User ID')),
                ('username',        _('Username')),
                ('register_date',   _('Register date')),
                ('post_count',      _('Number of Posts'))
            ], default='user_id'),
            SelectBox('direction', [
                ('desc',        _('Descending')),
                ('asc',         _('Ascending'))
            ], default='asc')
        )

        if 'letter' in req.args or 'order_by' in req.args \
           or 'direction' in req.args:
            form.update(req.args)
            if not form.has_errors:
                generate = True
        else:
            generate = True
        if generate:
            d = form.to_dict()
            userlist = get_user_list(self.ctx,
                order_by=getattr(users.c, d['order_by']),
                order=d['direction'],
                letter=d['letter'] or None,
                hide_internal=True
            )
        else:
            userlist = []

        return TemplateResponse('memberlist.html',
            list=userlist,
            form=form.generate()
        )


class UserPage(RequestHandler):
    handler_regexes = [r'users/(?P<username>.+)$']

    def handle_request(self, req, username):
        # TODO: add a permission CAN_VIEW_PROFILE
        # check avatar
        if req.args.get('show') == 'avatar':
            avatar = get_user_avatar(req, username)
            if avatar is None:
                return PageNotFound()
            resp = Response(avatar)
            resp['Content-Type'] = 'image/png'
            return resp
        # display user
        user = get_user(req, username)
        if user is None:
            return PageNotFound()
        return TemplateResponse('user.html',
            person = user
        )


class GotoPage(RequestHandler):
    handler_regexes = ['goto$']

    def handle_request(self, req):
        if 'post' in req.args:
            post_id = req.args['post']
            post = get_post(req.ctx, post_id)
            while post.parent: #get root_post
                post = post.parent or post
            thread = req.db.get(Thread, Thread.c.root_post_id == post.post_id)
            return HttpRedirect(thread.url)
        else:
            return HttpRedirect(self.ctx.make_external_url('/'))


class SplitPage(RequestHandler, RemoteCallable):
    handler_regexes = [r'post/(?P<post_id>\d+)/split$']

    def handle_request(self, req, post_id):
        try:
            thread = Thread.by_child(req.ctx, post_id)
        except ValueError:
            return PageNotFound()
        if not req.user.acl.can_access('MODERATOR', thread.forum_id):
            return AccessDeniedResponse()
        return TemplateResponse('split.html',
            thread = {'root_post_id':thread.root_post_id, 'title':thread.title}
        )

    @export('split.get_post_tree')
    def split(self, req, root_post_id):
        def iterate_items(post_list):
            tmp = []
            for post in post_list:
                tmp.append({
                    'post_id': post["post_id"],
                    'title': post["title"],
                    'children': "children" in post and \
                                iterate_items(post["children"]) or [],
                    'parent_id': post["parent_id"]
                })
            return tmp

        post_tree = get_post_tree(req, root_post_id)

        if not req.user.acl.can_access('MODERATOR', post_tree["forum"]["forum_id"]):
            return AccessDeniedResponse()

        return {
            'posts':iterate_items(post_tree["posts"]),
            'thread':{
                'forum_id':post_tree["forum"]["forum_id"],
                'root_post_id':post_tree["post_id"]
            }
        }

    @export('split.commit')
    def commit(self, req, changes):
        # TODO: Check whether operation is allowed at every subforum of a thread
        #       the user changes
        for tmp in changes.iteritems():
            change = tmp[1]
            id = change['id']
            new_pid = change['new_pid']
            old_pid = change['old_pid']
            act_tid = change['act_tid']
            old_tid = change['old_tid']
            post = req.db.get(Post, Post.c.post_id == id)
            if new_pid != -1:
                post.parent_id = new_pid
            else:
                if act_tid == -1:
                    #XXX: forum_id
                    thread = Thread(
                        name = post.name,
                        forum_id = 1,
                        root_post_id = post.post_id
                    )
                    req.db.save(thread)
                else:
                    thread = req.db.get(Thread, Thread.c.thread_id == act_tid)
                    thread.name = post.name
                post.parent_id = thread.thread_id
        req.db.flush()
        return ""


class WhoIsOnlinePage(RequestHandler, PagePublisher):
    page_name = 'whoisonline'
    relative_url = 'whoisonline'
    handler_regexes = [r'whoisonline$']

    def handle_request(self, req):
        sessions, users, guests, total = get_active_sessions(req.ctx)
        return TemplateResponse('whoisonline.html',
            sessions=sessions,
            user_count=users,
            guest_count=guests,
            total_count=total
        )


class UserSettings(RequestHandler, PagePublisher):
    page_name = 'settings'
    relative_url = 'settings/'
    handler_regexes = [
        r'settings/$',
        r'settings/(?P<page>.+?)$'
    ]
    allow_username_change = cfg.bool('security', 'username_change', False)

    def handle_request(self, req, page=None):
        req.user.assert_logged_in()
        sidebar = []
        missing = object()
        page_result = missing
        for comp in self.ctx.get_components(UserSettingsPage):
            caption = comp.get_settings_link_title(req)
            # if the caption is None the plugin doesn't want to
            # be visible in the sidebar, skip
            if caption is None:
                continue
            active = comp.settings_page_identifier == page
            if active:
                page_result = comp.get_settings_page(req)
                # the page really wants to output data on its own
                # we don't need to create a sidebar, stop here
                if isinstance(page_result, Response):
                    return page_result
            sidebar.append({
                'url':        comp.url,
                'caption':    caption,
                'active':     active,
                'identifier': comp.settings_page_identifier
            })
        # display error page
        if page_result is missing and page is not None:
            return PageNotFound()
        # we have found a page, display it, but first sort the sidebar
        sidebar.sort(key=lambda x: x['caption'].lower())
        if page is None:
            return TemplateResponse('settings/index.html',
                setting_pages = sidebar
            )
        template, context = page_result
        context['setting_pages'] = sidebar
        return TemplateResponse(template, **context)


class LostPasswordPage(RequestHandler, PagePublisher):
    page_name = 'lostpassword'
    relative_url = 'lostpassword'
    handler_regexes = ['lostpassword$']

    def handle_request(self, req):
        # if the user is identified he has probably not lost has password ;)
        if req.user.identified:
            return HttpRedirect(self.ctx.make_external_url(''))

        _ = req.gettext
        ctx = self.ctx
        msg = None
        form = Form(req, self, 'POST',
            TextField('username', validator=isExistingUsername()),
            TextField('email', validator=isEmail())
        )

        if req.method == 'POST':
            form.update(req.form, prefix='f_')
            if not form.has_errors:
                d = form.to_dict()
                password = reset_password(ctx, **d)
                if password is not None:
                    text = render_template(req, 'mails/new_password.txt', {
                        'username':         d['username'],
                        'password':         password
                    })
                    mail = Email(ctx, _('New password'), d['email'], text)
                    mail.send()
                    return TemplateResponse('messages/password.html', **d)
                else:
                    msg = _('Creation of a new password failed. Username '
                            'or email address is invalid.')

        return TemplateResponse('lostpassword.html',
            form = form.generate(prefix='f_'),
            msg = msg
        )
