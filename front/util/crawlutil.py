import multiprocessing
from urllib import request
from urllib import error
from urllib import parse
import random
import time
import logging
import re
import json
import pymysql
from configuration.mysettings import settings
import gevent
import threading


logger = logging.getLogger("crawlLog")

formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')

file_handler = logging.FileHandler('crawlLog.log')
file_handler.setFormatter(formatter)


logger.setLevel(logging.INFO)
dbsetting = settings['dbsetting']
conection = pymysql.connect(host=dbsetting.get('host', '127.0.0.1'),
                            port=dbsetting.get('port', 3306),
                            user=dbsetting.get('user', 'root'),
                            password=dbsetting.get('password', '123456'),
                            database=dbsetting.get(
    'database', 'mindreaddb'),
    charset=dbsetting.get('charset', 'utf8'))
if conection:
    cursor = conection.cursor()


def downloadHtml(url, headers=[], proxy={},
                 timeout=None,
                 decodeInfo="utf-8",
                 num_retries=5):

    if random.randint(1, 10) >= 6:
        proxy = None

    proxy_support = request.ProxyHandler(proxy)
    opener = request.build_opener(proxy_support)
    if proxy:
        opener = request.build_opener(proxy_support)
    opener.addheaders = headers
    request.install_opener(opener)

    html = None
    try:
        res = request.urlopen(url)
        html = res.read().decode(decodeInfo)
    except UnicodeDecodeError as e:
        print(e)
    except error.URLError or error.HTTPError as e:
        if num_retries > 0:
            time.sleep(random.randint(1, 3))
            if hasattr(e, 'code') and 500 <= e.code < 600:
                html = downloadHtml(url,
                                    headers,
                                    proxy,
                                    timeout,
                                    decodeInfo,
                                    num_retries - 1)
    return html


headers = [("User-Agent", "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36"),
           ("Accept", "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8"),
           ("Accept-Language", "zh-CN,zh;q=0.9"),
           ("Connection", 'keep-alive'),
           ("Host", "book.douban.com")]


def saveImg(url, filename):
    # 把图片下载到本地
    data = request.urlopen(url).read()
    with open('statics/images/' + filename, "wb") as f:
        f.write(data)


def formatbookinfo(html):
    pattern = re.compile(
        r'<span class="pl">\s*([\w\W]{0,16}?):?</span>\s*([\w\W]{0,256}?)\s*<br/?>')
    infos = re.findall(pattern, html)
    print(infos)
    pattern = re.compile(r'<div class="intro">\s*<p>([\w\W]*?)</p></div>')
    if re.findall(pattern, html):
        brief = re.findall(pattern, html)[0]
    else:
        brief = None
    book = dict(
        title=None,
        author=None,
        press=None,
        subtitle=None,
        orititle=None,
        translator=None,
        date=None,
        price=None,
        ISBN=None,
        brief=brief,
        img=None)
    pattern = re.compile(r'">([\w\W]*?)</a>')
    for info in infos:
        sym = info[0][:2]
        if sym == '作者':
            book["author"] = '/ '.join([i
                                        for i in re.findall(pattern, info[1])])
        elif info[0][:3] == '出版社':
            book['press'] = info[1]
        elif sym == '副标':
            book['subtitle'] = info[1]
        elif sym == '原作':
            book['orititle'] = info[1]
        elif sym == '译者':
            book['translator'] = '/ '.join([i
                                            for i in re.findall(pattern, info[1])])
        elif info[0][:3] == '出版年':
            book['date'] = info[1]
        elif sym == '定价':
            book['price'] = info[1]
        elif sym == 'IS':
            book['ISBN'] = info[1]

    pattern = re.compile(r'<a class="nbg"\s* href="([\w\W]*?)\s*"')
    img_url = re.findall(pattern, html)[0]
    if book['ISBN']:
        book['img'] = book['ISBN'] + '.' + img_url.split('.')[-1]
        saveImg(img_url, book['img'])

    pattern = re.compile('/tag/([\w\W]*?)"')
    tags = re.findall(pattern, html)
    return book, tags


def insertBook(book):
    sql = 'insert into tb_book(book_title, book_author, book_press, ' \
          'book_subtitle, book_orititle, book_translator, book_date, ' \
          'book_price, book_ISBN, book_brief, book_img) values(%s, %s, %s, %s' \
          ', %s, %s, %s, %s, %s, %s, %s )'
    params = (book['title'], book['author'], book['press'], book['subtitle'],
              book['orititle'], book['translator'], book['date'], book['price'],
              book['ISBN'], book['brief'], book['img'])
    try:
        cursor.execute(sql, params)
        cursor.connection.commit()
    except Exception as e:
        print('错误信息', e)


def bookExistbyTitle(title):
    sql = 'select count(*) from tb_book where book_title = %s'
    params = (title)
    cursor.execute(sql, params)
    result = cursor.fetchone()[0]
    return result


def insertTag(tag, ISBN):
    sql = 'select count(*) from tb_tag where tag_name = %s'
    params = (tag,)
    cursor.execute(sql, params)
    cursor.connection.commit()
    result = cursor.fetchone()
    if not result[0]:
        sql = 'insert into tb_tag(tag_name) values (%s)'
        params = (tag,)
        try:
            cursor.execute(sql, params)
            cursor.connection.commit()
        except Exception as e:
            print('错误信息', e)
    cursor.execute('select tag_id from tb_tag where tag_name = %s', (tag,))
    tag_id = cursor.fetchone()[0]
    sql = 'insert into tb_book_tag(book_tag_book_ISBN, book_tag_tag_id) ' \
          'values (%s, %s)'
    params = (ISBN, tag_id)
    try:
        cursor.execute(sql, params)
        cursor.connection.commit()
    except Exception as e:
        print('错误信息', e)


lock = threading.Lock()


def addbook(url, title):
    logger.addHandler(file_handler)
    html = downloadHtml(url, headers=headers)
    if html:
        book, tags = formatbookinfo(html)
        logger.info('Add Book ' + str(book) + '\nand Add Tags ' + str(tags))
        book['title'] = title
        with lock:
            insertBook(book)
            for tag in tags:
                insertTag(tag, book['ISBN'])
    else:
        logger.error("downloadHtml fail")
    logger.removeHandler(file_handler)


def crawlbyWord(q):
    while True:
        word = q.get()
        url = 'https://book.douban.com/j/subject_suggest?q=' + \
            parse.quote(word)
        html = downloadHtml(url, headers=headers)
        if html:
            booklist = json.loads(html)
            jobs = []
            for book in booklist:
                if not bookExistbyTitle(book['title']):
                    job = gevent.spawn(addbook, book['url'], book['title'])
                    # addbook(book['url'], book['title'])
                    jobs.append(job)
            if jobs:
                gevent.joinall(jobs)
        else:
            print('downloadHtml fail')
