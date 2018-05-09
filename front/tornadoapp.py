#!/usr/bin/python3
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
from controllers.handles import IndexHandler, LoginHandler,\
    RegistHandler, CheckHandler, CheckCodeHandler, InfoHandler, \
    BooksHandler, BlogsHandler, ColBookHandler, ComplainHandler, \
    BookHandler, DelBlogHandler, LogoutHandler, CommentsHandler, \
    FocBlogHandler, UserHandler, UnfocUserHandler, SendCodeHandler
from controllers.modules import BookModule, UserBlogModule, \
    BookBlogModule, CommentModule, UserModule, UModule
import os
from tornado.web import Application
from util.dbutil import DBUtil
from configuration import mysettings
import multiprocessing
from util.crawlutil import crawlbyWord


class MyApplication(Application):
    def __init__(self, handlers, tp, sp, ui):

        super().__init__(handlers,
                         template_path=tp,
                         static_path=sp,
                         ui_modules=ui,
                         debug=True)
        self.dbutil = DBUtil(**mysettings.settings['dbsetting'])
        self.q = multiprocessing.Queue()
        for _ in range(mysettings.settings['crawl_num']):
            multiprocessing.Process(target=crawlbyWord, args=(self.q,)).start()


app = MyApplication([(r'/', IndexHandler),
                     (r'^/books', BooksHandler),
                     (r'^/book', BookHandler),
                     (r'^/blogs', BlogsHandler),
                     (r'^/login', LoginHandler),
                     (r'^/regist', RegistHandler),
                     (r'^/check', CheckHandler),
                     (r'^/check_code', CheckCodeHandler),
                     (r'^/delblog', DelBlogHandler),
                     (r'^/logout', LogoutHandler),
                     (r'^/colbook', ColBookHandler),
                     (r'^/info', InfoHandler),
                     (r'^/comments', CommentsHandler),
                     (r'^/cpl', ComplainHandler),
                     (r'^/focblog', FocBlogHandler),
                     (r'^/user', UserHandler),
                     (r'^/unfocuser', UnfocUserHandler),
                     (r'^/sendcode', SendCodeHandler)
                     ],
                    tp='views',
                    sp=os.path.join(os.path.dirname(__file__), "statics"),
                    ui={'bookmodule': BookModule,
                        'userblogmodule': UserBlogModule,
                        'bookblogmodule': BookBlogModule,
                        'commentmodule': CommentModule,
                        'usermodule': UserModule,
                        'umodule': UModule}
                    )
server = HTTPServer(app)
server.listen(mysettings.settings.get('port', 8888))
IOLoop.current().start()
