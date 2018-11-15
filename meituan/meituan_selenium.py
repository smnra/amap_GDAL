#!usr/bin/env python  
#-*- coding:utf-8 _*-  

""" 
@author:Administrator 
@file: meituan_selenium.py 
@time: 2018/11/{DAY} 
描述: 

"""
#!usr/bin/env python
#-*- coding:utf-8 _*-

""" 
@author:Administrator 
@file: amap_selenium_chrome.py 
@time: 2018/10/07
描述: selenium  高德地图 chrome  采集小区边界

"""


import requests,re,time,os, random,json
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
from collections import OrderedDict

class GetMeituan():
    def __init__(self):
        # 查询城市code的url
        self.cityCodeUrl = 'https://www.meituan.com/ptapi/getprovincecityinfo/'
        # 保存城市code的文件名
        self.cityCodeFile = './cityCode.csv'
        self.ua = UserAgent()  # 初始化 随机'User-Agent' 方法
        self.userAnent =  'user-agent="'+ self.ua.random + '"'
        print(self.userAnent)

        # 保存城市的列表
        self.cityList = []

        # 保存分类的 列表
        self.cateList = []

        # 保存子区域的列表
        self.areaList = []


    def seleniumChromeInit(self):

        # 模拟创建一个浏览器对象，然后可以通过对象去操作浏览器
        driverPath = r'../Chrome/Application/chromedriver.exe'
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

    def isJsonStr(self,jsonStr):
        try:
            json.loads(jsonStr)
        except ValueError:
            return False
        return True

    def toJson(self,text):
        # 字符串 反序列化
        if self.isJsonStr(text):
            return json.loads(text)

    def getCtyCode(self,provinceName):
        # 打开amap 首页 等待网页加载完成
        url = self.cityCodeUrl
        self.browserDriver.get(url)
        # 暂停1秒，已达到完全模拟浏览器的效果
        time.sleep(1)
        #等待加载完成
        preTag = WebDriverWait(self.browserDriver, 20).until(EC.presence_of_element_located((By.XPATH,"//pre")))
        resultJson = [cityCode for cityCode in self.toJson(preTag.text)]
        for city in resultJson:
            cityCodeList = city.get("cityInfoList","")
            self.cityList = self.cityList + list(cityCodeList)


    def getCateCode(self):
        # 获取各种 美食分类
        url = "http://xa.meituan.com/meishi/b16010/"
        self.browserDriver.get(url)
        # 暂停1秒，已达到完全模拟浏览器的效果
        time.sleep(1)
        #等待 <ul class='more clear'> 加载完成
        cateTags = WebDriverWait(self.browserDriver, 20).until(
            EC.presence_of_element_located((By.XPATH, "//ul[@class='more clear']")))

        cateTags = self.browserDriver.find_elements_by_xpath("//ul[@class='more clear']")

        # 获取 分类名称   获取美食分类连接
        liTags = cateTags[0].find_elements_by_tag_name("a")
        for li in liTags:
            name = li.text
            href = li.get_attribute("href")
            cateId = href.split(r"/")[-2].split("b")[0].replace("c","")
            print(cateId,name)
            self.cateList.append({"id": cateId, "name": name})

    def queryCityInfo(self,cityName):
        # 根据 城市名字查询 城市信息
        for city in self.cityList:
            if city.get("name","")==cityName:
                return city
        return ""


    def getAreaCode(self,cityName):
        # 获取 子区域分类

        # 拼接城市 主页 url
        url = "http://" + self.queryCityInfo(cityName).get("acronym","") + ".meituan.com/meishi/"
        self.browserDriver.get(url)
        time.sleep(1)

        # 等待 <ul class='more clear'> 加载完成
        cateTags = WebDriverWait(self.browserDriver, 20).until(
            EC.presence_of_element_located((By.XPATH, "//ul[@class='more clear']")))
        cateTags = self.browserDriver.find_elements_by_xpath("//ul[@class='more clear']")[1]

        # 获取 一级行政区 元素 , 遍历b 标签
        bTags = self.browserDriver.find_elements_by_xpath("//ul[@class='more clear']//b")
        for bTag in bTags:
            bName = bTag.text

            # 鼠标移动到 b 标签上
            webdriver.ActionChains(self.browserDriver).move_to_element(bTag).perform()
            areaTags = self.browserDriver.find_elements_by_xpath("//div[@class='popover-content']/ul//li//a")
            for a in areaTags:
                name = a.text
                if name=="全部":
                    name=bName
                id = a.get_attribute("href").split("/")[-2].replace("b","")
                self.areaList.append({"id": id, "name": name})
                print({"id": id, "name": name})





    def getCookie(self):
        # 打开amap 首页 等待网页加载完成
        url = "http://xa.meituan.com/meishi/c57b116/"
        self.browserDriver.get(url)
        # 暂停1秒，已达到完全模拟浏览器的效果
        time.sleep(2)
        #等待加载完成
        # preTag = self.browserDriver.find_element_by_xpath("//*[@class='list']")
        cookies = self.browserDriver.get_cookies()
        print(cookies)
        return  cookies




    def getPois(self):
        # 打开amap 首页 等待网页加载完成
        url = "https://meishi.meituan.com/i/?ci=42&stid_b=0#"
        self.browserDriver.get(url)
        # 暂停1秒，已达到完全模拟浏览器的效果
        time.sleep(2)
        #等待加载完成
        preTag = WebDriverWait(self.browserDriver, 20).until(EC.presence_of_element_located((By.XPATH,"//span[@class='active']")))
        preTag = self.browserDriver.find_element_by_xpath("//*[@class='list']")
        cookies = self.browserDriver.get_cookies()
        headers = self.browserDriver.he
        print(cookies)
        return  cookies




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






if __name__=="__main__":
    meituan = GetMeituan()
    # 初始化selenium Chrome 对象
    browserDriver = meituan.seleniumChromeInit()

    # 获取所有城市id
    meituan.getCtyCode("陕西")

    # 获取分类ID
    meituan.getCateCode()

    # 获取子区域id
    meituan.getAreaCode("宝鸡")
    
    meituan.getPois()
    print("complate!")