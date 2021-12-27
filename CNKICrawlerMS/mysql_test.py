#  测试mysql连接

import pymysql
conn = pymysql.connect(host='127.0.0.1', user='root', passwd="884712", db='world')
cur = conn.cursor()
cur.execute("SELECT Name FROM city WHERE District = 'England'")
for r in cur:
    print(r)
cur.close()
conn.close()

