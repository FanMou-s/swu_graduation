from bs4 import BeautifulSoup
from selenium import webdriver
import urllib
import ddddocr
import time
import pyautogui
from selenium.webdriver import ActionChains
from PyQt5.QtWidgets import QApplication
from PIL import Image
from PIL import ImageGrab




# 进入知网首页并搜索关键词
def get_info(driver, key_word):
    url = "file:///C:/Users/asus/Desktop/%E6%AF%95%E4%B8%9A%E8%AE%BA%E6%96%87/%E6%A3%80%E7%B4%A2-%E4%B8%AD%E5%9B%BD%E7%9F%A5%E7%BD%91.html"
    driver.get(url)  # 进入知网首页
    # 拿到返回结果
    content = driver.page_source.encode('utf-8')
    soup = BeautifulSoup(content, 'lxml')
    return soup

def get_page_info(driver, soup):
    global img_count
    img_count = 0
    # 文章处理
    tbody = soup.find_all('tbody')
    # 异常处理，解决验证码问题
    try:
        tbody = BeautifulSoup(str(tbody[0]), 'lxml')  # 解析
    except Exception:
        # 获取验证码的图片
        path = "img"
        paths = path + "\\"
        pic = soup.find_all('img', title="点击切换验证码")
        link = pic[0].get('src')  # 得到地址
        link = "file:///C:/Users/asus/Desktop/毕业论文/检索-中国知网_files/VerifyCode"
        urllib.request.urlretrieve(link, '{0}{1}.png'.format(paths, img_count))
        img_name = '{0}.png'.format(img_count)

        logo = driver.find_element_by_xpath(
            "/html/body/div[3]/div[2]/div[2]/div[2]/div[1]/div[1]/img")
        rc = ActionChains(driver)
        rc.context_click(logo).perform()
        time.sleep(1)
        pyautogui.typewrite(['down', 'down', 'down'])
        time.sleep(1)
        pyautogui.typewrite(['enter'])

        # 保存剪贴板里的图片
        image = ImageGrab.grabclipboard()  # 获取剪贴板文件
        image.save('img/test.png')

        img_count += 1
        # 解析验证码

        ocr = ddddocr.DdddOcr()
        with open('img/' + img_name, 'rb') as f:
            img_bytes = f.read()
        res = ocr.classification(img_bytes)  # 解析结果
        # 验证
        driver.find_element_by_xpath(
            "/html/body/div[3]/div[2]/div[2]/div[2]/div[1]/div[1]/input").send_keys(res)
        time.sleep(2)
        # /html/body/div[3]/div[2]/div[2]/div[2]/div[1]/div[2]/a
        driver.find_element_by_xpath(
            "/html/body/div[3]/div[2]/div[2]/div[2]/div[1]/div[2]/a").click()
        time.sleep(2)
        # tbody = BeautifulSoup(str(tbody[0]), 'lxml')  # 解析


if __name__ == '__main__':
    global img_count
    driver = webdriver.Chrome('C:\Program Files\Google\Chrome\Application\chromedriver.exe')
    soup = get_info(driver, '知识图谱')
    get_page_info(driver, soup)
    driver.close()