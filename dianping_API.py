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
        self.cityIds = []
        self.ch = []                      #　ch  总分类列表

        self.categorysUrl = 'http://mapi.dianping.com/searchshop.json?sortid=3&cityid=' + str(self.cityId)
        self.poiPageUrl = 'http://mapi.dianping.com/searchshop.json?start=0&categoryid=55&sortid=3&cityid=17&regionid=1754'

        # self.urlsFileName = r'./tab/' + self.city + '_' + self.ch + '_urls.dat'         #保存页面url的文件路径
        # self.poisFileName = r'./tab/' + self.city + '_' + self.ch + '_pois.csv'         #保存店铺POI信息的文件路径
        # self.currentUrlFileName = r'./tab/' + self.city + '_' + self.ch + '_currentUrl.dat'     # 保存进度的文件路径



    def changeUserAgnet(self):
        self.headers['User-Agent'] = self.ua.random

    def clearCookie(self):
        self.headers['Cookie'] = ""

    def getDataCategorys(self):
        # dataCategorys 获取POI总的分类
        self.dataCategorys = []
        self.changeUserAgnet()
        self.clearCookie()
        url = 'http://www.dianping.com/' + self.city + '/ch8'
        result = requests.get(url, timeout=10, headers=self.headers )
        if result.status_code==200:              # 如果返回的状态码为200 则正常,否则异常
            soup = BeautifulSoup(result.text, 'html.parser')     #将返回的网页转化为bs4 对象
            div = soup.find_all("div", class_="nc-items",attrs={'id':False})
            # 查找 类名为"nc-items",并且 不存在 id 属性的' div 标签
            for a in div[0].findAll("a"):
                # 遍历 div列表的第一个元素 包含的所有的 <A> 标签
                value = a.find("span").text        # a标签的子标签 span 标签 的文本值
                key = a.attrs['href'].split("/")[-1]    # 把a标签的 herf属性的值 用/分割 为列表 取最后一个元素
                self.dataCategorys.append([key, value, a.attrs['href']])
            return list(self.dataCategorys)
        else:
            print("getDataCategorys Error! 请检查验证码!")
            return self.getDataCategorys()




    def getCategorys(self):
        # 获取POI总的分类
        self.changeUserAgnet()
        self.clearCookie()
        url = self.categorysUrl
        result = requests.get(url, timeout=10, headers=self.headers)
        if result.status_code==200:              # 如果返回的状态码为200 则正常,否则异常
            resultJson = result.json()
            keys = list(resultJson.keys())
            if 'metroNavs' in keys:
                self.metroNavs = resultJson['metroNavs']    # 地铁站分类
            if 'recordCount' in keys:
                self.metroNavs = resultJson['recordCount']    # POI 个数
            if 'regionNavs' in keys:
                self.metroNavs = resultJson['regionNavs']    # 区域分类
            return
        else:
            print("getDataCategorys Error! 请检查验证码!")
            return self.getDataCategorys()


if __name__=='__main__':
    dianping = getDianpingInfoAPI(17)
    poiClass = dianping.getCategorys()
    print(dianping)