import pymysql
from .myutil import mymd5
import time
import datetime


class DBUtil:
    def __init__(self, **kwargs):
        conection = pymysql.connect(host=kwargs.get('host', '127.0.0.1'),
                                    port=kwargs.get('port', 3306),
                                    user=kwargs.get('user', 'root'),
                                    password=kwargs.get('password', '123456'),
                                    database=kwargs.get(
                                        'database', 'mindreaddb'),
                                    charset=kwargs.get('charset', 'utf8'))
        if conection:
            self.cursor = conection.cursor()
        else:
            raise Exception('数据库连接参数错误！')

    def saveuser(self, phone, password):
        sql = 'insert into tb_user(user_phone, user_password, user_name, user_createdat)\
            values (%s, %s, %s, %s)'
        params = (phone, password, 'phone'+phone, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        try:
            self.cursor.execute(sql, params)
            self.cursor.connection.commit()
        except Exception as e:
            print('错误信息：', e)

    def addBlogtoBook(self, user_id, ISBN, title, content):
        blog_id = mymd5(str(time.time()))
        sql = 'insert into tb_blog(blog_id, blog_title, blog_content, \
         blog_user_id, blog_book_ISBN, blog_createdat) values (%s, %s, %s, %s, %s, %s); \
         insert into tb_user_blog(user_blog_focus, user_blog_user_id, \
         user_blog_blog_id, user_blog_createdat) values (true, %s, %s, %s)'

        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        params = (blog_id, title, content, user_id, ISBN, now, user_id, blog_id, now)
        try:
            self.cursor.execute(sql, params)
            self.cursor.connection.commit()
        except Exception as e:
            print('错误信息', e)
        return True

    def delBlog(self, blog_id):
        sql = 'delete from tb_blog where blog_id = %s'
        params = (blog_id, )
        try:
            self.cursor.execute(sql, params)
            self.cursor.connection.commit()
        except Exception as e:
            print('错误信息', e)
        return True

    def unFocusBlog(self, user_id, blog_id):
        sql = "delete from tb_user_blog where user_blog_user_id = %s \
        and user_blog_blog_id = %s"
        params = (user_id, blog_id)
        try:
            self.cursor.execute(sql, params)
            self.cursor.connection.commit()
        except Exception as e:
            print('错误信息', e)
        return True

    def unfocUser(self, user_id, focused_id):
        sql = "delete from tb_user_focus where u_id = %s and focused_id = %s"
        params = (user_id, focused_id)
        try:
            self.cursor.execute(sql, params)
            self.cursor.connection.commit()
        except Exception as e:
            print('错误信息', e)
        return True

    def login(self, phone, password):

        sql = 'select count(*) from tb_user where user_phone=%s and \
         user_password=%s'
        params = (phone, password)
        self.cursor.execute(sql, params)
        self.cursor.connection.commit()
        result = self.cursor.fetchone()
        if result[0]:
            return True
        else:
            return False

    def checkphone(self, phone):

        sql = 'select count(*) from tb_user where user_phone=%s'
        params = (phone,)
        self.cursor.execute(sql, params)
        self.cursor.connection.commit()
        result = self.cursor.fetchone()  # (1,)(0,)
        if result[0]:
            return True  # 有这个名字
        else:
            return False  # 没有这个名字

    def checkcol(self, user_id, ISBN):
        sql = 'select count(*) from tb_user_book where user_book_user_id \
        = %s and user_book_book_ISBN = %s'
        params = (user_id, ISBN)
        self.cursor.execute(sql, params)
        self.cursor.connection.commit()
        result = self.cursor.fetchone()
        if result[0]:
            return True
        else:
            return False

    def colBook(self, user_id, ISBN, iscol):
        if iscol:
            sql = 'insert into tb_user_book(user_book_user_id, \
            user_book_book_ISBN) values (%s, %s)'
        else:
            sql = 'delete from tb_user_book where user_book_user_id = %s and \
            user_book_book_ISBN = %s'
        params = (user_id, ISBN)
        try:
            self.cursor.execute(sql, params)
            self.cursor.connection.commit()
        except Exception as e:
            print('错误信息：', e)
        return iscol

    def findBooks(self, title=None, tag=None, user_id=None, ISBN=None):
        books = []
        sql = ''
        params = tuple()
        if title is not None:
            title = '%'+'%'.join(title.split())+'%'
            sql = 'select book_ISBN, book_title, book_subtitle, \
            book_translator, book_img, book_press, book_date, book_price, \
            book_author, book_orititle from tb_book where book_title like %s \
            or book_subtitle like %s or book_orititle like %s order by \
            book_date desc'
            params = (title,)*3
        elif tag is not None:
            tag = '%'+'%'.join(tag.split())+'%'
            sql = 'select distinct book_ISBN, book_title, book_subtitle, ' \
             'book_translator, book_img, book_press, book_date, book_price, ' \
             'book_author, book_orititle from tb_book join tb_book_tag on ' \
             'book_ISBN = book_tag_book_ISBN join tb_tag on tag_id = ' \
             'book_tag_tag_id where tag_name like %s order by book_date desc '
            params = (tag,)
        elif user_id is not None:
            sql = 'select book_ISBN, book_title, book_subtitle, \
             book_translator, book_img, book_press, book_date, book_price, \
             book_author, book_orititle from tb_book join tb_user_book on \
             book_ISBN = user_book_book_ISBN join tb_user on user_id = \
             user_book_user_id where user_id=%s order by user_book_id desc'
            params = (user_id,)
        elif ISBN is not None:
            ISBN = '%'+'%'.join(ISBN.split())+'%'
            sql = 'select book_ISBN, book_title, book_subtitle, \
             book_translator, book_img, book_press, book_date, book_price, \
             book_author, book_orititle from tb_book where book_ISBN like %s \
             order by book_date desc'
            params = (ISBN,)
        if sql and params:
            self.cursor.execute(sql, params)
            self.cursor.connection.commit()
            result = self.cursor.fetchall()
            if result and result[0]:
                for b in result:
                    book = dict()
                    book['ISBN'] = b[0]
                    book['title'] = b[1]
                    book['subtitle'] = b[2]
                    book['translator'] = b[3]
                    book['img'] = b[4]
                    book['press'] = b[5]
                    book['date'] = b[6]
                    book['price'] = b[7]
                    book['author'] = b[8]
                    book['orititle'] = b[9]
                    books.append(book)
        return books

    def findBookbyISBN(self, ISBN, img=False):
        sql = "select * from tb_book where book_ISBN = %s"
        params = (ISBN,)
        self.cursor.execute(sql, params)
        self.cursor.connection.commit()
        b = self.cursor.fetchone()
        if b:
            book = dict()
            if img:
                book['img'] = b[4]
                return book
            book['ISBN'] = b[0]
            book['title'] = b[1]
            book['subtitle'] = b[2]
            book['translator'] = b[3]
            book['img'] = b[4]
            book['press'] = b[5]
            book['date'] = b[6]
            book['price'] = b[7]
            book['brief'] = b[8]
            book['catalog'] = b[9]
            book['author'] = b[10]
            book['orititle'] = b[11]
            return book
        else:
            return None

    def findUser(self, phone=None, user_id=None, brief=False):
        if phone is not None:
            sql = "select user_id, user_phone, user_email, user_name, \
            user_gender, user_avatar, user_createdat, user_selfintro \
            from tb_user where user_phone = %s"
            params = (phone,)
        elif user_id is not None:
            sql = "select user_id, user_phone, user_email, user_name, \
            user_gender, user_avatar, user_createdat, user_selfintro \
            from tb_user where user_id = %s"
            params = (user_id,)
        else:
            return None
        self.cursor.execute(sql, params)
        self.cursor.connection.commit()
        u = self.cursor.fetchone()
        if u:
            user = dict()
            if brief:
                user['user_id'] = u[0]
                user['name'] = u[3]
                user['avatar'] = u[5]
            else:
                user['user_id'] = u[0]
                user['phone'] = u[1]
                user['email'] = u[2]
                user['name'] = u[3]
                user['gender'] = u[4]
                user['avatar'] = u[5]
                user['createdat'] = u[6]
                user['selfintro'] = u[7]
            return user
        else:
            return None

    def findBlogs(self, user_id=None, ISBN=None, like=False):
        blogs = []
        if user_id is not None:
            if like:
                sql = "select blog_id, blog_title, blog_content, \
                blog_book_ISBN, blog_user_id, blog_createdat from \
                tb_blog join tb_user_blog on blog_id = \
                user_blog_blog_id where user_blog_user_id = %s and \
                user_blog_like = true order by \
                user_blog_createdat desc"
            else:
                sql = "select blog_id, blog_title, blog_content, \
                blog_book_ISBN, blog_user_id, blog_createdat from \
                tb_blog join tb_user_blog on blog_id = \
                user_blog_blog_id where user_blog_user_id = %s and \
                user_blog_focus = true order by \
                user_blog_createdat desc"
            params = (user_id,)
        elif ISBN is not None:
            sql = "select blog_id, blog_title, blog_content, \
            blog_book_ISBN, blog_user_id, blog_createdat from \
            tb_blog where blog_book_ISBN = %s order by blog_createdat desc"
            params = (ISBN, )
        else:
            return blogs
        self.cursor.execute(sql, params)
        self.cursor.connection.commit()
        result = self.cursor.fetchall()
        if result and result[0]:
            for b in result:
                blog = dict()
                blog['blog_id'] = b[0]
                blog['title'] = b[1]
                blog['content'] = b[2]
                blog['ISBN'] = b[3]
                blog['blog_user_id'] = b[4]
                blog['date'] = b[5]
                blogs.append(blog)
        return blogs

    def findComments(self, blog_id):
        comments = []
        sql = 'select comment_id, comment_content, comment_blog_id, \
        comment_user_id from tb_comment where comment_blog_id = %s'
        params = (blog_id,)
        self.cursor.execute(sql, params)
        self.cursor.connection.commit()
        result = self.cursor.fetchall()
        if result and result[0]:
            for c in result:
                comment = dict()
                comment['comment_id'] = c[0]
                comment['content'] = c[1]
                comment['comment_blog_id'] = c[2]
                comment['comment_user_id'] = c[3]
                comments.append(comment)
        return comments

    def findBlog(self, blog_id):
        sql = "select blog_id, blog_title, blog_content, blog_book_ISBN, \
         blog_user_id, blog_createdat from tb_blog where blog_id = %s"
        params = (blog_id,)
        self.cursor.execute(sql, params)
        self.cursor.connection.commit()
        result = self.cursor.fetchone()
        if result:
            blog = dict()
            blog['blog_id'] = result[0]
            blog['title'] = result[1]
            blog['content'] = result[2]
            blog['ISBN'] = result[3]
            blog['blog_user_id'] = result[4]
            blog['date'] = result[5]
            return blog
        else:
            return None

    def updateUser(self, user_id, name, email, gender, selfintro, avatar):
        sql = "update tb_user set user_name = %s, user_email = %s, \
         user_gender = %s, user_selfintro = %s, user_avatar = %s , \
         user_updatedat = %s where user_id = %s"
        params = (name, email, gender, selfintro, avatar, user_id, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        try:
            self.cursor.execute(sql, params)
            self.cursor.connection.commit()
        except Exception as e:
            print('错误信息', e)
        return True

    def addCommenttoBlog(self, user_id, blog_id, content):
        sql = "insert into tb_comment(comment_user_id, comment_blog_id, \
        comment_content, comment_createdat) values (%s, %s, %s, %s)"
        params = (user_id, blog_id, content, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        try:
            self.cursor.execute(sql, params)
            self.cursor.connection.commit()
        except Exception as e:
            print('错误信息', e)
        return True

    def complainCom(self, comment_id):
        sql = "update tb_comment set comment_iscomplained = true where \
        comment_id = %s"
        params = (comment_id,)
        try:
            self.cursor.execute(sql, params)
            self.cursor.connection.commit()
        except Exception as e:
            print('错误信息', e)
        return True

    def focBlog(self, user_id, blog_id):
        sql = 'select count(*) from tb_user_blog where user_blog_user_id = %s \
        and user_blog_blog_id = %s'
        params = (user_id, blog_id)
        self.cursor.execute(sql, params)
        self.cursor.connection.commit()
        result = self.cursor.fetchone()
        if not result[0]:
            sql = 'insert into tb_user_blog(user_blog_user_id, user_blog_blog_id, \
            user_blog_focus, user_blog_createdat) values (%s, %s, %s, %s)'
            params = (user_id, blog_id, True, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            try:
                self.cursor.execute(sql, params)
                self.cursor.connection.commit()
            except Exception as e:
                print('错误信息', e)
        return True

    def focUser(self, u_id, focused_id):
        sql = 'select count(*) from tb_user_focus where u_id = %s \
        and focused_id = %s'
        params = (u_id, focused_id)
        self.cursor.execute(sql, params)
        self.cursor.connection.commit()
        result = self.cursor.fetchone()
        if not result[0]:
            sql = 'insert into tb_user_focus(u_id, focused_id) values \
            (%s, %s)'
            try:
                self.cursor.execute(sql, params)
                self.cursor.connection.commit()
            except Exception as e:
                print('错误信息', e)
        return True

    def findFocusedUsers(self, user_id):
        sql = 'select focused_id from tb_user_focus where u_id = %s'
        params = (user_id, )
        self.cursor.execute(sql, params)
        self.cursor.connection.commit()
        result = self.cursor.fetchall()
        users = []
        if result and result[0]:
            for u in result:
                users.append(u[0])
        return users


