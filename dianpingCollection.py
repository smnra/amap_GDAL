#!usr/bin/env python  
#-*- coding:utf-8 _*-  

""" 
@author:Administrator 
@file: dianpingCollection.py 
@time: 2018/07/{DAY} 
描述: 大众点评网 评估查询采集

"""




'''
dianpingUrl
http://www.dianping.com/xian
http://www.dianping.com/xian/ch8/r8914
                                 r8914 为商圈代号
https://www.dianping.com/ajax/json/suggest/search?do=hsc&c=17&s=0&q=%E7%8E%AB%E7%91%B0%E8%8A%B1
http://www.dianping.com/search/map/keyword/17/10_ST.LOUIS%E5%9C%A3%E8%B7%AF%E6%98%93%E8%91%A1%E5%9B%BD%E9%A4%90%E5%8E%85#

'''
import requests
from bs4  import BeautifulSoup


class getDianpingInfo():
    def __init__(self,cityName='xian'):
        # url : http://www.dianping.com/xian/ch10/r8914o2    #  最后面的o2  是结果的排序方式

        self.url = 'http://www.dianping.com/xian/ch10/r8914o2'   #  最后面的o2  是结果的排序方式
        self.city = cityName              # 要采集的城市 默认为西安
        self.dataCategory = 'food'      # 要采集的
        self.regionNavs = []     # 行政区 区县 如 科技路  的id
        self.regionNavSubs = []    # 按 行政区 的商圈 子分类  如 雁塔区 底下的商圈为 小寨, 小雁塔等的id
        self.dataCategorys = getDianpingInfo(self.city)  # 总分类 例如:在属性名为:data-category 值 为 "index.food" ,"index.life",  等 在页面中可以查找到 http://www.dianping.com/xian
        self.dataCategorys = {"food" : "ch10",         # 美食 ch10
                              "life" : "ch30",        # 休闲娱乐 ch30
                              "wedding" : "ch10",      # 结婚
                              "movie" : "ch10",        # 影视
                              "beauty" : "ch10",       # 丽人
                              "hotel" : "ch10",        # 酒店
                              "baby" : "ch10",         # 亲子
                              "view" : "ch10",         # 周边游
                              "sports" : "ch10",        # 运动健身
                              "shopping" : "ch20",      # 购物 ch20
                              "home" : "ch10",           # 家装
                              "education" : "ch10",     # 学习培训
                              "other" : "ch10",          # 生活服务
                              "medical" : "ch10",        # 医疗健康
                              "car" : "ch10",           # 爱车
                              "pet" : "ch10"          # 宠物
                             }


    def getDataCategorys(self,city):
        pass
        result = requests.get(self.url, timeout=10)
        soup = BeautifulSoup(result.text, 'html.parser')

    def getRegionNavs(self,id):
        self



if __name__=="__main__":
    xianDianping = getDianpingInfo('xian')























