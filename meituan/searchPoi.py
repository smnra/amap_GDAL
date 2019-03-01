#!usr/bin/env python  
# -*- coding:utf-8 _*-

""" 
@Author: SMnRa 
@Email: smnra@163.com
@Project: amap_GDAL
@File: searchPoi.py 
@Time: 2019/02/25 13:39

功能描述: 




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
from bs4 import BeautifulSoup


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
        # #保存URL列表的文件
        # self.urlFile = createNewDir.createDir(r'../meituan_url_') + self.cityAcronym + '.csv'

        # 坐标系转换模块
        gps = ct.GPS()
        self.coordTrans = gps.gcj_decrypt_exact

        self.citySearchUrl = {
            '西安市': 'https://xa.meituan.com/s/',
            '宝鸡市': 'https://baoji.meituan.com/s/',
            '咸阳市': 'https://xianyang.meituan.com/s/',
            '榆林市': 'https://yl.meituan.com/s/',
            '延安市': 'https://yanan.meituan.com/s/',
            u'汉中市': 'https://hanzhong.meituan.com/s/',
            '铜川市': 'https://tc.meituan.com/s/',
            '商洛市': 'https://sl.meituan.com/s/',
            '渭南市': 'https://wn.meituan.com/s/',
            '安康市': 'https://ankang.meituan.com/s/'
        }

    def seleniumChromeInit(self):
        # 模拟创建一个浏览器对象，然后可以通过对象去操作浏览器
        driverPath = r'../Chrome/Application/chromedriver.exe'
        self.downloadPath = r'C:\Users\Administrator\Downloads'
        # 浏览器驱动

        options = webdriver.ChromeOptions()
        prefs = {'profile.default_content_settings.popups': 0,
                 'download.default_directory': self.downloadPath,
                 'profile.managed_default_content_settings.images': 2  # 无图模式
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
        # 是否是 JSON 字符串
        try:
            json.loads(jsonStr)
        except ValueError:
            return False
        return True

    def toJson(self, text):
        # 字符串 反序列化
        if self.isJsonStr(text):
            return json.loads(text)

    def readCurr(self):
        # 从文件读取采集进度
        if not os.path.exists(r'./searchPoi.csv'):
            with open(r'./searchPoi.csv', mode='w', encoding='utf-8', errors='ignore') as f:
                f.write(
                    "searchCity,searchName, searchID, " + "poiCity, poiName, poiId, poiType, poiArea, olon, olat, lon, lat, url, poiUrl, poiSource, poiComment, poiPrice, poiAddress" + '\n')

        if not os.path.exists(r'./searchPoi.dat'):
            return 0

        with open(r'./searchPoi.dat', mode='r', encoding='utf-8', errors='ignore') as f:
            currUrl = f.readline()

        if currUrl in self.poiSearch:
            currUrlIndex = self.poiSearch.index(currUrl)
        else:
            currUrlIndex = 0

        return currUrlIndex

    def queryLoadCompalte(self, xpath):
        # 查询是元素否完成 返回 True
        resultHtml = None
        try:
            resultHtml = self.browserDriver.find_element_by_xpath(xpath)
        except Exception as  e:
            print(e)
            time.sleep(0.1)

        if resultHtml:
            return resultHtml
        else:
            return self.queryLoadCompalte(xpath)
            # 迭代本方法 直到加载完成...

    def oprnUrl(self, url):
        # chrome 新标签打开URL
        try:
            return self.browserDriver.get(url)
        except Exception as e:
            print(e)
            time.sleep(0.1)
            return self.oprnUrl(url)

    def readUrlList(self, filePath):
        if not os.path.exists(filePath):
            return False
        else:
            with open(filePath, mode='r', encoding='utf-8', errors='ignore') as f:
                # 从 urlFile 字符串的文件路径读取url列表
                self.poiSearch = f.readlines()
            return self.poiSearch

    def getSearchUrl(self, city, name):
        url = self.citySearchUrl[city] + name
        return url

    def getSearchPois(self):
        #
        self.poiSearch = self.readUrlList(r'./poiSearchName.txt')
        currUrlIndex = self.readCurr()  # 读取进度

        # 遍历每一个 需要采集的 url
        for searchName in self.poiSearch[currUrlIndex:-1]:
            searchList = searchName.replace("\n", "").split(",")
            url = self.getSearchUrl(searchList[0], searchList[1])
            print(url)
            self.oprnUrl(url)

            # 等待   ""//div[@class='list']"" 元素载入完成
            if self.queryLoadCompalte("//div[@class='common-list']"):
                #  检测 返回结果为空的情况 "对不起，没有符合条件的商家 "class="list-ul"
                try:
                    # 等待 <div class='common-list-main'> 标签加载完成
                    ulTags = WebDriverWait(self.browserDriver, 5).until(
                        EC.presence_of_element_located((By.XPATH, "//*[@class='common-list-main']")))
                except Exception as e:
                    print(u"对不起，没有符合条件的商家")
                    continue

            # 最后一页标志
            isLastPage = False
            while not isLastPage:
                # a 标签
                aTags = self.browserDriver.find_elements_by_xpath("//div[@class='list-item-desc-top']")

                #  遍历每一个 poi
                poiInfo = []
                poiInfos = []
                for div in aTags:
                    a = div.find_element_by_tag_name('a')
                    poiUrl = a.get_attribute("href")
                    poiId = poiUrl.split("/")[-2]
                    poiName = a.text

                    poiCityDiv = self.browserDriver.find_elements_by_xpath("//span[@class='current-city']")
                    poiCity = poiCityDiv[0].text

                    commentDiv = div.find_elements_by_xpath("./div[@class='item-eval-info clearfix']/span")
                    if commentDiv[0].text == '暂无评分':
                        poiComment = commentDiv[1].text
                        poiSource = commentDiv[0].text
                    else:
                        poiComment = commentDiv[2].text
                        poiSource = commentDiv[1].text

                    addressDiv = div.find_elements_by_xpath("./div[@class='item-site-info clearfix']/div")[0]
                    addressSpan = addressDiv.find_elements_by_xpath("./span")
                    poiAddress = addressSpan[1].text

                    try:
                        poiType, poiArea = addressSpan[0].text.split("|")
                    except Exception as e:
                        print(e)
                        poiType = poiArea = addressSpan[0].text

                    priceDiv = div.find_elements_by_xpath("./div[@class='item-bottom-info clearfix']/div")[0]
                    poiPrice = priceDiv.text

                    lonlatDiv = div.find_elements_by_xpath("./div[@class='item-site-info clearfix']/div")[1]
                    lonlatDiv.click()
                    time.sleep(0.2)
                    if self.queryLoadCompalte("//div[@class='info-win']"):
                        #  检测 返回结果为空的情况 "对不起，没有符合条件的商家 "class="list-ul"
                        try:
                            # 等待 <div class='common-list-main'> 标签加载完成
                            ulTags = WebDriverWait(self.browserDriver, 8).until(
                                EC.presence_of_element_located((By.XPATH, "//div[@class='info-win']/p")))
                        except Exception as e:
                            print(u"未找到info-win")
                            continue
                    infowinDiv = div.find_elements_by_xpath("//div[@class='info-win']/p")
                    lonlatDiv = infowinDiv[3].find_elements_by_xpath("./a")[0]
                    mapUrl = lonlatDiv.get_attribute('href')
                    olon, olat = mapUrl.split("&")[2].replace("c=", "").split(",")
                    coordination = self.coordTrans(float(olat), float(olon))  # 坐标系转换
                    lon, lat = [str(coordination.get("lon", "")), str(coordination.get("lat", ""))]
                    closemapDiv = self.browserDriver.find_elements_by_xpath("//i[@class='iconfont icon-close_icon']")[0]
                    try:
                        closemapDiv.click()
                    except Exception as e:
                        print(e)

                    poiInfo = searchList + [poiCity, poiName, poiId, poiType, poiArea, str(olon), str(olat), lon, lat,
                                            url, poiUrl, poiSource, poiComment,
                                            poiPrice, poiAddress + '\n']
                    print(poiInfo)
                    poiInfos.append(",".join(poiInfo))
                    # self.poiInfos.append(list(poiInfo))

                with open(r'./searchPoi.csv', mode='a+', encoding='utf-8', errors='ignore') as f:  # 将poi信息写入文件
                    f.writelines(poiInfos)

                with open(r'./searchPoi.dat', mode='w', encoding='utf-8', errors='ignore') as f:  # 将采集进度写入文件
                    f.write(searchName)
                if self.browserDriver.find_elements_by_xpath("//*[@class='no-search-content']"):
                    isLastPage = True
                else:
                    isLastPageTag = self.browserDriver.find_elements_by_xpath(
                        "//*[@class='mt-pagination']/*[@class='clearfix']")
                    isLastPageTag = isLastPageTag[-1].find_element_by_tag_name("li")
                    if "active" not in isLastPageTag.get_attribute("class"):
                        isLastPage = True
                    else:
                        isLastPage = False
                        isLastPageTag.click()
                        print("Next page Click !!!")
                        self.queryLoadCompalte("//*[@class='common-list']")

    def getSearchPois_2(self):
        # 获取脚本中的JSON数据
        self.poiSearch = self.readUrlList(r'./poiSearchName.txt')
        currUrlIndex = self.readCurr()  # 读取进度

        # 遍历每一个 需要采集的 url
        for searchName in self.poiSearch[currUrlIndex:-1]:
            poiInfos = []
            searchList = searchName.replace("\n", "").split(",")
            url = self.getSearchUrl(searchList[0], searchList[1].replace("/","_"))
            print(url)
            self.oprnUrl(url)

            # 等待   "//div[@class='common-list']" 元素载入完成
            if self.queryLoadCompalte("//script[contains(text(),'searchResult')]"):
                #  检测 返回结果为空的情况 "对不起，没有符合条件的商家 "class="list-ul"
                try:
                    # 等待 "//*[@class='common-list-main']" 标签加载完成
                    ulTags = WebDriverWait(self.browserDriver, 5).until(
                        EC.presence_of_element_located((By.XPATH, "//script[contains(text(),'searchResult')]")))
                except Exception as e:
                    print(u"对不起，没有符合条件的商家")
                    continue

            # 最后一页标志
            isLastPage = False
            while not isLastPage:
                bsText = self.browserDriver.page_source
                soup = BeautifulSoup(bsText, "html.parser")
                scriptTags = soup.find_all('script', text=re.compile(r'window.AppData = .+'))
                if scriptTags:
                    scriptText = scriptTags[0].text.replace('window.AppData = ', "")
                    scriptText = scriptText.strip(";")
                    pois = self.toJson(scriptText)
                    if pois:
                        pois = pois.get("data", "").get("searchResult", "")
                        for poi in pois:
                            poiCity, poiName, poiId, poiType, poiArea, olon, olat, lon, lat,poiUrl, poiSource, poiComment, poiPrice, poiAddress = "", "", "", "", "", "", "", "", "", "", "", "", "", ""
                            poiCity = poi.get("city", "") or \
                                      self.browserDriver.find_elements_by_xpath("//span[@class='current-city']")[0].text
                            poiName = poi.get("title", "")
                            poiId = poi.get("id", "")
                            poiType = poi.get("showType", "")
                            poiArea = poi.get("areaname", "")
                            olon = poi.get("longitude", "")
                            olat = poi.get("latitude", "")
                            coordination = self.coordTrans(float(olat), float(olon))  # 坐标系转换
                            lon, lat = [str(coordination.get("lon", "")), str(coordination.get("lat", ""))]
                            poiUrl = "https://www.meituan.com/meishi/" + str(poiId)
                            poiSource = poi.get("avgscore", "")
                            poiComment = poi.get("comments", "")
                            poiPrice = poi.get("avgprice", "")
                            poiAddress = poi.get("address", "")

                            poiInfo = searchList + [poiCity, poiName, str(poiId), poiType, poiArea, str(olon), str(olat),
                                                    lon, lat, url, poiUrl, str(poiSource), str(poiComment), str(poiPrice),
                                                    poiAddress + '\n']

                            poiInfos.append(",".join(poiInfo))

                print(poiInfos)

                with open(r'./searchPoi.csv', mode='a+', encoding='utf-8', errors='ignore') as f:  # 将poi信息写入文件
                    f.writelines(poiInfos)
                with open(r'./searchPoi.dat', mode='w', encoding='utf-8', errors='ignore') as f:  # 将采集进度写入文件
                    f.write(searchName)

                if self.browserDriver.find_elements_by_xpath("//*[@class='no-search-content']"):
                    isLastPage = True
                else:
                    isLastPageTag = self.browserDriver.find_elements_by_xpath(
                        "//*[@class='mt-pagination']/*[@class='clearfix']")
                    isLastPageTag = isLastPageTag[-1].find_element_by_tag_name("li")
                    if "active" not in isLastPageTag.get_attribute("class"):
                        isLastPage = True
                    else:
                        isLastPage = False
                        isLastPageTag.click()
                        print("Next page Click !!!")
                        self.queryLoadCompalte("//*[@class='common-list']")


if __name__ == "__main__":
    meituan = GetMeituan()
    # 初始化selenium Chrome 对象
    browserDriver = meituan.seleniumChromeInit()

    # # 获取所有城市id
    # meituan.getCtyCode(u"陕西")
    #
    # # 获取分类ID
    # meituan.getCateCode()
    #
    # # 获取子区域id
    # meituan.getAreaCode(u"咸阳",[u"陈s区"])

    # 获取poi
    meituan.getSearchPois_2()
    print("complate!")
