#!usr/bin/env python  
#-*- coding:utf-8 _*-  

""" 
@author:Administrator 
@file: amap_selenium_chrome.py 
@time: 2018/10/07
描述: selenium  高德地图 chrome  采集小区边界

"""


import requests,re,time,os, random
from bs4  import BeautifulSoup
#导入webdriver
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver import ActionChains
from selenium.webdriver.support import  expected_conditions as EC
from fake_useragent import UserAgent
#要想调用键盘按键操作需要引入keys包
from selenium.webdriver.common.keys import Keys


class GetAmap():
    def __init__(self,fileName):
        self.url = 'https://www.amap.com/'
        self.url = 'https://www.amap.com/search?query=%E9%94%A6%E4%B8%9A6%E5%8F%B7%E5%BA%9C%E9%82%B8&city=610100&geoobj=109.194934%7C34.646429%7C109.200103%7C34.652162&zoom=17'
        self.geoUrl = 'https://www.amap.com/search?query=%E9%94%A6%E4%B8%9A6%E5%8F%B7%E5%BA%9C%E9%82%B8&city=610100&geoobj=109.194934%7C34.646429%7C109.200103%7C34.652162&zoom=17'
        # 查询边界的url
        self.fileName = fileName
        self.ua = UserAgent()  # 初始化 随机'User-Agent' 方法
        self.userAnent =  'user-agent="'+ self.ua.random + '"'
        print(self.userAnent)
    def seleniumChromeInit(self):

        # 模拟创建一个浏览器对象，然后可以通过对象去操作浏览器
        driverPath = r'./Chrome/Application/chromedriver.exe'
        self.downloadPath = r'C:\Users\Administrator\Downloads'
        # 浏览器驱动



        options = webdriver.ChromeOptions()
        prefs = {'profile.default_content_settings.popups': 0, 'download.default_directory': self.downloadPath}
        options.add_experimental_option('prefs', prefs)
        # 更换头部
        options.add_argument(self.userAnent)
        print(self.userAnent)
        #options.add_argument("--no-sandbox")
        # options.add_argument('--headless')
        browserDriver = webdriver.Chrome(executable_path=driverPath, chrome_options=options)
        # browserDriver.maximize_window()     # 设置最大化
        # browserDriver.set_window_size(1366,900)
        self.browserDriver = browserDriver
        self.action = ActionChains(self.browserDriver)
        return browserDriver
        browserDriver.close()



    def openAmap(self,browserDriver):
        # 打开amap 首页 等待网页加载完成
        # self.url = 'https://www.amap.com/'
        browserDriver.get(self.url)
        # 暂停2秒，已达到完全模拟浏览器的效果
        time.sleep(2)
        #等待 searchipt 加载完成
        searchBox = self.webLoadComplate(browserDriver, "searchipt")
        return browserDriver

    def webLoadComplate(self,browserDriver,id):
        # 等到id 元素载入完成 返回该元素
        try:
            # 等待到 元素载入完成  元素 出现
            element = WebDriverWait(browserDriver, 20).until(EC.presence_of_element_located((By.ID, id)))
        except Exception as e:
            print(e)
            time.sleep(1)
            return self.webLoadComplate(browserDriver,id)
            # 迭代本方法 直到加载完成...
        return element


    def searchAmap(self,browserDriver,word):
        searchBox = browserDriver.find_element_by_id('searchipt')
        # 查找搜索框
        if searchBox:
            searchBox.send_keys(word)
            searchBox.send_keys(Keys.RETURN)
            return True
        else:
            print("未找到搜索框,id:",word)
            return False


    def authSlideAmap(self,browserDriver):
        #等待 iframe 加载完成
        iframeTag = self.webLoadComplate(browserDriver, "sufei-dialog-content")
        # 切换到 ifream
        browserDriver.switch_to.frame('sufei-dialog-content')

        # 等待 ifream 的 id:nc_1_n1z 的 元素加载完成
        iframeTag = self.webLoadComplate(browserDriver, "nc_1_n1z")
        # 请按住滑块，拖动到最右边
        element =browserDriver.find_element_by_xpath("//*[@id='nc_1_n1z']")
        time.sleep(2.15)
        if element:
            print("第一步,点击元素")
            ActionChains(browserDriver).click_and_hold(on_element=element).perform()
            time.sleep(0.15)
            print("第二步，拖动元素")
            x = 0
            y = 1
            while x<= 200:
                try:
                    element = browserDriver.find_element_by_xpath("//*[@id='nc_1_n1z']")
                except Exception as e:
                    print("Error, nc_1_n1z 元素不存在!!!")
                    element = None
                if element:
                    x = x+10
                    ActionChains(browserDriver).move_to_element_with_offset(to_element=element, xoffset=x,yoffset=y*(-1)).perform()
                    print(x,y)
                    time.sleep(random.randint(10, 50) / 100)
                else:
                    print("Error!!!")
                    break
            print("第三步，释放鼠标")
            # 释放鼠标
            ActionChains(browserDriver).release(on_element=element).perform()
            time.sleep(3)

        # 切换到默认的ifream
        browserDriver.switch_to.default_content()




    def main(self):
        browserDriver = self.seleniumChromeInit()
        # 初始化selenium Chrome 对象
        browserDriver = self.openAmap(browserDriver)
        # 打开amap首页
        if self.searchAmap(browserDriver, "安康学院"):
            print(browserDriver.title)

        self.authSlideAmap(browserDriver)



if __name__=="__main__":
    amap = GetAmap("./build.csv")
    amap.main()
    print("complate!")