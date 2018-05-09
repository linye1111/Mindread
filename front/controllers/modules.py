from tornado.web import UIModule


class BookModule(UIModule):
    def render(self, *args, **kwargs):
        return self.render_string('modules/book_module.html', **kwargs)


class UserBlogModule(UIModule):
    def render(self, *args, **kwargs):
        img = self.handler.application.dbutil.findBookbyISBN(
            ISBN=kwargs['ISBN'], img=True)['img']
        user = self.handler.application.dbutil.findUser(
            user_id=kwargs['blog_user_id'], brief=True)
        kwargs['content'] = '<br>'.join(kwargs['content'].split('\n'))
        isU = user['user_id'] == self.handler.session['user_id']
        return self.render_string('modules/user_blog_module.html', isU=isU,
                                  img=img, **dict(kwargs, **user))


class BookBlogModule(UIModule):
    def render(self, *args, **kwargs):
        user = self.handler.application.dbutil.findUser(
            user_id=kwargs['blog_user_id'], brief=True)
        kwargs['content'] = '<br>'.join(kwargs['content'].split('\n'))
        return self.render_string('modules/book_blog_module.html',
                                  **dict(kwargs, **user))


class CommentModule(UIModule):
    def render(self, *args, **kwargs):
        user = self.handler.application.dbutil.findUser(
            user_id=kwargs['comment_user_id'], brief=True)
        kwargs['content'] = '<br>'.join(kwargs['content'].split('\n'))
        return self.render_string('modules/comment_module.html',
                                  **dict(kwargs, **user))


class UserModule(UIModule):
    def render(self, *args, **kwargs):
        user = self.handler.application.dbutil.findUser(
            user_id=kwargs['user_id'], brief=True)
        return self.render_string('modules/user_module.html',
                                  **dict(kwargs, **user))


class UModule(UIModule):
    def render(self, *args, **kwargs):
        u = self.handler.application.dbutil.findUser(
            user_id=self.handler.session['user_id'], brief=True)
        return self.render_string('modules/u_module.html', **u)
