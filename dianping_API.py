#!usr/bin/env python  
#-*- coding:utf-8 _*-  

""" 
@author:Administrator 
@file: dianping_API.py 
@time: 2018/08/{DAY} 
描述: 大众点评 API
返回json格式的结果
http://mapi.dianping.com/searchshop.json?start=0&categoryid=55&sortid=3&cityid=17&regionid=1754
http://mapi.dianping.com/searchshop.json?start=0&categoryid=55&parentCategoryId=55&locatecityid=0&limit=20&sortid=3&cityid=17&regionid=1754&maptype=0&callback=jsonp_1533991018085_97238
http://mapi.dianping.com/searchshop.json?start=0&categoryid=55&parentCategoryId=55&locatecityid=0&limit=20&sortid=3&cityid=17&regionid=8914&maptype=0&callback=jsonp_1533991129709_2717
http://mapi.dianping.com/searchshop.json?start=3927&categoryid=55&cityid=17
"""

import requests
from bs4  import BeautifulSoup
from fake_useragent import UserAgent
from decodeDzdpPoi import *
from createNewDir import *
from coordinateTranslate import *
from random import randint
from time import sleep
import os
import sys
import getProxyFromProxyPools as proxy
import csv

sys.setrecursionlimit(1500)  # set the maximum depth as 1500

class getDianpingInfoAPI():
    def __init__(self,cityId=17):
        # url : http://www.dianping.com/xian/ch10/r8914o2    #  最后面的o2  是结果的排序方式
        self.headers = {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
                        'Accept-Encoding': 'gzip, deflate',
                        'Accept-Language': 'zh-CN,zh;q=0.9',
                        'Cache-Control': 'no-cache',
                        'Connection': 'keep-alive',
                        'Cookie': 's_ViewType=10; _hc.v=6253504c-e567-584b-6e22-f50b3ba7fc14.1533461129; _lxsdk_cuid=16509c802acc8-0ce39f0d22e7c6-252b1971-100200-16509c802acc8; _lxsdk=16509c802acc8-0ce39f0d22e7c6-252b1971-100200-16509c802acc8; aburl=1; _tr.u=3Fco1rsYewrQ2nmY; cy=17; cye=xian; Hm_lvt_dbeeb675516927da776beeb1d9802bd4=1533971041; Hm_lpvt_dbeeb675516927da776beeb1d9802bd4=1533971041; cityid=17; m_flash2=1; default_ab=shopList%3AA%3A1%7Cmap%3AA%3A1; pvhistory=6L+U5ZuePjo8L2Vycm9yL2Vycm9yX3BhZ2U+OjwxNTMzOTg5OTE2NjQwXV9b',
                        'DNT': '1',
                        'Host': 'mapi.dianping.com',
                        'Pragma': 'no-cache',
                        'Upgrade-Insecure-Requests': '1',
                        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.162 Safari/537.36 Avast/65.0.411.162'
                        }

        self.cityId = cityId              # 要采集的城市的ID  默认为西安 id = 17
        self.ua=UserAgent()     # 初始化 随机'User-Agent' 方法
        self.translate = GPS()      # 初始化坐标系转化
        self.getproxy = proxy.ChangeProxy().getProxy()        #初始化类对象 ChangeProxy()的方法 getProxy()
        self.proxies = None         # requests 的 get()方法的 附加参数
        self.categorysUrl = 'http://mapi.dianping.com/searchshop.json?sortid=3&cityid=' + str(self.cityId)

        self.poiPageUrl = 'http://mapi.dianping.com/searchshop.json'
        self.parameters =  {'start' : '0',
                            'categoryid' : '55',
                            'sortid' : '3',
                            'cityid' : '17',
                            'limit' :  '50',
                            'regionid' : '1754'
                            }

        self.metroNavs = []  # 地铁站分类
        self.recordCount = []   # POI 总个数
        self.regionNavs = []   # 区域分类
        self.regionsHot = []  # 热门区域
        self.regionsOne = [] # 一级区域
        self.regionsOneSelf = [] # 一级区域底下包含全部子poi的子区域
        self.regionsTwo = [] # 一级区域底下包含全部子poi的子区域

        self.categoryNavs = [] # POI类型分类
        # self.categorysHot = [] # 热门区域
        self.categorysOne = [] # 一级区域
        self.categorysOneSelf = [] # 一级区域底下包含全部子poi的子区域
        self.categorysTwo = [] # 一级区域底下包含全部子poi的子区域

        self.nextStartIndex = 0
        self.recordCount = 1
        self.pois = []  #保存一个分类的 poi信息

        # self.urlsFileName = r'./tab/' + self.city + '_' + self.ch + '_urls.dat'         #保存页面url的文件路径
        # self.poisFileName = r'./tab/' + self.city + '_' + self.ch + '_pois.csv'         #保存店铺POI信息的文件路径
        # self.currentUrlFileName = r'./tab/' + self.city + '_' + self.ch + '_currentUrl.dat'     # 保存进度的文件路径

    def changeProxy(self):
        getProxy = self.getproxy()
        http = "http://" + getProxy[0] + ":" + getProxy[1]
        https = "https://" + getProxy[0] + ":" + getProxy[1]
        self.proxies = {"http": http, "https": https, }
        return self.proxies



    def changeUserAgnet(self):
        self.headers['User-Agent'] = self.ua.random

    def clearCookie(self):
        self.headers['Cookie'] = ""

    def changeParameters(self,parameters):
        for parameter in list(parameters.keys()):
            self.parameters[parameter] = parameters[parameter]
            print("parameters已更改:\n",self.parameters[parameter])

    def getCategorys(self):
        # 获取POI总的分类
        self.changeUserAgnet()
        self.clearCookie()
        url = self.categorysUrl
        result = requests.get(url, timeout=10, headers=self.headers, proxies=self.proxies)
        if result.status_code==200:              # 如果返回的状态码为200 则正常,否则异常
            resultJson = result.json()
            keys = list(resultJson.keys())

            if 'metroNavs' in keys:
                self.metroNavs = resultJson['metroNavs']    # 地铁站分类

            if 'recordCount' in keys:
                self.recordCount = resultJson['recordCount']    # POI 个数

            if 'regionNavs' in keys:
                self.regionNavs = resultJson['regionNavs']    # 区域分类
                self.regionsHot = [regionNav for regionNav in self.regionNavs if regionNav['parentId']==-10000] # 热门区域
                self.regionsOne = [regionNav for regionNav in self.regionNavs if regionNav['parentId']==0] # 一级区域
                self.regionsOneSelf = [regionNav for regionNav in self.regionNavs if regionNav['parentId'] == regionNav['id']]  # 一级区域底下包含全部子poi的子区域
                self.regionsTwo = [regionNav for regionNav in self.regionNavs if regionNav['parentId'] not in [0,-10000,regionNav['id']]]  # 一级区域底下包含全部子poi的子区域

            if 'categoryNavs' in keys:
                self.categoryNavs = resultJson['categoryNavs']    # POI类型分类
                # self.categorysHot = [categoryNav for categoryNav in self.categoryNavs if categoryNav['parentId']==0 and categoryNav['id']!=0] # 热门区域
                self.categorysOne =  [categoryNav for categoryNav in self.categoryNavs if categoryNav['parentId']==0 and categoryNav['id']!=0] # 一级区域
                self.categorysOneSelf =  [categoryNav for categoryNav in self.categoryNavs if categoryNav['parentId']== categoryNav['id']]  # 一级区域底下包含全部子poi的子区域
                self.categorysTwo = [categoryNav for categoryNav in self.categoryNavs if categoryNav['parentId']!= categoryNav['id'] and categoryNav['parentId']!=0]  # 一级区域底下包含全部子poi的子区域
            return
        else:
            print("getCategorys Error! 请检查验证码!")
            self.changeProxy()    # 更改代理
            return self.getDataCategorys()     #迭代本方法



    def getPagePois(self):
        # 获取POI总的分类
        self.changeUserAgnet()              # 随机更换 UserAgnet
        self.clearCookie()                  # 清除 Cookies
        #self.changeParameters(params)       # 设置 get() 方法的 params 附加参数
        result = requests.get(self.poiPageUrl, timeout=10, headers=self.headers, params = self.parameters, proxies=self.proxies)
        if result.status_code==200:              # 如果返回的状态码为200 则正常,否则异常
            resultJson = result.json()          # 把json 转化为字典
            keys = list(resultJson.keys())       # 字典的key的 列表

            if 'nextStartIndex' in keys:
                self.nextStartIndex = resultJson['nextStartIndex']      # 更新下一次开始的start参数
            if 'recordCount' in keys:
                self.recordCount = resultJson['recordCount']

            if 'list' in keys and list:
                for item in resultJson['list']:
                    categoryId = item['categoryId']
                    categoryName = item['categoryName']
                    cityId = item['cityId']
                    id = item['id']
                    name = item['name']
                    priceText = item['priceText']
                    regionName = item['regionName']
                    reviewCount = item['reviewCount']
                    shopPower = item['shopPower']
                    shopType = item['shopType']
                    shopUuid = item['shopUuid']
                    poiInfo = [name, id, cityId, categoryName, categoryId,
                                regionName,self.parameters['regionid'], shopType,
                                shopUuid, reviewCount, shopPower, priceText
                                ]
                self.pois.append(list(poiInfo))     #添加信息到 self.pois 列表中




    def main(self):
        for category in self.categorysTwo:                      # 迭代 分类列表
            # category['id']
            for region in self.regionsTwo:                      # 迭代 区域列表
                # region['id']
                self.poiCount = self.recordCount
                self.poisFileName = r'./tab/' + str(self.cityId) + '_' + str(category['id']) + '_' + str(region['id']) + r'.csv'        #保存店铺POI信息的文件路径

                pageNum = 0
                while self.nextStartIndex!=self.recordCount:        # 迭代 页数
                    parameters = {  'start' : self.nextStartIndex,
                                    'categoryid' : str(category['id']),
                                    'sortid' : '3',
                                    'cityid' : str(self.cityId),
                                    'limit' :  '50',
                                    'regionid' : str(region['id'])
                                    }
                    self.changeParameters(parameters)    # 更新 parameters 到 self.parameters
                    self.getPagePois()
                    self.currentPoiFileName =  r'./tab/' + str(self.cityId) + '_' + str(category['id']) + '_' + str(region['id']) +  '_' + self.nextStartIndex + '_currentUrl.dat'  # 保存进度的文件路径

                    if pageNum > 20 :
                        pageNum = pageNum + 1
                        csvfile = open(self.poisFileName, 'a+', newline='')     # 写入 csv文件
                        writer = csv.writer(csvfile)
                        writer.writerows(self.pois)

                        with open(self.currentPoiFileName, 'w', encoding='utf-8', errors=None) as f:  # 将采集进度写入文件
                            f.writelines(str(self.cityId) + '_' + str(category['id']) + '_' + str(region['id']) +  '_' + self.nextStartIndex)

                        csvfile.close()
                        self.pois = []   # 清空 self.pois




if __name__=='__main__':
    dianping = getDianpingInfoAPI(17)     # 初始化对象  参数为城市ID
    poiClass = dianping.getCategorys()      # 获取分类信息

    dianping.main()
    print(123)