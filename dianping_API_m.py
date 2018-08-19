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
m.dianping.com/shop/550409/map         # 地图经纬度

"""

import requests
from bs4  import BeautifulSoup
from fake_useragent import UserAgent
from decodeDzdpPoi import *
from createNewDir import *
from coordinateTranslate import *
from time import sleep
import sys, os, csv, re
from random import triangular,randint
import getProxyFromProxyPools as proxy

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
        self.currentPoiFileName = r'./tab/' + str(self.cityId) + '_currentPoi.dat'  # 保存进度的文件路径
        self.poisFileName = r'./tab/' + str(self.cityId) + r'.csv'  # 保存店铺POI信息的文件路径

        self.translate = GPS()  # 初始化坐标系转化

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
            # print("parameters已更改:\n",parameter, self.parameters[parameter])

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
                self.metroNavs = resultJson.get('metroNavs',[])    # 地铁站分类

            if 'recordCount' in keys:
                self.recordCount = resultJson.get('recordCount',[])   # POI 个数

            if 'regionNavs' in keys:
                self.regionNavs = resultJson.get('regionNavs',[])    # 区域分类
                self.regionsHot = [regionNav for regionNav in self.regionNavs if regionNav.get('parentId',[])==-10000] # 热门区域
                self.regionsOne = [regionNav for regionNav in self.regionNavs if regionNav.get('parentId',[])==0] # 一级区域
                self.regionsOneSelf = [regionNav for regionNav in self.regionNavs if regionNav.get('parentId',[]) == regionNav['id']]  # 一级区域底下包含全部子poi的子区域
                self.regionsTwo = [regionNav for regionNav in self.regionNavs if regionNav.get('parentId',[]) not in [0,-10000,regionNav['id']]]  # 一级区域底下包含全部子poi的子区域
                self.regions = sorted(list(set([region.get('id',[]) for region in self.regionsTwo])))

            if 'categoryNavs' in keys:
                self.categoryNavs = resultJson.get('categoryNavs',[])    # POI类型分类
                # self.categorysHot = [categoryNav for categoryNav in self.categoryNavs if categoryNav['parentId']==0 and categoryNav['id']!=0] # 热门区域
                self.categorysOne =  [categoryNav for categoryNav in self.categoryNavs if categoryNav['parentId']==0 and categoryNav['id']!=0] # 一级区域
                self.categorysOneSelf =  [categoryNav for categoryNav in self.categoryNavs if categoryNav['parentId']== categoryNav['id']]  # 一级区域底下包含全部子poi的子区域
                self.categorysTwo = [categoryNav for categoryNav in self.categoryNavs if categoryNav['parentId']!= categoryNav['id'] and categoryNav['parentId']!=0]  # 一级区域底下包含全部子poi的子区域
                self.categorys = sorted(list(set([category['id'] for category in self.categorysTwo])))

            self.currentPoi = []
            return
        else:
            print("getCategorys Error! 请检查验证码!")
            sleep(1.36531)
            # self.changeProxy()    # 更改代理
            return self.getCategorys()     #迭代本方法


    def getPagePois(self):
        # 获取POI总的分类
        self.changeUserAgnet()              # 随机更换 UserAgnet
        self.clearCookie()                  # 清除 Cookies
        poiCount = 0
        #self.changeParameters(params)       # 设置 get() 方法的 params 附加参数
        poiInfo = []
        coordinate = ""
        poiDatil = []
        tagList = ""
        try:
            # print(self.parameters)
            result = requests.get(self.poiPageUrl, timeout=10, headers=self.headers, params = self.parameters, proxies=self.proxies)
        except  Exception as e:
            print(e)
            # self.changeProxy()    # 更换代理
            return self.getPagePois()

        if result.status_code==200:              # 如果返回的状态码为200 则正常,否则异常
            resultJson = result.json()          # 把json 转化为字典
            keys = list(resultJson.keys())       # 字典的key的 列表
            coordinate = ""  # 获取 店铺经纬度
            if 'isEnd' in keys:
                self.isEnd = resultJson.get('isEnd')                       # 本次的 分类和 地区下的店铺是否是最后一页
            if 'nextStartIndex' in keys:
                self.currentStartIndex = resultJson.get('nextStartIndex',0)     # 更新下一次开始的start参数
            if 'recordCount' in keys:
                self.recordCount = resultJson.get('recordCount',1)

            if 'list' in keys and list:
                if "没有找到合适的商户" not in result.text:
                    for item in resultJson.get('list',[]):
                        try:
                            categoryId = item.get('categoryId','')
                            categoryName = item.get('categoryName','')
                            cityId = item.get('cityId','')
                            dishtags = item.get('dishtags','')
                            id = item.get('id','')
                            matchText= item.get('matchText','')
                            name = item.get('name','')
                            poiType = item.get('poiType','')
                            priceText = item.get('priceText','')
                            regionName = item.get('regionName','')
                            reviewCount = item.get('reviewCount','')
                            shopPower = item.get('shopPower','')
                            shopType = item.get('shopType','')
                            tagList = ";".join([tag.get('text',[])  for tag in item.get('tagList',[])])    # tagList   列表转 字符串

                            if id :
                                coordinate = self.getPoiCoordinate(id)  # 获取 店铺经纬度
                                # time.sleep(random.uniform(1,4))
                                # poiDatil = self.getPoiDatil(id)         # 获取点评详细信息
                        except  Exception as e:
                            print(e, '\n', self.parameters)

                        poiInfo = [name, categoryId, categoryName, cityId,
                                   dishtags, id, matchText, poiType, priceText,
                                   regionName, reviewCount,
                                   shopPower, shopType, tagList, coordinate
                                   ] + poiDatil
                        poiInfo = list(["'" + str(item) + "'" for item in poiInfo])  # 增加csv界定符
                        self.pois.append(list(poiInfo))  # 添加信息到 self.pois 列表中
                        poiCount = poiCount + 1
                    print(self.currentStartIndex)

                else:
                    print("没有找到合适的商户:", result.url)

            print(poiInfo)
            return poiCount
        else:
            print("http返回状态码异常:",result.status_code, self.poiPageUrl)     # 更换代理
            sleep(triangular(1, 2.0))
            return self.getPagePois()


    def getCurrentPoi(self):
        #  # 载入进度, 写入表头
        if not isExistPath(self.poisFileName):  # 如果不存在 currentPoi.dat
            with open(self.poisFileName, 'a+', encoding='utf-8', errors=None) as f:
                f.writelines(','.join(
                    ["'name'",  "'categoryId'",  "'categoryName'",  "'cityId'",
                     "'dishtags'",  "'id'",  "'matchText'",  "'poiType'",
                     "'priceText'",  "'regionName'",
                     "'reviewCount'",  "'shopPower'",  "'shopType'",  "'tagList'",
                     "'coordinate'",  "'kouwei'",  "'huanjing'",  "'fuwu'",
                     "'addresses'",  "' phones'",  "' otherInfoes'"
                     , "\n"]))         # 写入表头
            self.currentPoi = [0,0,0]
        elif not isExistPath(self.currentPoiFileName):  # 如果不存在 currentPoiFileName.dat
            self.currentPoi = [0,0,0]
        elif isExistPath(self.currentPoiFileName):  # 如果存在 currentPoiFileName.dat
            with open(self.currentPoiFileName, 'r', encoding='utf-8', errors=None) as f:  # 将采读取进度文件
                self.currentPoi = list(f.readline().split(","))  # 从文件 currentPoi.dat 读取采集进度.

        if int(self.currentPoi[0]) in self.categorys:
            self.currentcategoryIndex = self.categorys.index(int(self.currentPoi[0]))   # 找到 self.categorys　的索引
        else: self.currentcategoryIndex = 0

        if int(self.currentPoi[1]) in self.regions:
            self.currentRegionIndex = self.regions.index(int(self.currentPoi[1]))     # 找到　self.regions　的索引
        else: self.currentRegionIndex = 0

        self.currentStartIndex = int(self.currentPoi[2])          #　设置开始的序号


    def main(self):
        for c,category in enumerate(self.categorys[self.currentcategoryIndex:]):                      # 迭代 分类列表
            self.nextCategory = category
            pageNum = 0
            for r,region in enumerate(self.regions[self.currentRegionIndex:]):                      # 迭代 区域列表
                self.nextRegion = region
                pageNum = pageNum + 1
                self.recordCount = 1
                while self.currentStartIndex!=self.recordCount:        # 迭代 页数
                    parameters = {  'start' : self.currentStartIndex,
                                    'categoryid' : str(category),
                                    # 'sortid' : '3',
                                    'cityid' : str(self.cityId),
                                    # 'limit' :  '50',
                                    'regionid' : str(region)
                                    }
                    self.changeParameters(parameters)    # 更新 parameters 到 self.parameters
                    result = self.getPagePois()
                    if result:
                        if (pageNum % 5)==0:
                            self.saveFile()     # 写入文件
                    else :
                        print("getPagePois 失败!")
                self.currentStartIndex = 0
                self.saveFile()  # 写入文件

    def saveFile(self):
        csvfile = open(self.poisFileName, 'a+', newline='', encoding='utf8')  # 内容写入 csv文件
        writer = csv.writer(csvfile)
        writer.writerows(self.pois)
        csvfile.close()
        with open(self.currentPoiFileName, 'w', encoding='utf-8', errors=None) as f:  # 将采集进度写入文件
            f.writelines(
                str(self.nextCategory) + ',' + str(self.nextRegion) + ',' + str(self.nextStartIndex))
        self.pois = []   # 清空 self.pois
        print("保存文件完成!")

    def getPoiCoordinate(self,id):
        url = 'http://m.dianping.com/shop/' + str(id) + r'/map'
        headers = {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
                    'Accept-Encoding': 'gzip, deflate',
                    'Accept-Language': 'zh-CN,zh;q=0.9',
                    'Cache-Control': 'no-cache',
                    'Connection': 'keep-alive',
                    'Cookie': '',
                    'DNT': '1',
                    'Host': 'm.dianping.com',
                    'Pragma': 'no-cache',
                    'Upgrade-Insecure-Requests': '1',
                    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.162 Safari/537.36 Avast/65.0.411.162'
                   }

        try:
            result = requests.get(url, timeout=10, headers=headers, proxies=self.proxies)
        except  Exception as e:
            print(e,"Retry...")
            # self.changeProxy()    # 更换代理
            return self.getPoiCoordinate(id)

        if result.status_code == 200:  # 如果返回的状态码为200 则正常,否则异常
            soup = BeautifulSoup(result.text, 'html.parser')  # 将返回的网页转化为bs4 对象
            scripts = soup.findAll(name='script')
            if scripts:
                script = [script.text for script in scripts if "shopLat" in script.text][0].strip().strip(';')
                script = script.replace(r'window.PAGE_INITIAL_STATE = ','').strip()
                script = script.replace('false', 'False').replace('true', 'True')
                scriptDict = eval(script)
                shopId = scriptDict.get('_context').get('pageInitData').get('shopId')
                shopLat = scriptDict.get('_context').get('pageInitData').get('shopLat')
                shopLng = scriptDict.get('_context').get('pageInitData').get('shopLng')
            if shopId==id :
                coordinate = self.translate.gcj_decrypt_exact(shopLat,shopLng)
                coordinate = str(coordinate.get("lon")) + ";" + str(coordinate.get("lat"))
                return  coordinate
                # Out[9]: '\n        window.PAGE_INITIAL_STATE = {"_context":{"header":{"user-agent":"Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.162 Safari/537.36 Avast/65.0.411.162","cookie":"; _hc.v=e337b7a8-91d7-140d-3e99-cc64da3abd05.1534085629"},"modules":[{"moduleName":"bottom-app","config":{"support_system":"all","bottomapp_link_ios":"https://link.dianping.com/universal-link?originalUrl=https%3A%2F%2Fevt.dianping.com%2Fsynthesislink%2F10900.html%3FshopId%3D{shopId}&schema=dianping%3A%2F%2Fshopinfo%3Fid%3D{shopId}%26utm%3D@utm@","bottomapp_utm":"ulink_shopmapbutton","setSyntheticalLink":"https://evt.dianping.com/synthesislink/10900.html","bottomapp_link_android":"https://evt.dianping.com/synthesislink/10900.html?shopId={shopId}","setDownloadLink":"https://m.dianping.com/download/redirect?id=10899","pos":"top"},"isServerRender":false},{"moduleName":"map","config":{"map_link_android":"https://m.dianping.com/shop/{shopId}/map","map_link_ios":"https://link.dianping.com/universal-link?originalUrl=https%3A%2F%2Fm.dianping.com%2Fshop%2F{shopId}%2Fmap&schema=dianping%3A%2F%2Fshopinfo%3Fid%3D{shopId}%26utm%3D@utm@","map_utm":"ulink_shopmap"},"isServerRender":false},{"moduleName":"autoopenapp","config":{"utm":"","app_utm":"w_mshop_map","app_link_android":"dianping://mapnavigation?shopid={shopId}","app_link_ios":"dianping://mapnavigation?shopid={shopId}"},"isServerRender":false}],"mSource":"default","pageInitData":{"shopId":"550409","shopIdTrue":"550409","shopLat":34.26091955582504,"shopLng":108.9531197944874,"userLat":0,"userLng":0,"shopName":"西安饭庄","address":"东大街298号","overseascity":false,"mapType":"qqmap","googleApiUrl":""},"pageEnName":"map"},"bottom-app":{"_config":{"support_system":"all","bottomapp_link_ios":"https://link.dianping.com/universal-link?originalUrl=https%3A%2F%2Fevt.dianping.com%2Fsynthesislink%2F10900.html%3FshopId%3D{shopId}&schema=dianping%3A%2F%2Fshopinfo%3Fid%3D{shopId}%26utm%3D@utm@","bottomapp_utm":"ulink_shopmapbutton","setSyntheticalLink":"https://evt.dianping.com/synthesislink/10900.html","bottomapp_link_android":"https://evt.dianping.com/synthesislink/10900.html?shopId={shopId}","setDownloadLink":"https://m.dianping.com/download/redirect?id=10899","pos":"top"},"_isInit":false},"map":{"_config":{"map_link_android":"https://m.dianping.com/shop/{shopId}/map","map_link_ios":"https://link.dianping.com/universal-link?originalUrl=https%3A%2F%2Fm.dianping.com%2Fshop%2F{shopId}%2Fmap&schema=dianping%3A%2F%2Fshopinfo%3Fid%3D{shopId}%26utm%3D@utm@","map_utm":"ulink_shopmap"},"_isInit":false},"autoopenapp":{"_config":{"utm":"","app_utm":"w_mshop_map","app_link_android":"dianping://mapnavigation?shopid={shopId}","app_link_ios":"dianping://mapnavigation?shopid={shopId}"},"_isInit":false}};\n    '
        else:
            print("http status_code :", result.status_code,",Retry...")
            return self.getPoiCoordinate(id)


    def getPoiDatil(self,id):
        self.changeUserAgnet()              # 随机更换 UserAgnet
        #self.clearCookie()                  # 清除 Cookies

        url = 'http://m.dianping.com/shop/' + str(id)
        services = []
        addresses = ""
        phones  = ""
        otherInfoes = ""

        headers = {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
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
        try:
            result = requests.get(url, timeout=10, headers=headers, proxies=self.proxies)
        except  Exception as e:
            print(e,"Retry...")
            # self.changeProxy()    # 更换代理
            return self.getPoiDatil(id)

        if result.status_code == 200:  # 如果返回的状态码为200 则正常,否则异常
            soup = BeautifulSoup(result.text, 'html.parser')  # 将返回的网页转化为bs4 对象
            # div = soup.find_all("div", class_="desc", attrs={'id': False})
            servicesDiv = soup.find_all("div", class_="desc")[0]
            if servicesDiv :
                services = servicesDiv.find_all("span")
                services = [service.text for service in services ]

            phoneAddressDiv = soup.find_all("div", class_="info-list link-list")
            if phoneAddressDiv[0]:
                addresses = phoneAddressDiv[0].text.strip()
            if phoneAddressDiv[1]:
                phoneses = phoneAddressDiv[1].find_all("a")
                phoneses = ";".join([phones.text.strip() for phones in phoneses])

            otherInfoDiv = soup.find_all("div", class_="businessTime")[0]
            if otherInfoDiv:
                otherInfoes = otherInfoDiv.text.strip().replace("\n"," ")

            return services + [addresses, phoneses, otherInfoes]

        else:
            # self.changeProxy()  # 更改代理
            print("http status_code :", result.status_code,",Retry...")
            return self.getPoiDatil(id)





if __name__=='__main__':
    [{"name": "西安,陕西", "id": "17"},
    {"name": "咸阳,陕西", "id": "292"},
    {"name": "宝鸡,陕西", "id": "291"},
    {"name": "延安,陕西", "id": "294"},
    {"name": "汉中,陕西", "id": "295"},
    {"name": "渭南,陕西", "id": "293"},
    {"name": "安康,陕西", "id": "297"},
    {"name": "铜川,陕西", "id": "290"}]

    for i in [299]:
        dianping = getDianpingInfoAPI(i)     # 初始化对象  参数为城市ID

        # print(dianping.getPoiCoordinate('550409'))
        dianping.getCategorys()    # 获取分类信息
        # dianping.regions = [1754]
        # dianping.categorys = [110]
        dianping.getCurrentPoi()              # 读取 采集进度

        dianping.main()
        print(123)