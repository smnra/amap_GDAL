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
http://www.dianping.com/xian/ch8
http://www.dianping.com/xian/ch8/r8914
                                 r8914 为商圈代号
https://www.dianping.com/ajax/json/suggest/search?do=hsc&c=17&s=0&q=%E7%8E%AB%E7%91%B0%E8%8A%B1
http://www.dianping.com/search/map/keyword/17/10_ST.LOUIS%E5%9C%A3%E8%B7%AF%E6%98%93%E8%91%A1%E5%9B%BD%E9%A4%90%E5%8E%85#

'''
import requests
from bs4  import BeautifulSoup
from fake_useragent import UserAgent
from decodeDzdpPoi import *
from createNewDir import createNewDir
import re

class getDianpingInfo():
    def __init__(self,cityName='xian'):
        # url : http://www.dianping.com/xian/ch10/r8914o2    #  最后面的o2  是结果的排序方式

        self.headers = {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
                        'Accept-Encoding': 'gzip, deflate',
                        'Accept-Language': 'zh-CN,zh;q=0.9',
                        'Cache-Control': 'max-age=0',
                        'Connection': 'keep-alive',
                        'Cookie': 'navCtgScroll=0; showNav=#nav-tab|0|0; _lx_utm=utm_source%3DBaidu%26utm_medium%3Dorganic; _lxsdk_cuid=164ecc140a2c8-0983a9007c6945-252b1971-100200-164ecc140a2c8; _lxsdk=164ecc140a2c8-0983a9007c6945-252b1971-100200-164ecc140a2c8; _hc.v=2195dd5e-1af7-1442-0872-b25748f68cf1.1532980446; s_ViewType=10; _dp.ac.v=0e97f4cb-0a00-4b68-a3af-42cbd882e87d; ua=13201465365; ctu=f5d5b94828db29ae10e4468d68c4987437689a310853888c076fc6a448bcd3e2; aburl=1; cy=17; cye=xian',
                        'DNT': '1',
                        'Host': 'www.dianping.com',
                        'Upgrade-Insecure-Requests': '1',
                        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.162 Safari/537.36 Avast/65.0.411.162'
                        }

        self.cityUrl = 'http://www.dianping.com/xian/ch8'   # 获取总的分类列表 dataCategorys 的 分类id
        self.city = cityName              # 要采集的城市 默认为西安
        self.dataCategorys = []      # 要采集的
        self.regionNavs = []         # 区县列表
        self.regionNavSubs = []      # 区县底下的商圈列表
        # 行政区 区县 如 科技路  的id 和包含的子商圈的列表 如:
        # [['123', '碑林区', 'http://www.dianping.com/xian/ch0/r123', [['1754', '钟楼/鼓楼', 'http://www.dianping.com/xian/ch0/r1754'], ['1765', '西安交大东校区', 'http://www.dianping.com/xian/ch0/r1765'], ['1757', '小雁塔', 'http://www.dianping.com/xian/ch0/r1757']]
        self.pois = []     # 保存商圈底下的poi的列表
        self.pois.append(["id", "starNum", "commentNum", "avgPrice", "subRegion", "address", "locolId", "local"])      # 列名
        self.ua=UserAgent()     # 初始化 随机'User-Agent' 方法

        '''
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
                             }  # 总分类 例如:在属性名为:data-category 值 为 "index.food" ,"index.life",  等 在页面中可以查找到 http://www.dianping.com/xian
        '''

    def changeUserAgnet(self):
        self.headers['User-Agent'] = self.ua.random

    def clearCookie(self):
        self.headers['Cookie'] = ""

    def getDataCategorys(self):
        # dataCategorys 获取POI总的分类
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
            return self.dataCategorys
        else:
            print("请检查验证码!")
            return self.getDataCategorys()

    def getRegionNavs(self):
        # 获取行政区列表
        self.changeUserAgnet()
        self.clearCookie()
        url = 'http://www.dianping.com/' + self.city + '/ch8'
        result = requests.get(url, timeout=10, headers=self.headers)
        if result.status_code == 200:  # 如果返回的状态码为200 则正常,否则异常
            soup = BeautifulSoup(result.text, 'html.parser')  # 将返回的网页转化为bs4 对象
            aTags = soup.find_all("a",attrs = {'data-click-name': "select_reg_biz_click"})
            # 查找 属性  'data-click-name'  值为 "select_reg_biz_click"的 a 标签
            for a in aTags:
                if "http" in a.attrs['href']:
                    key = a.attrs['data-cat-id']
                    name = a.attrs['data-click-title']
                    url = a.attrs['href']
                    self.regionNavs.append([key,name,url])
            return self.regionNavs
        else :
            print("请检查验证码!")
            return self.getRegionNavs()

    def getRegionNavSubs(self,regionNav,i):
        # 获取行政区底下的商圈列表
        subRegions = []
        self.changeUserAgnet()
        self.clearCookie()
        result = requests.get(regionNav[2], timeout=10, headers=self.headers)
        if result.status_code == 200:  # 如果返回的状态码为200 则正常,否则异常
            soup = BeautifulSoup(result.text, 'html.parser')  # 将返回的网页转化为bs4 对象
            div = soup.find_all("div", attrs={'id': "region-nav-sub"})
            div = div[0].find_all("a", attrs={'data-cat-id': True})
            for a in div:
                key = a.attrs['data-cat-id']
                name = a.find("span").text
                url = a.attrs['href']
                subRegions.append(list([key, name, url]))
                self.regionNavSubs.append(list([key, name, url]))       #存储在self.regionNavSubs 对象中
            # maxPage = int(soup.find_all("div", class_="page")[0].find_all("a")[-2].attrs["title"])    # 获取最大页数
            self.regionNavs[i].append(list(subRegions))                 # 追加到self.regionNavs[i] 列表
            return list(subRegions)
        else:
            print("请检查验证码!")
            return self.getRegionNavSubs(regionNav,i)


    def getMaxPage(self,dataCategory,regionNavSub):
        # dataCategory 为 poi的大分类id  regionNavSub 为商圈的id
        # "ch10" 代表 poi 美食分类. "8914" 代表 科技路沿线 商圈
        url = "http://www.dianping.com/" + self.city + r"/" + dataCategory + r"/r" + regionNavSub
        print(url)
        self.changeUserAgnet()
        self.clearCookie()
        result = requests.get(url, timeout=10, headers=self.headers)
        if result.status_code == 200:  # 如果返回的状态码为200 则正常,否则异常
            soup = BeautifulSoup(result.text, 'html.parser')  # 将返回的网页转化为bs4 对象
            maxPage = soup.find_all("div", class_="page")[0].find_all("a")[-2].attrs["title"]  # 获取最大页数
            self.maxPage = maxPage   # 存储在对象中
            return maxPage
        else :
            print("请检查验证码!")
            return self.getMaxPage(dataCategory,regionNavSub)


    def getPoi(self,dataCategory,regionNavSub,pageNum):
        # dataCategory 为 poi的大分类id  regionNavSub 为商圈的id
        # "ch10" 代表 poi 美食分类. "8914" 代表 科技路沿线 商圈
        url = "http://www.dianping.com/" + self.city + r"/" + dataCategory + r"/r" + regionNavSub + "p" + pageNum
        print(url)
        self.changeUserAgnet()
        self.clearCookie()
        try:
            result = requests.get(url, timeout=10, headers=self.headers)
            if result.status_code == 200:  # 如果返回的状态码为200 则正常,否则异常
                soup = BeautifulSoup(result.text, 'html.parser')  # 将返回的网页转化为bs4 对象
                div = soup.find_all("div",class_="txt")
                divAddress = soup.find_all("div", attrs={'class': "tag-addr"})
                aLocal = soup.find_all("a", attrs={'data-click-name': "shop_map_click"})
                pois = []
                for i,subDiv in enumerate(div):
                    poi = []
                    divStart = subDiv.find_all("div", attrs={'class':'comment'})
                    id = divStart[0].find("a",attrs={"data-click-name":"shop_iwant_review_click"}).attrs["data-shopid"]   #shop id

                    starNum = divStart[0].find("span",attrs={"class":True}).attrs["class"][-1].replace("sml-str","")   # 获取星级数字
                    commentNum = divStart[0].find("a",attrs={"data-click-name":"shop_iwant_review_click"}).text.split("\n")[1].strip()         # 获取评论数
                    if commentNum=='我要点评': commentNum='0'
                    avgPrice = divStart[0].find("a",attrs={"class":"mean-price"}).text.replace('\n','').replace(' ','').replace('人均','')       # 获取平均消费
                    subRegion = divAddress[i].find("a", attrs={'data-click-name':'shop_tag_region_click'}).text         # 商圈名字
                    address = divAddress[i].find("span", attrs={'class':'addr'}).text                                       # 地址
                    localId = aLocal[i].attrs["data-poi"]                               # 加密过的 经纬度信息
                    local = ";".join(decodePoi(localId))
                    poi = [id, starNum, commentNum, avgPrice, subRegion, address, localId, local]
                    pois.append(','.join(['"' + p + '"' for p in poi] + ['\n']))
                    # self.pois.append(poi)
                return pois
            else :
                print("请检查验证码!")
                return self.getPoi(dataCategory,regionNavSub,pageNum)

        except:
            print('连接错误,重试!\n',"pageNum:",pageNum )
            return self.getPoi(dataCategory,regionNavSub,pageNum)

if __name__=="__main__":
    dianping = getDianpingInfo('xian')
    dataCategory = dianping.getDataCategorys()    # 获取总的分类和 id 如: 美食,电影,休闲娱乐等...存储在self.dataCategorys 列表中
    regionNav =  dianping.getRegionNavs()           # 获取 地市底下的区县列表 如 雁塔区 碑林区... 存储在 self.regionNavs 列表中
    for i,regionNav in enumerate(dianping.regionNavs):
        regionSubNav =  dianping.getRegionNavSubs(regionNav,i)  # 获取县区底下的 商圈 列表 如  碑林区的 钟楼 交大东校区等..存储在 self.regionNavs 列表中.
        print(regionSubNav)
    regionSubNavs = list(dianping.regionNavSubs)
    filePath = createNewDir()
    with open(filePath + 'dzdp.csv', 'a+', encoding='utf-8', errors=None) as f:
        f.writelines(','.join(["id", "starNum", "commentNum", "avgPrice", "subRegion", "address", "locolId", "local", '\n']))
        # 写入表头

    for regionSubNav in regionSubNavs:
        maxPage = dianping.getMaxPage("ch10",regionSubNav[0])       # 获取商圈区域的最大页数  大于50页的可能获取不准确
        for i in range(1,int(maxPage) + 1):                                 # i 为页数
            pois = dianping.getPoi("ch10",regionSubNav[0],str(i))           # 采集店铺信息
            if pois :
                with open(filePath + 'dzdp.csv', 'a+',encoding='utf-8', errors=None) as f:    # 写入csv文件
                    f.writelines(pois)















'''
userAgent用户代理是必须的,否则:
抱歉！页面无法访问......
错误信息：
    currentDate:2018-07-31 16:56:23
    userIp:124.89.8.137, 10.72.40.11
    userAgent:python-requests/2.12.4

去大众点评首页


'''

