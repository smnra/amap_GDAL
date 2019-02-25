#!usr/bin/env python  
#-*- coding:utf-8 _*-  

""" 
@author:Administrator 
@file: meituan_hotel_selenium.py 
@time: 2018/11/{DAY} 
描述: 

"""
import meituan.meituan_selenium as mt
import requests, re, time,os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class HotelMeituan(mt.GetMeituan):
    def __init__(self):
        mt.GetMeituan.__init__(self)

        self.isLastPageXpath = "//a[@data-index='next']"




    def createCityHotelUrls(self):
        # 取 子分类id 和 子区域 id ,并拼接为url
        cateList = [id.get("id", "") for id in self.cateList]
        areaList = [id.get("id", "") for id in self.areaList]

        # 拼接 url
        for cateId in cateList:
            for areaId in areaList:
                hId = "".join(["c", cateId, "b", areaId])
                url = "https://hotel.meituan.com/" + self.cityAcronym + r"/ba" + areaId + "/"
                self.openUrlList.append(url)


    def readCurr(self):
        # 从文件读取采集进度
        if not os.path.exists(self.csvFile):
            with open(self.csvFile, mode='w', encoding='utf-8', errors='ignore') as f:
                f.write("poiCityName, poiAreaName, poiName, poiId, poiAddress, poiScore, poiMarkNumbers, poiPhone, lon, lat\n")

        if not os.path.exists(self.currFile):
            return 0

        with open(self.currFile, mode='r', encoding='utf-8', errors='ignore') as f:
            currUrl = f.readline()

        if currUrl in self.openUrlList :
            currUrlIndex = self.openUrlList.index(currUrl)
        else:
            currUrlIndex = 0

        return currUrlIndex


    def urlModel(self, ctype,cateId,areaId):
        # 根据不同的 类型 生成不同类型的 url
        # 例如 美食 酒店 休闲娱乐
        if ctype == "hotel":
            url = "https://hotel.meituan.com/" + self.cityAcronym + r"/ba" + areaId + "/"
            # https://hotel.meituan.com/baoji/ba13690/
        if ctype == "xiuxianyule":
            url = "https://" + self.cityAcronym + r".meituan.com/xiuxianyule/b" + areaId + "/"
            # https://baoji.meituan.com/xiuxianyule/b4304/
        if ctype == "meishi":
            url = "http://" + self.cityAcronym + ".meituan.com/meishi/c" + cateId + "b" + areaId + "/"
            # http://baoji.meituan.com/meishi/c17b13698/
        return url

    def createCityUrls(self,ctype):
        # 取 子分类id 和 子区域 id ,并拼接为url
        cateList = [id.get("id", "") for id in self.cateList]
        areaList = [id.get("id", "") for id in self.areaList]

        # 拼接 url
        for cateId in cateList:
            for areaId in areaList:
                url = self.urlModel(ctype, cateId, areaId)
                self.openUrlList.append(url)

    def getPoiInfo_xiuxianyule(self,poiUrl,poiInfoLoadedXpath):
        htmlText = self.newTabGet(poiUrl, poiInfoLoadedXpath)
        poiCityName = re.search(r'"cityName":[ ]*"(.+?)","', htmlText).group(1)
        poiAreaName = ""
        poiName = re.search(r',"shopName":[ ]*(.+?),', htmlText).group(1).replace(",","")
        poiId = re.search(r'"mtShopId":[ ]*(.+?),', htmlText).group(1).replace(",","")
        poiAddress = re.search(r'"address":[ ]*"(.+?)",', htmlText).group(1).replace(",","")
        poiScore = re.search(r'"score":[ ]*(.+?),', htmlText).group(1)
        poiPrice = re.search(r'"avgPrice":[ ]*(.+?),', htmlText).group(1)

        poiMarkNumbers = re.search(r'"markNumbers":[ ]*(.+?),"', htmlText).group(1)
        lon = re.search(r'"lng":[ ]*(.+?),"lat":[ ]*(.+?),', htmlText).group(1)
        lat = re.search(r'"lng":[ ]*(.+?),"lat":[ ]*(.+?),', htmlText).group(2)

        # "park":"","lng":107.371666,"lat":34.351068,

        poiPhone = re.search(r'>电话：(.*?)</div>', htmlText).group(1)

        # 坐标系转换
        coordination = self.coordTrans(float(lat), float(lon))
        lon, lat = [str(coordination.get("lon", "")), str(coordination.get("lat", ""))]

        return [poiCityName,poiAreaName,poiName,poiId,poiAddress,poiScore,poiMarkNumbers,poiPhone,lon,lat]


    def getPoiInfo_hotel(self,poiUrl,poiInfoLoadedXpath):
        htmlText = self.newTabGet(poiUrl, poiInfoLoadedXpath)
        poiCityName = re.search(r'"cityName":[ ]*"(.+?)","', htmlText).group(1)
        poiAreaName = re.search(r'"areaName":[ ]*"(.+?)","', htmlText).group(1)
        poiName = re.search(r',"name":[ ]*"(.+?)","style":', htmlText).group(1).replace(",","")
        poiId = re.search(r'"poiId":[ ]*(.+?),"', htmlText).group(1)
        poiAddress = re.search(r'"addr":[ ]*"(.+?)","', htmlText).group(1).replace(",","")
        poiScore = re.search(r'"avgScore":[ ]*(.+?),"', htmlText).group(1)
        poiMarkNumbers = re.search(r'"markNumbers":[ ]*(.+?),"', htmlText).group(1)
        lon = re.search(r'\|([0-9]+\.[0-9]+?),([0-9]+\.[0-9]+?)"', htmlText).group(2)
        lat = re.search(r'\|([0-9]+\.[0-9]+?),([0-9]+\.[0-9]+?)"', htmlText).group(1)
        poiPhone = re.search(r'>电话：(.*?)</div>', htmlText).group(1)

        # 坐标系转换
        coordination = self.coordTrans(float(lat), float(lon))
        lon, lat = [str(coordination.get("lon", "")), str(coordination.get("lat", ""))]

        return [poiCityName,poiAreaName,poiName,poiId,poiAddress,poiScore,poiMarkNumbers,poiPhone,lon,lat]





    def isLastPage(self,xpath):
        # xpath 为 翻页的 页码 列表  ,
        # 如果最后一个li标签的class 中 含有disable 则 认为是最后一页
        isLastPageTag = self.browserDriver.find_elements_by_xpath(xpath)
        if not isLastPageTag:
            isLastPageFlag = True
        elif "disabled" in isLastPageTag[-1].get_attribute("class"):
            isLastPageFlag = True
        elif "disabled" not in isLastPageTag[-1].get_attribute("class"):
            isLastPageFlag = False
            self.browserDriver.find_element_by_xpath(self.isLastPageXpath).click()
            # isLastPageTag[-1].click()
            print("Next page Click !!!")

        return isLastPageFlag


    def isExistTag(self,poiLoadedXpath,tagXpath):
        # 等待   poiLoadedXpath 元素载入完成, 然后获取 没有poi的 标志noPoiXpath
        if self.queryLoadCompalte(poiLoadedXpath):
            try:
                ulTags = WebDriverWait(self.browserDriver, 5).until(
                    EC.presence_of_element_located((By.XPATH, tagXpath)))
                tag = self.browserDriver.find_element_by_xpath(tagXpath)
                return tag
            except Exception as e:
                print(u"未找到 ",tagXpath)
                return None


    def getCityPois(self,ctype):
        # 获取poi  第一个参数是 判断poi 载入完成的 Xpath
        # 第二个参数是 包含 poi 详细信息页面的链接url 包含 poiId
        # 第三个参数 是 poi 店铺 详细信息页面载入完成的 xpath
        # 第四个参数是 页码 列表的 xpath     用来判断是否是最后一页
        # 并拼接url
        # self.createCityHotelUrls()
        self.createCityUrls(ctype)
        # 读取采集进度
        currUrlIndex = self.readCurr()

        # 遍历每一个 需要采集的 url
        for url in self.openUrlList[currUrlIndex:-1]:
            print(url)
            self.oprnUrl(url)

            # 最后一页标志
            isLastPageFlag = False
            while not isLastPageFlag:
                # 检测是否存在poi
                if self.queryLoadCompalte(self.poiLoadedXpath):
                    # 等待 poiLoadedXpath 元素载入完成
                    poiTagList = self.isExistTag(self.poiLoadedXpath, self.poiListXpath)
                    # 检查 poiListXpath 的元素是否存在
                    if not poiTagList:
                        print("未找到poi,转到下一个url...",url)
                        break

                # 获取poi　的  id 和 链接的 标签
                aTags = self.browserDriver.find_elements_by_xpath(self.poiListXpath)

                #  遍历每一个 poi
                poiInfos = []
                for a in aTags:   # https://hotel.meituan.com/165648762/
                    poiUrl = a.get_attribute("href")
                    poiId = poiUrl.split("/")[-2]

                    # 获取poi info 的详细信息
                    poiInfo = self.getPoiInfo(poiUrl, self.poiInfoXpath)
                    print(poiId,poiInfo)
                    poiInfos.append(",".join(poiInfo)+'\n')
                    # self.poiInfos.append(list(poiInfo))

                with open(self.csvFile, mode='a+', encoding='utf-8', errors='ignore') as f:  # 将poi信息写入文件
                    f.writelines(poiInfos)
                with open(self.currFile, mode='w', encoding='utf-8', errors='ignore') as f:  # 将采集进度写入文件
                    f.write(url)

                if self.isLastPage(self.nextPageXpath):
                    # 如果是最后一页
                    isLastPageFlag = True



if __name__=="__main__":
    meituanHotel = HotelMeituan()
    # 初始化selenium Chrome 对象
    browserDriver = meituanHotel.seleniumChromeInit()

    # 获取所有城市id
    meituanHotel.getCtyCode(u"陕西")

    # 获取分类ID
    meituanHotel.getCateCode()

    # 获取子区域id
    meituanHotel.getAreaCode(u"宝鸡",u"金s区")

    # 获取poi  第一个参数是 判断poi 载入完成的 Xpath
    # 第二个参数是 包含 poi 详细信息页面的链接url 包含 poiId
    # 第三个参数 是 poi 店铺 详细信息页面载入完成的 xpath
    # 第四个参数是 页码 列表的 xpath     用来判断是否是最后一页
    meituanHotel.poiLoadedXpath = "//div[@class='common-list-main']"
    meituanHotel.poiListXpath = "//div[@class='common-list-main']/div/a"
    meituanHotel.poiInfoXpath = "//div[@class='poi-display']"
    meituanHotel.nextPageXpath = "//ul[@class='paginator']/li"
    meituanHotel.isLastPageXpath = "//a[@data-index='next']"
    #  meituanHotel.getCityPois("hotel", "//div[@class='common-list-main']", "//div[@class='common-list-main']/div/a", "//div[@class='poi-display']", "//ul[@class='paginator']/li")



    meituanHotel.poiLoadedXpath = "//div[@class='common-list-main']"
    meituanHotel.poiListXpath = "//div[@class='common-list-main']/div/a"
    meituanHotel.poiInfoXpath = "//div[@class='seller-info-head']"
    meituanHotel.nextPageXpath = "//nav[@class='mt-pagination']/li"
    meituanHotel.isLastPageXpath = "//li[@class='next-btn']"
    meituanHotel.getCityPois("xiuxianyule")


