import io
from tornado.web import RequestHandler, asynchronous
from tornado import gen
from front.util.myutil import mymd5, create_validate_code, send_sms
from front.util.session import MySession
import time
from front.util.crawlutil import crawlbyWord
from front.controllers.modules import BookModule, UserBlogModule, BookBlogModule, CommentModule
import multiprocessing


class BaseHandler(RequestHandler):
    def initialize(self):
        self.session = MySession(self)


class LogoutHandler(BaseHandler):
    def get(self, *args, **kwargs):
        self.clear_all_cookies()
        self.redirect('/')


class DelBlogHandler(BaseHandler):
    @gen.coroutine
    def post(self, *args, **kwargs):
        user_id = self.session['user_id']
        blog_id = self.get_body_argument('blog_id')
        if self.get_body_argument('user_id') == user_id:
            success = self.application.dbutil.delBlog(blog_id)
        else:
            success = self.application.dbutil.unFocusBlog(
                user_id=user_id, blog_id=blog_id
            )
        self.write({"success": success})


class BookHandler(BaseHandler):
    @gen.coroutine
    def get(self, *args, **kwargs):
        ISBN = self.get_query_argument('ISBN')
        book = self.application.dbutil.findBookbyISBN(ISBN)
        blogs = self.application.dbutil.findBlogs(ISBN=ISBN)
        user = dict()
        if self.session['islogin']:
            user = self.application.dbutil.findUser(
                user_id=self.session['user_id'], brief=True)
        if book['brief']:
            book['brief'] = '<br>'.join(book['brief'].split('\n'))
        if book['catalog']:
            book['catalog'] = '<br>'.join(book['catalog'].split('\n'))
        self.render(
            'book.html', islogin=self.session['islogin'], blogs=blogs,
            **dict(book, **user))

    @gen.coroutine
    def post(self, *args, **kwargs):
        if self.session['islogin']:
            user_id = self.session['user_id']
            ISBN = self.get_body_argument('ISBN')
            title = self.get_body_argument('title')
            content = self.get_body_argument('content')
            success = self.application.dbutil.addBlogtoBook(
                user_id=user_id, ISBN=ISBN, title=title, content=content)
            if success:
                blogsHtml = ''
                blogs = self.application.dbutil.findBlogs(ISBN=ISBN)
                blogmodule = BookBlogModule(self)
                for blog in blogs:
                    blogsHtml += blogmodule.render(**blog).decode()
                self.write({'islogin': True,
                            'success': True, 'blogsHtml': blogsHtml})
            else:
                self.write({'islogin': True, 'success': False})
        else:
            self.write({'islogin': False})


class BlogsHandler(BaseHandler):
    @gen.coroutine
    def get(self, *args, **kwargs):
        if self.session['islogin']:
            user_id = self.get_query_argument('id')
            blogsHtml = ''
            blogs = self.application.dbutil.findBlogs(user_id=user_id)
            blogsmodule = UserBlogModule(self)
            for blog in blogs:
                blogsHtml += blogsmodule.render(**blog).decode()
            self.write({'blogsHtml': blogsHtml})
        else:
            self.write({'blogsHtml': '<h1 style="color:black;">请登录铭阅！<h1>'})


class BooksHandler(BaseHandler):
    @gen.coroutine
    def get(self, *args, **kwargs):
        if self.session['islogin']:
            user_id = self.get_query_argument('id')
            w = self.get_query_argument('w')
            opt = self.get_query_argument('opt')
            booksHtml = ''
            findBooks = self.application.dbutil.findBooks
            if w and opt:
                if opt == '2':
                    books = findBooks(ISBN=w)
                if opt == '1':
                    books = findBooks(tag=w)
                if opt == '0':
                    books = findBooks(title=w)
                    if len(books) < 5:

                        time.sleep(10)
                        self.application.q.put(w)
            else:
                books = findBooks(user_id=user_id)
            booksmodule = BookModule(self)
            for book in books:
                booksHtml += booksmodule.render(**book).decode()
            self.write({'booksHtml': booksHtml})
        else:
            self.write({'booksHtml': '<h1 style="color:black;">请登录铭阅！<h1>'})


class IndexHandler(BaseHandler):
    @gen.coroutine
    def get(self, *args, **kwargs):
        # 服务器向浏览器检查session
        if self.session['islogin']:
            phone = self.session['phone']
            user = self.application.dbutil.findUser(phone=phone, brief=True)
            if user:
                self.session['user_id'] = str(user['user_id'])
                books = self.application.dbutil.findBooks(
                    user_id=user['user_id'])
                self.render('index.html', books=books, **user)
            else:
                self.write('The user is not exist!')
        else:
            self.redirect('/login')

    @gen.coroutine
    def post(self, *args, **kwargs):
        self.redirect('/search?w='+self.get_body_argument('w') +
                      '&opt='+self.get_body_argument('opt'))


class LoginHandler(BaseHandler):
    def get(self, *args, **kwargs):
        m = ''
        if self.request.query == 'msg=fail':
            m = '用户名或密码错误！'
        elif self.request.query == 'check=fail':
            m = '验证码错误！'
        self.render('login.html', result=m)

    @gen.coroutine
    def post(self, *args, **kwargs):
        phone = self.get_body_argument('phone')
        password = self.get_body_argument('password')
        code = mymd5(self.get_body_argument('code').upper())
        check_code = self.session['CheckCode']
        if code != check_code:
            self.redirect('/login?check=fail')
        else:
            # MyApplication中的dbutil属性所引用的那个DBUtil对象
            if self.application.dbutil.login(phone=phone,
                                             password=mymd5(password)):
                self.session['islogin'] = True
                self.session['phone'] = phone
                self.redirect('/')
            else:
                self.redirect('/login?msg=fail')


class RegistHandler(BaseHandler):
    def get(self, *args, **kwargs):
        m = ''
        # 根据msg的不同信息，生成不同的m内容
        # empty：注册信息不完整
        # duplicate:用户名充分
        # dberror:数据库错误
        if self.request.query:
            # msg=empty
            q = self.request.query.split('=')[1]
            if q == 'empty':
                m = '注册信息不完整'
            if q == 'duplicate':
                m = '用户名重复'
            if q == 'dberror':
                m = '数据库错误，稍后重试'
            if q == 'wrongcode':
                m = '验证码错误'
        self.render('regist.html', result=m)

    @gen.coroutine
    def post(self, *args, **kwargs):
        phone = self.session['phone']
        password = self.get_body_argument('password')
        code = self.get_body_argument('code')

        if self.session['code'] == code:
            if phone and password:
                try:
                    self.application.dbutil.saveuser(
                        phone=phone, password=mymd5(password))
                except Exception as e:
                    info = str(e)  # 'dberror''duplicate'
                    self.redirect('/regist?msg='+info)

                self.redirect('/login')

            else:
                self.redirect('/regist?msg=empty')
        self.redirect('/regist?msg=wrongcode')


class CheckCodeHandler(BaseHandler):
    @gen.coroutine
    def get(self, *args, **kwargs):  # 生成图片并返回
        mstream = io.BytesIO()
        # 创建图片 并写入验证码
        img, code = create_validate_code()
        # 讲图片对象写入到mastream
        img.save(mstream, 'GIF')
        self.session['CheckCode'] = mymd5(code.upper())
        # 为每个用户保存验证码的加密值
        self.write(mstream.getvalue())
        # 返回图片给客户端


class CheckHandler(BaseHandler):
    @gen.coroutine
    def post(self, *args, **kwargs):

        type = self.get_body_argument("type")

        if type == 'regist':

            phone = self.get_body_argument('phone')
            if self.application.dbutil.checkphone(phone):
                # 返回一个信息，告诉用户该手机号不能被使用
                self.write({'msg': 'fail'})
            else:
                # 返回一个信息，告诉用户该手机号能被使用
                self.write({'msg': 'ok'})

        if type == 'col':
            if self.session['islogin']:
                ISBN = self.get_body_argument('ISBN')
                user_id = self.session['user_id']
                self.write({'islogin': True,
                            'iscol': self.application.dbutil.checkcol(
                                user_id, ISBN
                            )})
            else:
                self.write({'islogin': False})


class ColBookHandler(BaseHandler):
    @gen.coroutine
    def post(self, *args, **kwargs):
        if self.session['islogin']:
            ISBN = self.get_body_argument('ISBN')
            action = self.get_body_argument('action')
            user_id = self.session['user_id']
            if action == '收藏本书':
                self.write({'islogin': True,
                            'iscol': self.application.dbutil.colBook(
                                user_id, ISBN, iscol=True
                            )})
            else:
                self.write({'islogin': True,
                            'iscol': self.application.dbutil.colBook(
                                user_id, ISBN, iscol=False
                            )})
        else:
            self.write({'islogin': False})


class InfoHandler(BaseHandler):
    @gen.coroutine
    def get(self, *args, **kwargs):
        if self.session['islogin']:
            user_id = self.session['user_id']
            user = self.application.dbutil.findUser(user_id=user_id)
            users = self.application.dbutil.findFocusedUsers(user_id=user_id)
            self.render('info.html', users=users, **user)
        else:
            self.redirect('/login')

    @gen.coroutine
    def post(self, *args, **kwargs):
        if self.session['islogin']:
            user_id = self.session['user_id']

            name = self.get_body_argument('name')
            email = self.get_body_argument('email')
            gender = self.get_body_argument('gender')
            selfintro = self.get_body_argument('selfintro')
            avatar = user_id+'.jpg'
            if self.request.files:
                file = self.request.files['avatar'][0]
                # 把用户上传的头像文件保存到服务器磁盘
                path = user_id+'.'+file['filename'].split('.')[-1]
                writer = open('statics/images/{}'.format(path), 'wb')
                writer.write(file['body'])
                writer.close()
                avatar = path
            self.application.dbutil.updateUser(user_id=user_id,
                                               name=name, email=email,
                                               gender=gender,
                                               selfintro=selfintro,
                                               avatar=avatar)
            self.redirect('/')
        else:
            self.redirect('/login')


class CommentsHandler(BaseHandler):
    @gen.coroutine
    def get(self, *args, **kwargs):
        blog_id = self.get_query_argument('blog_id')
        blog = self.application.dbutil.findBlog(blog_id)
        comments = self.application.dbutil.findComments(blog_id=blog_id)
        img = self.application.dbutil.findBookbyISBN(
            ISBN=blog['ISBN'], img=True)['img']
        blog_user = self.application.dbutil.findUser(
            user_id=blog['blog_user_id'], brief=True)
        if blog['content']:
            blog['content'] = '<br>'.join(blog['content'].split('\n'))
        self.render('comments.html', islogin=self.session['islogin'],
                    blog_user=blog_user, comments=comments, img=img, **blog)

    @gen.coroutine
    def post(self, *args, **kwargs):
        if self.session['islogin']:
            user_id = self.session['user_id']
            blog_id = self.get_body_argument('blog_id')
            content = self.get_body_argument('content')
            success = self.application.dbutil.addCommenttoBlog(
                user_id=user_id, blog_id=blog_id, content=content)
            if success:
                commentsHtml = ''
                comments = self.application.dbutil.findComments(
                    blog_id=blog_id)
                commentmodule = CommentModule(self)
                for comment in comments:
                    commentsHtml += commentmodule.render(**comment).decode()
                self.write({'islogin': True,
                            'success': True, 'commentsHtml': commentsHtml})
            else:
                self.write({'islogin': True, 'success': False})
        else:
            self.write({'islogin': False})


class ComplainHandler(BaseHandler):
    @gen.coroutine
    def post(self, *args, **kwargs):
        if self.session['islogin']:
            comment_id = self.get_body_argument('comment_id')
            self.application.dbutil.complainCom(comment_id=comment_id)
            self.write({'islogin': True, 'success': True, })
        else:
            self.write({'islogin': False})


class FocBlogHandler(BaseHandler):
    @gen.coroutine
    def post(self, *args, **kwargs):
        if self.session['islogin']:
            user_id = self.session['user_id']
            blog_id = self.get_body_argument('blog_id')
            self.application.dbutil.focBlog(user_id=user_id, blog_id=blog_id)
            self.write({'islogin': True, 'success': True, })
        else:
            self.write({'islogin': False})


class UserHandler(BaseHandler):
    @gen.coroutine
    def get(self, *args, **kwargs):
        user_id = self.get_query_argument('id')
        user = self.application.dbutil.findUser(user_id=user_id)
        users = self.application.dbutil.findFocusedUsers(user_id=user_id)
        if self.session['islogin']:
            self.render('user.html', islogin=True, users=users, **user)
        else:
            self.render('user.html', islogin=False, users=users, **user)

    @gen.coroutine
    def post(self, *args, **kwargs):
        if self.session['islogin']:
            success = self.application.dbutil.focUser(
                self.session['user_id'],
                self.get_body_argument('user_id')
            )
            self.write({'islogin': True, 'success': success})
        else:
            self.write({'islogin': False})


class UnfocUserHandler(BaseHandler):
    @gen.coroutine
    def post(self, *args, **kwargs):
        if self.session['islogin']:
            success = self.application.dbutil.unfocUser(
                self.session['user_id'],
                self.get_body_argument('user_id')
            )
            self.write({'islogin': True, 'success': success})
        else:
            self.write({'islogin': False})


class SendCodeHandler(BaseHandler):
    def post(self, *args, **kwargs):
        phone = self.get_body_argument('phone')
        self.session['phone'] = phone
        status, self.session['code'] = send_sms(phone)
        if status == 2:
            self.write({'success': True})
        else:
            self.write({'success': False})
