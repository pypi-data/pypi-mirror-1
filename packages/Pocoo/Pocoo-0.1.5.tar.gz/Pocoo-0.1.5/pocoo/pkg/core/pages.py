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
from pocoo.application import Page

from pocoo.utils.mail import Email
from pocoo.utils.net import make_url_context_external
from pocoo.utils.json import parse_datetime
from pocoo.utils.tabbox import TabBox, Tab

from pocoo.pkg.core.remotecall import RemoteCallable, export
from pocoo.pkg.core.usersettings import UserSettingsPage
from pocoo.pkg.core.db import users
from pocoo.pkg.core.forum import get_forum_index, get_forum, get_post_tree, \
     get_forum_pathbar, get_view_mode, get_flat_view, quote_post, edit_post, \
     get_post, Thread, get_last_posts, get_last_thread_change, get_post_pathbar
from pocoo.pkg.core.user import User, get_user_list, \
     get_user, get_user_avatar, reset_password
from pocoo.pkg.core.session import get_active_sessions, get_sessions_by_action
from pocoo.pkg.core.textfmt import parse_and_render, get_editor
from pocoo.pkg.core.search import search
from pocoo.pkg.core.forms import LoginForm, RegisterForm, NewPostForm, \
     MemberListForm, LostPasswordForm

_ = lambda x: x


class IndexPage(Page, PagePublisher, RemoteCallable):
    page_name = 'index'
    relative_url = ''
    handler_regexes = [u'$']

    def handle_request(self, req):
        return TemplateResponse('index.html',
            categories=get_forum_index(req),
            feed_url=self.ctx.make_url('feeds/recent.xml')
        )


class ForumPage(Page):
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


class PostPage(Page, RemoteCallable):
    handler_regexes = [r'post/(?P<post_id>\d+)$']

    def handle_request(self, req, post_id):
        post_id = int(post_id)
        if not req.user.acl.can_access_post('READ_POST', post_id):
            return AccessDeniedResponse()

        rights = {
            'delete_post': req.user.acl.can_access_post('DELETE_POST', post_id),
            'lock_topic': req.user.acl.can_access_post('LOCK_TOPIC', post_id),
            'delete_topic': req.user.acl.can_access_post('DELETE_TOPIC', post_id)
        }

        view = get_view_mode(req)
        if view == 'flat':
            return self._flat_view(req, post_id, rights)
        else:
            return self._threaded_view(req, post_id, rights)

    def _flat_view(self, req, post_id, rights):
        topic = get_flat_view(req, post_id)
        if topic is None:
            return PageNotFound()
        return TemplateResponse('viewtopic.html',
            topic=topic,
            pathbar=get_post_pathbar(self.ctx, topic['posts'][0]['post_id']),
            feed_url=self.ctx.make_url('feeds/thread/%d.xml' % post_id),
            rights=rights
        )

    def _threaded_view(self, req, post_id, rights):
        thread = get_post_tree(req, post_id)
        if thread is None:
            return PageNotFound()
        return TemplateResponse('viewthread.html',
            thread=thread,
            pathbar=get_post_pathbar(self.ctx, thread['posts'][0]['post_id']),
            feed_url=self.ctx.make_url('feeds/thread/%d.xml' % post_id),
            rights=rights
        )

    @export('thread.get_post')
    def _get_post(self, req, post_id):
        if not req.user.acl.can_access_post('READ_POST', post_id):
            return AccessDeniedResponse()
        post = get_post(req, post_id)
        if post is None:
            return

        #FIXME: Why isn't this working?
        # After this, req.user.acl.can_access_post('DELETE_POST', post_id) is still False
        req.user.acl.set_post_privilege('DELETE_POST', post_id, 2)

        return render_template(req, 'partial/post.html', {
            'post':     post,
            'rights':   {
                'delete_post': req.user.acl.can_access_post('DELETE_POST', post_id),
            }
        })

    @export('thread.tree_requires_update')
    def _tree_requires_update(self, req, post_id, last_update):
        last_update = parse_datetime(last_update)
        last_thread_change = get_last_thread_change(req, post_id)
        return last_thread_change is not None and \
               last_thread_change > last_update

    @export('thread.get_tree')
    def _get_tree(self, req, post_id):
        if not req.user.acl.can_access_post('READ_POST', post_id):
            return AccessDeniedResponse()
        return render_template(req, 'partial/tree.html', {
            'posts':        get_post_tree(req, post_id)['posts']
        })


class LoginPage(Page, PagePublisher):
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
        form = LoginForm(req, self, 'POST')
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


class LogoutPage(Page, PagePublisher):
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


class RegisterPage(Page, PagePublisher):
    page_name = 'register'
    relative_url = 'register'
    handler_regexes = ['register$']

    def handle_request(self, req):
        coppa = req.ctx.cfg.get_bool('board', 'enable_coppa', False)
        activation = req.ctx.cfg.get_bool('board', 'email_verification', False)

        if req.user.identified:
            return HttpRedirect('')
        if 'activate' in req.args and 'user' in req.args:
            return self.activation(req)
        _ = req.gettext
        form = RegisterForm(req, self, 'POST')
        if req.method == 'POST':
            form.update(req.form, prefix='f_')
            if not form.has_errors:
                d = form.to_dict()
                user = User.create(req.ctx,
                    d['username'],
                    d['password'],
                    d['email'],
                    activation
                )
                if activation:
                    link = self.ctx.make_external_url('register?user=%s&activate=%s' %
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
                    requires_activation=activation,
                    username=d['username'],
                    email=d['email']
                )
        return TemplateResponse('register.html',
            form=form.generate(prefix='f_'),
            coppa_enabled=coppa
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
                user.save()
                activated = True
                username = user.username
        return TemplateResponse('messages/activation.html',
            username=username,
            activated=activated
        )


class NewPostPage(Page, RemoteCallable):
    handler_regexes = [
        (r'post/(?P<post_id>\d+)/reply$',
         {'action':'reply'}),
        (r'post/(?P<post_id>\d+)/quote$',
         {'action':'quote'}),
        (r'post/(?P<post_id>\d+)/edit$',
         {'action':'edit'})
    ]

    @export("newpost.box")
    def box(self, req, page, *args):

        page = int(page)
        if page == 1:
            return render_template(req, 'partial/preview.html',
                {'text':parse_and_render(req, args[0])})

    def handle_request(self, req, action, post_id):
        post_id = int(post_id)
        try:
            thread = Thread.by_child(self.ctx, post_id)
        except ValueError:
            return PageNotFound()
        _ = req.gettext

        # note: quote_post can raise a ValueError when a post does
        # not exist. but since we check for that by calling
        # Thread.by_child this shouldn't happen.
        username = _('anonymous')
        preview = ""

        if action == 'reply':
            mode = 'reply'
            if not req.user.acl.can_access_post('REPLY_POST', post_id):
                return AccessDeniedResponse()
            text = u''
            __, title = quote_post(req, post_id)
        elif action == 'quote':
            mode = 'reply'
            if not req.user.acl.can_access_post('REPLY_POST', post_id):
                return AccessDeniedResponse()
            text, title = quote_post(req, post_id)
        else:
            mode = 'edit'
            #XXX: also check for EDIT_OWN_POST
            if not req.user.acl.can_access_post('EDIT_POST', post_id):
                return AccessDeniedResponse()
            text, title, username = edit_post(req, post_id)

        form = NewPostForm(req, req.environ['APPLICATION_REQUEST'], 'POST', {
            'username': username,
            'title':    title,
            'text':     text
        })

        if req.method == 'POST':
            form.update(req.form, prefix='f_')
            if not form.has_errors and 'partial' not in req.form:
                d = form.to_dict()
                if "preview" in req.form:
                    #XXX
                    req.form['partial'] = 2
                else:
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

        f = form.generate(prefix='f_')

        box = TabBox(req, self.box, True,
            Tab(_("Latest Posts"), lazy=True, short_name="lposts"),
            Tab(_("Preview"), static=False, send=[f["text"]["name"]],
                short_name="preview")
        )

        js, options = get_editor(req)
        return TemplateResponse('newpost.html',
            mode = mode,
            form = f,
            show_username_entry = not req.user.identified,
            editor_options = options,
            editor_javascript = js,
            post_id = thread.root_post_id,
            pathbar=get_post_pathbar(req.ctx, post_id),
            preview = preview,
            tabbox = box
        )

    @export('newpost.check')
    def check(self, req, root_post_id, latest_post):
        latest_post = latest_post and int(latest_post) or None
        post_list = []
        if not latest_post:
            post_list = get_last_posts(req, root_post_id, 5)
        else:
            post = get_last_posts(req, root_post_id, 1)[0]
            if latest_post != post['post_id']:
                z = 1
                while post['post_id'] != latest_post and z < 5:
                    post_list.append(post)
                    post = get_last_posts(req, root_post_id, 1, z)[0]
                    z += 1

        return post_list and {
                'html': render_template(req, 'partial/latestposts.html',
                    {'posts': post_list }),
                'latestpost': post_list[0]["post_id"]
            } or ""


class NewThreadPage(Page, RemoteCallable):
    handler_regexes = [r'forum/(?P<forum_id>\d+)/new$']

    @export("newthread.box")
    def box(self, req, page, *args):
        page = int(page)
        if page == 0:
            return render_template(req, 'partial/preview.html',
                {'text':parse_and_render(req, len(args) and args[0] or "")})

    def handle_request(self, req, forum_id):
        _ = req.gettext
        preview = ""
        forum_id = int(forum_id)
        if not req.user.acl.can_access_forum('CREATE_THREAD', forum_id):
            return AccessDeniedResponse()

        form = NewPostForm(req, req.environ['APPLICATION_REQUEST'], 'POST', {
            'username': _('anonymous')
        })

        if req.method == 'POST':
            form.update(req.form, prefix='f_')
            if not form.has_errors and 'partial' not in req.form:
                d = form.to_dict()
                if 'preview' in req.form:
                    #XXX
                    req.form['partial'] = 3
                elif 'submit' in req.form:
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

        f = form.generate(prefix='f_')

        box = TabBox(req, self.box, True,
            Tab(_("Preview"), static=False, send=[f["text"]["name"]],
                short_name="preview")
        )

        js, options = get_editor(req)
        return TemplateResponse('newthread.html',
            show_username_entry = not req.user.identified,
            form = f,
            editor_options = options,
            editor_javascript = js,
            pathbar = get_forum_pathbar(self.ctx, forum_id),
            preview = preview,
            tabbox = box
        )


class MemberListPage(Page, PagePublisher):
    page_name = 'memberlist'
    relative_url = 'users/'
    handler_regexes = [r'users/$']

    def handle_request(self, req):
        _ = req.gettext
        generate = False

        form = MemberListForm(req, self, 'GET', {
            'order_by':         'user_id',
            'direction':        'asc'
        })

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
                order_by=d['order_by'],
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


class UserPage(Page):
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
        user = get_user(req.ctx, username)
        if user is None:
            return PageNotFound()
        return TemplateResponse('user.html',
            person = user
        )


class SearchPage(Page, PagePublisher):
    page_name = 'search'
    relative_url = 'search/'
    handler_regexes = [r'search/$']

    def handle_request(self, req):
        if 'q' in req.values:
            try:
                page = abs(int(req.values['page']))
            except (ValueError, KeyError):
                page = 1
            rv = search(req, req.values['q'], 30, page)
            if rv is None:
                return PageNotFound()
            return TemplateResponse('search/results.html', **rv)
        return TemplateResponse('search/form.html')


class WhoIsOnlinePage(Page, PagePublisher):
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


class UserSettings(Page, PagePublisher):
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


class LostPasswordPage(Page, PagePublisher):
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
        form = LostPasswordForm(req, self, 'POST')

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


class PostOperationsPage(Page):
    handler_regexes = [
        (r'post/(?P<post_id>\d+)/lock$',
         {'action':'lock'}),
        (r'post/(?P<post_id>\d+)/unlock$',
         {'action':'unlock'}),
        (r'post/(?P<post_id>\d+)/delete$',
         {'action':'delete_post'}),
        (r'post/(?P<post_id>\d+)/delete_thread$',
         {'action':'delete_thread'})
    ]

    def handle_request(self, req, action, post_id):
        """
        Use the following command for testing:
            req.user.acl.set_forum_privilege('MODERATE_FORUM', forum_id, 2)
        Execute the following line also if you want to store the permission in the
        database:
            req.user.save()
        """
        try:
            thread = Thread.by_child(req.ctx, post_id)
        except ValueError:
            return PageNotFound()

        if not req.user.acl.can_access_forum('MODERATE_FORUM', thread.forum_id):
            return AccessDeniedResponse()

        if req.method == 'POST' and 'continue' in req.form:
            if action == 'delete_post':
                thread.delete_reply(post_id)
            elif action == 'lock':
                thread.lock()
            elif action == 'unlock':
                thread.unlock()
            elif action == 'delete_thread':
                thread.delete()
            thread.save()
            return TemplateResponse('messages/operation_done.html',
                action = action,
                url = self.ctx.make_url('post/%s' % post_id)
            )
        elif 'abort' in req.form:
            return HttpRedirect(self.ctx.make_url('post/%s' % post_id))
        else:
            return TemplateResponse('messages/operation_request.html',
                action = action
            )

"""
Old SplitPage

class SplitPage(Page, RemoteCallable):
    handler_regexes = [r'post/(?P<post_id>\d+)/split$']

    def handle_request(self, req, post_id):
        try:
            thread = Thread.by_child(req.ctx, post_id)
        except ValueError:
            return PageNotFound()
        if not req.user.acl.can_access('MODERATOR', thread.forum_id):
            return AccessDeniedResponse()
        return TemplateResponse('split.html',
            thread = {
                'root_post_id': thread.root_post_id,
                'title':        thread.title
            }
        )

    @export('split.get_post_tree')
    def split(self, req, root_post_id):
        def iterate_items(post_list):
            tmp = []
            for post in post_list:
                tmp.append({
                    'post_id':  post['post_id'],
                    'title':    post['title'],
                    'children': 'children' in post and \
                                iterate_items(post['children']) or [],
                    'parent_id': post['parent_id']
                })
            return tmp

        post_tree = get_post_tree(req, root_post_id)

        if not req.user.acl.can_access('MODERATOR', post_tree['forum']['forum_id']):
            return AccessDeniedResponse()

        return {
            'posts':    iterate_items(post_tree["posts"]),
            'thread': {
                'forum_id':     post_tree["forum"]["forum_id"],
                'root_post_id': post_tree["post_id"]
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
"""
