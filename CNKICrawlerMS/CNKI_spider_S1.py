# 解决方法1
# 获取论文时赋予ID，新增论文时进行检索判断

from bs4 import BeautifulSoup
from selenium import webdriver
import time
import requests
import urllib
import csv
import ddddocr
import pyautogui
from selenium.webdriver import ActionChains
from PIL import ImageGrab
import re
import pymysql

# 定义全局变量
global count
global img_count  # 当前验证码图片
global curr_page_num  # 当前的页数
global all_pages  # 所有可爬页数
global topic  # 当前主题
global academic_subjects  # 当前学科

count = 0
img_count = 0
curr_page_num = 0
all_pages = 0


# 进入知网首页并搜索关键词
def get_info():
    global topic  # 赋值当前主题
    global academic_subjects  # 赋值当前学科
    global img_count
    global curr_page_num
    global count

    url = "https://www.cnki.net/"
    key_word = "碳纳米管"
    driver = webdriver.Chrome('C:\Program Files\Google\Chrome\Application\chromedriver.exe')

    driver.get(url)  # 进入知网首页
    time.sleep(2)
    # 将关键词输入搜索框
    driver.find_element_by_css_selector('#txt_SearchText').send_keys(key_word)
    time.sleep(2)

    # 点击搜索按钮
    driver.find_element_by_css_selector(
        'body > div.wrapper.section1 > div.searchmain > div > div.input-box > input.search-btn').click()
    time.sleep(5)

    # 拿到返回结果
    content = driver.page_source.encode('utf-8')
    soup = BeautifulSoup(content, 'lxml')

    # 找到所有主题
    dd = soup.find_all('dd')
    dd_topic = BeautifulSoup(str(dd[1]), 'lxml')
    ul_topic = dd_topic.find_all('ul')

    for item in ul_topic:
        lis_topic = BeautifulSoup(str(item), 'lxml')
        lis_topic = lis_topic.find_all('li')
        li_count = 0
        for li in lis_topic:
            li_count += 1
            full_text = li.get_text()
            text = full_text.split("(")
            topic = text[0]  # 获取当前主题
            topic = "\"" + topic + "\""
            print(topic)
            # 选取第一个复选框点击
            ele0_path = '/html/body/div[3]/div[2]/div[1]/div[3]/dl[1]/dd[1]/div/ul[1]/li[{}]/input'.format(li_count)
            print(ele0_path)
            ele0 = driver.find_element_by_xpath(ele0_path)
            driver.execute_script("arguments[0].click();", ele0)
            time.sleep(2)

            # 针对于每一个主题，筛选对应的学科
            dd_subject = BeautifulSoup(str(dd[2]), 'lxml')
            ul_subject = dd_subject.find_all('ul')
            for item_subject in ul_subject:
                lis_subject = BeautifulSoup(str(item_subject), 'lxml')
                lis_subject = lis_subject.find_all('li')
                li_subject_count = 0
                for li_subject in lis_subject:
                    li_subject_count += 1
                    full_text = li_subject.get_text()
                    text = full_text.split("(")
                    academic_subjects = text[0]  # 获取当前学科
                    academic_subjects = "\"" + academic_subjects + "\""
                    print(academic_subjects)

                    # 选取复选框点击
                    ele1_path = '/html/body/div[3]/div[2]/div[1]/div[3]/dl[2]/dd/div/ul/li[{}]/input'.format(
                        li_subject_count)
                    print(ele1_path)
                    ele1 = driver.find_element_by_xpath(ele1_path)
                    driver.execute_script("arguments[0].click();", ele1)
                    # 等待加载
                    time.sleep(3)

                    # 重新解析
                    content = driver.page_source.encode('utf-8')
                    soup = BeautifulSoup(content, 'lxml')
                    get_page_info(driver, soup)

                    # 爬取数据
                    # BUG-2021120401 此处应当加以修改
                    '''
                    for pn in range(2, 300):
                        curr_page_num = pn
                        content = change_page(driver, pn)
                        get_page_info(driver, content)'''


# 获取当页的数据
def get_page_info(driver, soup):
    global img_count
    global curr_page_num
    global count
    global topic  # 当前主题
    global academic_subjects  # 当前学科

    # 连接数据库
    conn = pymysql.connect(host='127.0.0.1', user='root', passwd="884712", db='CNKI_data')
    cur = conn.cursor()
    # 文章处理
    tbody = soup.find_all('tbody')
    # 异常处理，解决验证码问题
    try:
        tbody = BeautifulSoup(str(tbody[0]), 'lxml')  # 解析
    except Exception:
        # 右键点击复制粘贴

        # 首先点击更换，避免重复调用方法的时候同一张照片一直识别不出来
        driver.find_element_by_xpath(
            "/html/body/div[3]/div[2]/div[2]/div[2]/div[1]/div[1]/img").click()
        time.sleep(1)
        path = "img"
        paths = path + "\\"
        logo = driver.find_element_by_xpath(
            "/html/body/div[3]/div[2]/div[2]/div[2]/div[1]/div[1]/img")
        rc = ActionChains(driver)
        rc.context_click(logo).perform()
        time.sleep(1)
        pyautogui.typewrite(['down', 'down', 'down'])
        time.sleep(1)
        pyautogui.press('enter')

        # 保存剪贴板里的图片
        time.sleep(1)
        image = ImageGrab.grabclipboard()  # 获取剪贴板文件
        time.sleep(2)
        image.save('{0}{1}.png'.format(paths, img_count))
        img_name = '{0}.png'.format(img_count)
        img_count += 1

        # 解析验证码
        ocr = ddddocr.DdddOcr()
        with open('img/' + img_name, 'rb') as f:
            img_bytes = f.read()
        res = ocr.classification(img_bytes)  # 解析结果
        # 验证
        time.sleep(1)
        driver.find_element_by_xpath(
            "/html/body/div[3]/div[2]/div[2]/div[2]/div[1]/div[1]/input").clear()
        time.sleep(1)
        driver.find_element_by_xpath(
            "/html/body/div[3]/div[2]/div[2]/div[2]/div[1]/div[1]/input").send_keys(res)
        time.sleep(1)
        driver.find_element_by_xpath(
            "/html/body/div[3]/div[2]/div[2]/div[2]/div[1]/div[2]/a").click()
        time.sleep(5)

        # 重新加载
        # 如果加载出错（验证码识别失败），循环测试
        content = driver.page_source.encode('utf-8')
        soup = BeautifulSoup(content, 'lxml')
        get_page_info(driver, soup)

    else:
        tr = tbody.find_all('tr')  # 获取tr标签，返回一个数组
        # 对每一个tr标签进行处理
        for item in tr:
            tr_bf = BeautifulSoup(str(item), 'lxml')

            # 获取论文标题
            td_name = tr_bf.find_all('td', class_='name')  # 拿到tr下的td
            td_name_bf = BeautifulSoup(str(td_name[0]), 'lxml')
            a_name = td_name_bf.find_all('a')
            href = a_name[0].get('href')

            # 获取论文的filename
            filename = get_filename(href)

            # get_text()是获取标签中的所有文本，包含其子标签中的文本
            title = a_name[0].get_text().strip()

            # 获取包含作者的那个td
            td_author = tr_bf.find_all('td', class_='author')
            td_author_bf = BeautifulSoup(str(td_author), 'lxml')

            # 每个a标签中都包含了一个作者名
            # BUG-2021120101 有些标签不包含 <a></a>，此处应该加以改进
            a_author = td_author_bf.find_all('a')

            # 拿到每一个标签里的作者名
            authors_name = ""
            for author in a_author:
                name = author.get_text().strip()  # 获取学者的名字
                authors_name = authors_name + name + " "

            # 获取来源
            td_source = tr_bf.find_all('td', class_='source')
            td_source_bf = BeautifulSoup(str(td_source), 'lxml')
            a_source = td_source_bf.find_all('a')
            # 有的来源无法通过超链接点击
            if len(a_source) == 0:
                td_source_bf = BeautifulSoup(str(td_source), 'lxml').find_all('td')
                source = td_source_bf[0].get_text().strip().split(" ")
            else:
                source = a_source[0].get_text().strip()

            # 获取时间
            td_date = tr_bf.find_all('td', class_='date')
            td_date_bf = BeautifulSoup(str(td_date), 'lxml').find_all('td')
            dates = td_date_bf[0].get_text().strip().split(" ")

            # 获取数据库
            td_data = tr_bf.find_all('td', class_='data')
            td_data_bf = BeautifulSoup(str(td_data), 'lxml').find_all('td')
            data = td_data_bf[0].get_text().strip()

            # 获取被引数量
            td_quote = tr_bf.find_all('td', class_='quote')
            td_quote_bf = BeautifulSoup(str(td_quote), 'lxml').find_all('td')
            quote = td_quote_bf[0].get_text().strip()
            if len(quote) == 0:
                quote = 0

            # 获取下载数量
            td_download = tr_bf.find_all('td', class_='download')
            td_download_bf = BeautifulSoup(str(td_download), 'lxml').find_all('td')
            download = td_download_bf[0].get_text().strip()
            if len(download) == 0:
                download = 0

            filename = "\"" + filename + "\""
            title = "\"" + title + "\""
            authors_name = "\"" + authors_name + "\""

            # 防止来源不是一个字符串而报错，很丑陋的处理方式
            try:
                source = "\"" + source + "\""
            except:
                sources = ""
                for i in source:
                    sources = i + sources + " "
                source = "\"" + sources + "\""

            dates[0] = "\"" + dates[0] + "\""
            data = "\"" + data + "\""

            # 写入数据库
            sql = "INSERT INTO papers (filename,title,academic_subjects,topic,paper_authors,source,date," \
                  "paper_database,quote_num,download_num) VALUES " \
                  "({},{},{},{},{},{},{},{},{},{});".format(
                filename, title, academic_subjects, topic, authors_name, source, dates[0], data, quote, download)
            cur.execute(sql)
            cur.connection.commit()
            global count
            count += 1
            print("已爬取第 " + str(count) + " 条")
        cur.close()
        conn.close()


# 换页
# pn表示当前要爬的页数
def change_page(driver, pn):
    driver.find_element_by_css_selector('#page' + str(pn)).click()
    time.sleep(5)
    content1 = driver.page_source.encode('utf-8')
    soup = BeautifulSoup(content1, 'lxml')
    return soup


# 获取文件的filename
# /KNS8/Detail/RedirectScholar?flag=TitleLink&tablename=GARBLAST&filename=SBRC41C6F634A2B5F3A329FB5EAD11CCABE4
# /KNS8/Detail?sfield=fn&QueryID=110&CurRec=20&recid=&FileName=FUHE202101004&DbName=CJFDLAST2021&DbCode=CJFD&yx=A&pr=&URLID=11.1801.TB.20200825.1841.008
def get_filename(href):
    str_filename = re.search(r'(.*)FileName=(.*)&?', href, re.M | re.I).group(2)
    filename = str_filename.split('&')[0]
    return filename


if __name__ == '__main__':
    get_info()
