import urllib.request as ur
import urllib.parse as urlaa
import json
from bs4 import BeautifulSoup
import re
import pymysql

connect = pymysql.Connect(
    host='119.80.187.10',
    port=3307,
    user='xuehz',
    passwd='xuehz',
    charset='utf8',
    database='xuehz_data'
)
if connect:
    print('链接成功')
cursor = connect.cursor()


def create_table_db():
    sql = "create table if not exists tank_python_one(id INT primary key not null auto_increment ,title   VARCHAR(100),url VARCHAR (100),images VARCHAR (1000))"
    cursor.execute(sql)


def get_page_index(offset,keyword):
    data = {
        'offset': offset,
        'format': 'json',
        'keyword': keyword,
        'autoload': 'true',
        'count': '20',
        'cur_tab': '1'
    }

    try:
        url = 'http://www.toutiao.com/search_content/?offset=0&format=json&keyword=%E4%B8%89%E9%87%8C%E5%B1%AF%E8%A1%97%E6%8B%8D&autoload=true&count=20&cur_tab=1' + urlaa.urlencode(data)
        reponse = ur.urlopen(url)
        text = reponse.read()
        text = text.decode('utf-8')
        return text
    except BaseException as e:
        print(e)
    finally:
        print()


def parse_page_index(html):
    data = json.loads(html)
    if data and 'data' in data.keys():
        for item in data['data']:
            yield item['article_url']


def get_page_detail(url):
    try:
        response = ur.urlopen(url)
        text = response.read()

        return text.decode('utf-8')
    except BaseException as e:
        print(e)


def parse_page_detail(html,url):
    soup = BeautifulSoup(html,'html.parser')
    title = soup.select('title')[0].get_text()
    #正则表达式对象
    images_pattern = re.compile(r'var gallery = (.*?);', re.S)
    result = re.search(images_pattern, html)
    if result:
        data = json.loads(result.group(1))
        if data and 'sub_images' in data.keys():
            sub_images = data['sub_images']
            images = [item.get('url') for item in sub_images]
            return {
                'title': title,
                'url': url,
                'images': images
            }


def save_info_sql(info, num):
    sql = "insert into tank_python_one(title, url, images) VALUES(%s, %s, %s)"
    images_str = ','.join(str(i) for i in info['images'])
    data = (info['title'], info['url'], images_str)
    cursor.execute(sql, data)
    connect.commit()
    print('成功插入', cursor.rowcount, '条数据')
    save_file(info['title'], info['images'], num)


def save_file(filename,images,num):
    # 保存到本地
    temp = 0
    for url in images:
        pathname = '/Users/MyMac/Desktop/图片/%sx%sy%s.jpg' % (filename, num, temp)
        ur.urlretrieve(url, pathname)
        temp += 1
        print(pathname + '保存成功')


def main():
    html = get_page_index(0, '李嘉欣')
    create_table_db()
    x = 0
    for url in parse_page_index(html):
        html = get_page_detail(url)
        if html:
            result = parse_page_detail(html, url)
            # print(result)
            if result:
                save_info_sql(result, x)
                x += 1

if __name__ == '__main__':
    main()