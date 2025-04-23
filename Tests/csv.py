import re
from urllib import request


def login():

    username = request.values.get('username')
    password = request.values.get('password')

    db = pymysql.connect('127.0.0.1')

    username = re.sub('(union|select|from|where|or|and|%|_)', '', username, flag=re.I)
    password = re.sub('(union|select|from|where|or|and|%|_)', '', password, flag=re.I)
    cursor.execute("select * from users where username='%s' and password='%s'" % (username, password))