#!usr/bin/env python
# -*- coding:utf-8 _*-

""" 
@author:Administrator 
@file: meituan_selenium.py 
@time: 2018/11/{DAY} 
描述: 

"""
# !usr/bin/env python
# -*- coding:utf-8 _*-

""" 
@author:Administrator 
@file: amap_selenium_chrome.py 
@time: 2018/10/07
描述: selenium  MEITUAN chrome  采集小区边界

"""

import requests, re, time, os, random, json
from bs4 import BeautifulSoup
# 导入webdriver
import createNewDir
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from fake_useragent import UserAgent
# 要想调用键盘按键操作需要引入keys包
from selenium.webdriver.common.keys import Keys
from collections import OrderedDict
from itertools import combinations
import coordinateTranslate as ct


class GetMeituan():
    def __init__(self):
        # 查询城市code的url
        self.cityCodeUrl = 'https://www.meituan.com/ptapi/getprovincecityinfo/'
        # 保存城市code的文件名
        self.cityCodeFile = './cityCode.csv'
        self.ua = UserAgent()  # 初始化 随机'User-Agent' 方法
        self.userAnent = 'user-agent="' + self.ua.random + '"'
        print(self.userAnent)

        # 保存城市的列表
        self.cityList = []

        # 当前城市
        self.city = {}
        self.cityAcronym = ""

        # 保存分类的 列表
        self.cateList = []

        # 保存子区域的列表
        self.areaList = []

        # 当前需要采集的url 列表
        self.openUrlList = []

        # poi 相信信息的列表
        self.PoiInfos = []

        # # 保存的 csv文件 路径 和 文件名称
        # self.csvFile = createNewDir.createDir(r'../meituan') + self.cityAcronym + '.csv'
        # # 保存的 采集进度的 文件名
        # self.currFile = createNewDir.createDir(r'../meituan') + self.cityAcronym + '.dat'

        # 坐标系转换模块
        gps = ct.GPS()
        self.coordTrans = gps.gcj_decrypt_exact


    def seleniumChromeInit(self):

        # 模拟创建一个浏览器对象，然后可以通过对象去操作浏览器
        driverPath = r'../Chrome/Application/chromedriver.exe'
        self.downloadPath = r'C:\Users\Administrator\Downloads'
        # 浏览器驱动

        options = webdriver.ChromeOptions()
        prefs = {'profile.default_content_settings.popups': 0,
                 'download.default_directory': self.downloadPath,
                 'profile.managed_default_content_settings.images': 2    #无图模式
                 }
        options.add_experimental_option('prefs', prefs)
        # 更换头部
        options.add_argument(self.userAnent)
        print(self.userAnent)
        # options.add_argument("--no-sandbox")
        # options.add_argument('--headless')
        browserDriver = webdriver.Chrome(executable_path=driverPath, chrome_options=options)
        # browserDriver.maximize_window()     # 设置最大化
        # browserDriver.set_window_size(1366,900)
        self.browserDriver = browserDriver
        self.action = ActionChains(self.browserDriver)

    def isJsonStr(self, jsonStr):
        try:
            json.loads(jsonStr)
        except ValueError:
            return False
        return True

    def toJson(self, text):
        # 字符串 反序列化
        if self.isJsonStr(text):
            return json.loads(text)
        else:
            return None

    def getCtyCode(self, provinceName):
        # 打开amap 首页 等待网页加载完成
        url = self.cityCodeUrl
        self.browserDriver.get(url)
        # 暂停1秒，已达到完全模拟浏览器的效果
        time.sleep(1)
        # 等待加载完成
        preTag = WebDriverWait(self.browserDriver, 20).until(EC.presence_of_element_located((By.XPATH, "//pre")))
        resultJson = [cityCode for cityCode in self.toJson(preTag.text)]
        for city in resultJson:
            cityCodeList = city.get("cityInfoList", "")
            self.cityList = self.cityList + list(cityCodeList)

    def getCateCode(self):
        # 获取各种 美食分类
        url = "http://xa.meituan.com/meishi/b16010/"
        self.browserDriver.get(url)
        # 暂停1秒，已达到完全模拟浏览器的效果
        time.sleep(1)
        # 等待 <ul class='more clear'> 加载完成
        cateTags = WebDriverWait(self.browserDriver, 20).until(
            EC.presence_of_element_located((By.XPATH, "//ul[@class='more clear']")))

        cateTags = self.browserDriver.find_elements_by_xpath("//ul[@class='more clear']")

        # 获取 分类名称   获取美食分类连接
        liTags = cateTags[0].find_elements_by_tag_name("a")
        for li in liTags:
            name = li.text
            href = li.get_attribute("href")
            cateId = href.split(r"/")[-2].split("b")[0].replace("c", "")
            print(cateId, name)
            self.cateList.append({"id": cateId, "name": name})

        # 删除 名为 "代金卷" 的类别
        del self.cateList[0]


    def queryCityInfo(self, cityName):
        # 根据 城市名字查询 城市信息
        for city in self.cityList:
            if city.get("name", "") == cityName:
                self.city = city
                self.cityAcronym = city.get("acronym", "")
                # 保存的 csv文件 路径 和 文件名称
                self.csvFile = createNewDir.createDir('..\\meituan\\') + '\\' + self.cityAcronym + '_meituan.csv'
                # 保存的 采集进度的 文件名
                self.currFile = createNewDir.createDir('..\\meituan\\') + '\\' + self.cityAcronym + '_meituan.dat'
                return city
        return ""


    def getAreaCode(self, cityName, areaName):
        # 获取 子区域分类
        # 拼接城市 主页 url
        url = "http://" + self.queryCityInfo(cityName).get("acronym", "") + ".meituan.com/meishi/"
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

            if bName not in areaName:  # 过滤 一级行政区
                # 鼠标移动到 b 标签上
                webdriver.ActionChains(self.browserDriver).move_to_element(bTag).perform()
                areaTags = self.browserDriver.find_elements_by_xpath("//div[@class='popover-content']/ul//li//a")
                for a in areaTags:
                    name = a.text
                    if name == u"全部":
                        name = bName
                        id = a.get_attribute("href").split("/")[-2].replace("b", "")
                        self.areaList.append({"id": id, "name": name})
                        print({"id": id, "name": name})


    def createCityUrls(self):
        # 取 子分类id 和 子区域 id ,并拼接为url
        cateList = [id.get("id", "") for id in self.cateList]
        areaList = [id.get("id", "") for id in self.areaList]

        # 拼接 url
        for cateId in cateList:
            for areaId in areaList:
                hId = "".join(["c", cateId, "b", areaId])
                url = "http://" + self.cityAcronym + ".meituan.com/meishi/" + hId + "/"
                self.openUrlList.append(url)


    def readCurr(self):
        # 从文件读取采集进度
        if not os.path.exists(self.csvFile):
            with open(self.csvFile, mode='w', encoding='utf-8', errors='ignore') as f:
                f.write("poiCity, poiName, poiId, olon, olat, lon, lat, url, poiUrl, poiSource, poiComment, poiPrice, poiAddress" + '\n')

        if not os.path.exists(self.currFile):
            return 0

        with open(self.currFile, mode='r', encoding='utf-8', errors='ignore') as f:
            currUrl = f.readline()

        if currUrl in self.openUrlList :
            currUrlIndex = self.openUrlList.index(currUrl)
        else:
            currUrlIndex = 0

        return currUrlIndex



    def queryLoadCompalte(self, xpath):
        # 查询是否完成 返回 True
        resultHtml = None
        try:
            #  检测 返回结果为空的情况 "对不起，没有符合条件的商家 "class="list-ul"
            resultHtml = self.browserDriver.find_element_by_xpath(xpath)
        except Exception as  e:
            print(e)
            time.sleep(1)

        if resultHtml:
            return resultHtml
        else:
            return self.queryLoadCompalte(xpath)
            # 迭代本方法 直到加载完成...


    def oprnUrl(self,url):
        try:
            return self.browserDriver.get(url)
        except Exception as e:
            print(e)
            time.sleep(1)
            return self.oprnUrl(url)


    def getCoord(self,poiUrl):
        # 新标签中打开 poi的 详细信息页面

        # <span>地址：</span>
        htmlText = self.newTabGet(poiUrl,"//*[contains(text(), '地址：')]")

        # 正则表达式匹配经纬度
        try:
            lon = float(re.search(r'"longitude":[ ]*(.+?),',htmlText).group(1))
        except Exception as e:
            print("not found 'longitude'!")
            try:
                lon = float(re.search(r'"lng":[ ]*(.+?),', htmlText).group(1))
            except Exception as e:
                lon = 0
                print("not found 'lng'!")

        try:
            lat = float(re.search(r'"latitude":[ ]*(.+?),', htmlText).group(1))
        except Exception as e:
            print("not found 'latitude'!")
            try:
                lat = float(re.search(r'"lat":[ ]*(.+?),', htmlText).group(1))
            except Exception as e:
                lat = 0
                print("not found 'lat'!")

        return [lon,lat]
        # "longitude": 107.146922, "latitude": 34.371929
        # "lng":107.145204,"lat":34.371987,



    def newTabGet(self,url,xpath):
        js = " window.open('')"
        self.browserDriver.execute_script(js)
        # 可以看到是打开新的标签页 不是窗口
        window = self.browserDriver.window_handles
        # 获取窗口(标签)列表
        self.browserDriver.switch_to.window(window[1])
        # 切换到新标签
        self.oprnUrl(url)
        self.queryLoadCompalte(xpath)
        html = self.browserDriver.page_source

        self.browserDriver.close()
        self.browserDriver.switch_to.window(window[0])

        return html


    def getCityPois(self):
        # 并拼接url
        self.createCityUrls()

        # 读取采集进度
        currUrlIndex = self.readCurr()


        # 遍历每一个 需要采集的 url
        for url in self.openUrlList[currUrlIndex:-1]:
            print(url)
            self.oprnUrl(url)

            # 等待   ""//div[@class='list']"" 元素载入完成
            if self.queryLoadCompalte("//div[@class='list']"):
                #  检测 返回结果为空的情况 "对不起，没有符合条件的商家 "class="list-ul"
                try:
                    # 等待 <ul class='list-ul'> 标签加载完成
                    ulTags = WebDriverWait(self.browserDriver, 5).until(
                        EC.presence_of_element_located((By.XPATH, "//ul[@class='list-ul']")))
                except Exception as e:
                    print(u"对不起，没有符合条件的商家")
                    continue


            # 最后一页标志
            isLastPage = False
            while not isLastPage:
                # a 标签
                aTags = self.browserDriver.find_elements_by_xpath("//ul[@class='list-ul']/li/div[@class='info']/a")

                #  遍历每一个 poi
                poiInfo = []
                poiInfos = []
                for a in aTags:
                    poiUrl = a.get_attribute("href")
                    poiId = poiUrl.split("/")[-2]
                    poiName = a.find_element_by_tag_name("h4").text.replace(",","")
                    poiCity = self.city.get("name","")

                    poiComment = a.find_elements_by_xpath("..//div[@class='source clear']/p")[0].text
                    poiSource, poiComment = poiComment.split(u"分")
                    if poiComment is '': poiComment = u'0条评论'

                    poiAddress = a.find_elements_by_xpath("..//p[@class='desc']")[0].text
                    poiAddress, poiPrice = poiAddress.split('\n')
                    poiAddress.replace(",","")

                    olon,olat = self.getCoord(poiUrl)
                    coordination = self.coordTrans(olat,olon)  # 坐标系转换
                    lon,lat = [str(coordination.get("lon","")),str(coordination.get("lat",""))]

                    poiInfo = [poiCity, poiName, poiId, str(olon), str(olat), lon, lat, url,poiUrl, poiSource, poiComment, poiPrice, poiAddress+'\n']
                    print(poiInfo)
                    poiInfos.append(",".join(poiInfo))
                    # self.poiInfos.append(list(poiInfo))

                with open(self.csvFile, mode='a+', encoding='utf-8', errors='ignore') as f:  # 将poi信息写入文件
                    f.writelines(poiInfos)

                with open(self.currFile, mode='w', encoding='utf-8', errors='ignore') as f:  # 将采集进度写入文件
                    f.write(url)

                isLastPageTag = self.browserDriver.find_elements_by_xpath("//ul[@class='pagination clear']/li")
                isLastPageTag = isLastPageTag[-1].find_element_by_tag_name("span")
                if "disabled" in isLastPageTag.get_attribute("class"):
                    isLastPage = True
                else:
                    isLastPage = False
                    isLastPageTag.click()
                    print("Next page Click !!!")
                    self.queryLoadCompalte("//ul[@class='list-ul']")


    def getCookie(self):
        # 打开amap 首页 等待网页加载完成
        url = "http://xa.meituan.com/meishi/c57b116/"
        self.browserDriver.get(url)
        # 暂停1秒，已达到完全模拟浏览器的效果
        time.sleep(2)
        # 等待加载完成
        # preTag = self.browserDriver.find_element_by_xpath("//*[@class='list']")
        cookies = self.browserDriver.get_cookies()
        print(cookies)
        return cookies


    def webLoadComplate(self, browserDriver, id):
        # 等到id 元素载入完成 返回该元素
        try:
            # 等待到 元素载入完成  元素 出现
            element = WebDriverWait(browserDriver, 20).until(EC.presence_of_element_located((By.ID, id)))
        except Exception as e:
            print(e)
            time.sleep(1)
            return self.webLoadComplate(browserDriver, id)
            # 迭代本方法 直到加载完成...
        return element



if __name__ == "__main__":
    meituan = GetMeituan()
    # 初始化selenium Chrome 对象
    browserDriver = meituan.seleniumChromeInit()

    # 获取所有城市id
    meituan.getCtyCode(u"陕西")

    # 获取分类ID
    meituan.getCateCode()

    # 获取子区域id
    meituan.getAreaCode(u"西安",[u"陈s区"])

    # 获取poi
    meituan.getCityPois()

    print("complate!")
