#!usr/bin/env python
#-*- coding:utf-8 _*-

"""
@author:Administrator
@file: dianping_API.py
@time: 2018/08/{DAY}
描述: 大众点评 API
返回json格式的结果
"""


import requests
from changeKey import Keys              #导入更换Key 的模块
from fake_useragent import UserAgent
from time import sleep
from cutRect import cutRect, rectToPoint
import createShapeFile
import json, csv
from random import triangular,randint
import geoOperation
from getProxyFromProxyPools import ChangeProxy
from createNewDir import *
from coordinateTranslate import GPS



poi_search_url = "http://restapi.amap.com/v3/place/text"
#poi_boundary_url = "https://ditu.amap.com/detail/get/detail"
poi_boundary_url = "https://www.amap.com/detail/get/detail"
url = 'http://restapi.amap.com/v3/place/polygon'



class GetRectPoi():
    url = 'http://restapi.amap.com/v3/place/polygon?polygon=108.889573,34.269261;108.924163,34.250959&key=dc44a8ec8db3f9ac82344f9aa536e678&extensions=all&offset=10&page=1'
    # 在此处 polygon 字段为 要取得POI的 矩形框的左上角坐标 和右下角坐标 例如 '108.889573,34.269261;108.924163,34.250959'
    # key 为高德地图的 key 如 : 'dc44a8ec8db3f9ac82344f9aa536e678'
    # extensions 表示 是要获取基本POI  还是全部POI  值为 'base' 或  'all'
    # offset 为 每一页返回的POI 的个数 建议不超过15个 10 个最好 值为 '10'
    # page 为页数  '1'


    def __init__(self,rect,typecode):
        self.polygonUrl = 'https://www.amap.com/detail/get/detail'
        '''
        用于获取建筑物边界的 url: 'https://www.amap.com/detail/get/detail?id=B001D088Y7'
        '''

        self.searchUrl = 'http://restapi.amap.com/v3/place/polygon'
        '''
        用于搜索 矩形框内的 POI 的 url : 'http://restapi.amap.com/v3/place/polygon?polygon=108.889573,34.269261;108.924163,34.250959&key=dc44a8ec8db3f9ac82344f9aa536e678&extensions=all&offset=10&page=1'
        '''

        self.searchUrlParams = {  'key': 'dc44a8ec8db3f9ac82344f9aa536e678',
                                  'polygon': '',                   #self.rectToPolygonStr(rect),
                                  'extensions': 'all',
                                  'offset': '20',
                                  'page': '1' }        # 初始 searchUrl 的 附带参数
        self.polygonUrlParams = {'id' : ''}         # 初始 boundUrl 的 附带参数

        self.searchUrlHeaders = {"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
                                "Accept-Encoding": "gzip, deflate",
                                "Accept-Language": "zh-CN,zh;q=0.9",
                                "Connection": "keep-alive",
                                "Cookie": "key=bfe31f4e0fb231d29e1d3ce951e2c780; guid=b62c-103a-88ca-1534; isg=BGhox-wZp35qUIv697t9Zvi6OVa6Ocz1wvvAUyKd9ePMfQHnyqFwKo_8cdUo1oRz",
                                "DNT": "1",
                                "Host": "restapi.amap.com",
                                "Pragma": "no-cache",
                                "Cache-Control": "no-cache",
                                "Upgrade-Insecure-Requests": "1",
                                "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.162 Safari/537.36 Avast/65.0.411.162"
                                }        # 初始 searchUrl 的 headers 字典

        self.polygonUrlHeaders = {"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
                                "Accept-Encoding": "gzip, deflate, br",
                                "Accept-Language": "zh-CN,zh;q=0.9",
                                "Connection": "keep-alive",
                                "Cookie": "key=bfe31f4e0fb231d29e1d3ce951e2c780; guid=b62c-103a-88ca-1534; _uab_collina=153440389354382456943315; isg=BLy8y9g9yzq3FP9mYx9hIkSGjVquHWCxjlcU75Y9yKeKYVzrvsUwbzLzRUm8Mpg3",
                                "DNT": "1",
                                "Host": "www.amap.com",
                                "If-None-Match": 'W/"dc5-u8GPvtk0uXscPOCrJfDSBe3nBt8"',
                                "Pragma": "no-cache",
                                "Cache-Control": "no-cache",
                                "Upgrade-Insecure-Requests": "1",
                                "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.162 Safari/537.36 Avast/65.0.411.162"
                                }       # 初始 boundUrl 的 headers 字典

        self.proxyPools = ChangeProxy()                        #实例化代理池类
        self.changeProxy = self.proxyPools.changeProxyIP     # 调用更换代理方法
        self.noProxy = self.proxyPools.noProxyIP()              # 无代理的requests.session 对象
        self.ua = UserAgent()  # 初始化 随机'User-Agent' 方法
        self.amapKey = Keys()                                  # 实例化 Keys 类对象
        self.pageCount = 0                                     # 用于计数 表示获取了多少页POI 用来 判断是否是最后一页
        self.retryCount = 0                                    # 重试次数
        ''' 定义源矩形的对象坐标 '''
        self.rect = rect         # 定义初始的 rect
        self.searchUrlParams['types'] = typecode
        self.subRects = []       #分割rect后的列表信息 格式为字典的列表
        self.strSubRects = []       #分割rect后的列表信息 格式为 字符串的列表
        self.createTime = arrow.now().format('YYYYMMDDHHmmss')
        self.filePath = os.getcwd()  +  '\\tab\\'+ str(self.rect) + "_" + typecode        #拼接文件夹以当天日期命名 typecode 为 poi类型 id
        createDir(self.filePath)
        self.currentPoiFileName = r'./tab/' + str(self.rect) + "_" + typecode  +  r'/currentPoi.dat'  # 保存进度的文件路径
        self.poisFileName = r'./tab/'  + str(self.rect) + "_" + typecode +  r'/pois.csv'  # 保存POI信息的文件路径
        self.subRectsFileName = r'./tab/'  + str(self.rect) + "_" + typecode  +  r'/subRects.dat'  # 保存subRects的文件
        self.currentRect = ""           # 当前正在处理的 rect
        self.currentPage = 1            #　当前正在处理的 页数
        self.currentRectIndex = 0       # 用于保存当前采集Rect的索引
        self.pois = []                  #用来保存poi数据的 列表

        self.gps = GPS()                # 坐标系转化
        self.gcjToWgs = self.gps.gcj_decrypt_exact

    def changeKey(self):
        self.key = self.amapKey.getKey()  # 调用更换Key 的方法
        self.searchUrlParams['key'] = self.key
        cookie = self.searchUrlHeaders["Cookie"].split(";")
        for i in range(len(cookie)):
            if "key=" in cookie[i]:
                self.searchUrlHeaders["Cookie"].replace(cookie[i].split("=")[1], self.key)

        #"Cookie": "key=bfe31f4e0fb231d29e1d3ce951e2c780; guid=b62c-103a-88ca-1534; isg=BGhox-wZp35qUIv697t9Zvi6OVa6Ocz1wvvAUyKd9ePMfQHnyqFwKo_8cdUo1oRz",

    def changeUserAgnet(self, option):
        ''' 随机更换请求头的 用户代理 User-Agent '''
        ''' 根据option参数选择设置 哪个 requestheader 的 User-Agent '''
        if option == 'search':
            self.searchUrlHeaders['User-Agent'] = self.ua.random
        elif option == 'polygon':
            self.polygonUrlHeaders['User-Agent'] = self.ua.random

    def changeCookie(self, option, cookie=""):
        ''' 设置 http 的 cookie '''
        ''' 根据option参数选择设置 哪个 requestheader 的 Cookie '''
        if option == 'search':
            self.searchUrlHeaders['Cookie'] = cookie
        elif option == 'polygon':
            self.polygonUrlHeaders['User-Agent'] = cookie


    def setParams(self,option,keyDict):
        #设置requests.get() 方法 url附带的的 参数
        ''' 根据option参数选择设置 哪个 requestheader 参数 '''
        if option == 'search':
            urlParams = self.searchUrlParams
        elif option == 'polygon':
            urlParams = self.polygonUrlParams
        for key,value in keyDict.items() :      #遍历 keyDict
            if key in urlParams :               #如果 keyDict 中的key 在 self.urlParams中存在,
                urlParams[key] = value          #把 keyDict 中的value 更新到 self.urlParams 中

    def setHeader(self,keyDict,option):
        #设置requests.get() 方法 headers 的各个参数
        ''' 根据option参数选择设置 哪个 requestheader 参数 '''
        if option == 'search':
            headers = self.searchUrlHeaders
        elif option == 'polygon':
            headers = self.polygonUrlHeaders
        for key,value in keyDict.items() :              #遍历 keyDict
            if key in headers :   #如果 keyDict 中的key 在 self.urlParams中存在,
                headers[key] = value      #把 keyDict 中的value 更新到 self.urlParams 中


    def add_parameters(self,params, **kwargs):
        #将字典中 key  转化为 'key'　
        return params.update(kwargs)
        #>> > params = {}
        #>> > add_parameters(params, f1=1, f2=3, f3=9)
        #>> > params
        #{'f1': 1, 'f2': 3, 'f3': 9}

    def rectToPolygonStr(self, rect) :
        #rect格式为 [[108.889573,34.269261], [108.924163,34.250959]]
        polygon = str(rect[0][0]) + ',' + str(rect[0][1]) + ';' + str(rect[1][0]) + ',' + str(rect[1][1])
        # 转化为'108.889573,34.269261;108.924163,34.250959'
        return  polygon

    def isJsonStr(self,jsonStr):
        try:
            json.loads(jsonStr)
        except ValueError:
            return False
        return True




    def getPoiPage(self,rect, proxy=requests.session):
        '''
        此方法通过高德地图搜索api url:
        'http://restapi.amap.com/v3/place/polygon?page=1&extensions=all&offset=10&polygon=108.924463%2C34.269687%3B108.946908%2C34.259437&key=dc44a8ec8db3f9ac82344f9aa536e678'
        来搜索矩形范围内的 POI 的详细信息 并返回当前页的 json 的字典详细数据
        :param rect: # 接收的参数为 矩形框的 坐标 [[108.889573,34.269261], [108.924163,34.250959]]
        :param proxy: # 一个使用代理的 requests.session 对象
        :return: #返回当前页的 json 的字典详细数据       {"status":"1","count":"894","info":"OK","infocode":"10000","suggestion":{"keywords":[],"cities":[]},"pois":......}
        '''
        self.changeKey()                            # 更换 get() 方法的附带参数 key 的值
        self.changeUserAgnet('search')              # 更换 http header 的 浏览器用户代理
        self.changeCookie('search', cookie="")      # 更换 http header 的  cookie
        rectParam = {'polygon': self.rectToPolygonStr(rect)}
        self.setParams('search',rectParam)          #使用 self.setParams() 方法 更新 get() 方法的附带参数 'polygon' 字段的值

        try:
            result = proxy.get(self.searchUrl, params = self.searchUrlParams, timeout = 10, headers = self.searchUrlHeaders)
            self.retryCount = self.retryCount + 1
            # 请求重试次数加1
            if result.status_code==200:
            # 判断返回的 http status_code 状态码 是否为200,  200:返回正常, 404:页面未找到 500:服务器内部错误
                if self.isJsonStr(result.text):
                # 判断返回的页面是否为json 序列
                    resultJson = result.json()
                    # 得到json格式的数据
                    if resultJson['status'] == '1':
                    # 在高德地图的api中 'status' 返回  '1'为正常, '6'为'too fast'请求过快, '0' 为 'invalid key' key出问题了
                        return  dict(resultJson)
                        # 返回 resultJson 字典

                    elif resultJson['status'] == '6':
                        sleep(triangular(1.0,3.0))
                        # 暂停脚本 1到3秒的时间
                        print("错误,被Amap ban了,amap status:", resultJson['status'], "/ninfo:", resultJson['info'], "Retry...")
                        return self.getPoiPage(rect, self.changeProxy())
                        # 更换代理 迭代本方法

                    elif resultJson['status'] == '0':
                        sleep(triangular(0,2.0))
                        print("错误,被Amap ban了,amap status:", resultJson['status'], "/ninfo:", resultJson['info'], "Retry...")
                        return self.getPoiPage(rect, proxy)
                        # 迭代本方法自动更换 key
                else:
                    print("页面返回值为无效的json序列!")

            elif result.status_code==403:
                sleep(triangular(0, 2.0))
                print("Http错误:", result.reason, "Retry...")
                return self.getPoiPage(rect,  self.changeProxy)
                # 更换代理 迭代本方法

            else:
                print("http status_code 错误:", result.status_code,"\nreason :", result.reason, "Retry...")
                sleep(triangular(0, 2.0))
                return self.getPoiPage(rect, self.changeProxy())
                # 更换代理 迭代本方法

        except Exception as e:
            print('出现异常:', e, '\nRetry...')
            sleep(triangular(0, 2.0))
            return self.getPoiPage(rect, self.changeProxy())


    def getRectPoiCount(self,rect, proxy=requests.session):
        '''
        接收 self.getPoiPage() 方法返回的 http json 字典 来确认索矩形范围内的 POI 的数量
        :param rect: # 接收的参数为 矩形框的 坐标 [[108.889573,34.269261], [108.924163,34.250959]]
        :param proxy: # 一个使用代理的 requests.session 对象
        :return: #通过解析返回POI数量的json 此方法的返回值为 键值对 {'rect' : rect, 'count' : 742}
                  # 若失败, 返回 0
        '''
        resultJson = self.getPoiPage(rect, proxy)
        # getPoiPage() 方法返回值为 http结果的json数据 的 字典
        if "count" in resultJson.keys():
        # 如果字典中存在key: "count"
            rectPoiCount = {'rect': rect, 'count': int(resultJson.get('count',None))}
            # 把 键值对 {'rect' : rect, 'count': 339}  保存到 rectPoiCount
            return  dict(rectPoiCount)
            # 返回 rect 和 poiCount 的字典
        else:
            return 0



    def getSubRect(self, rect, poiNum, proxy=requests.session):
        """
        # 分割RECT矩形,如果经纬度矩形内的POI个数大于指定的个数(poiNum)
        # 就把此矩形递归的分割成四等份,类似于田字格
        # 返回包含矩形内POI数量和矩形rect的列表 保存在self.subRects列表中
        :param rect: # 接收的参数为 矩形框的 坐标 [[108.889573,34.269261], [108.924163,34.250959]]
        :param proxy: # 一个使用代理的 requests.session 对象
        :param poiNum: #  一个矩形范围内的 最多有多少个 poi
        :return: # 返回矩形内包含POI数量和矩形rect的列表 保存在self.subRects 列表中
                  # 出错返回值 为 0
        """
        result = self.getRectPoiCount(rect, proxy)      #传入的参数为 rect,获取rect范围内的POI数量,
        if  not isinstance(result,int) :          #如果返回值为不为int型(为字典类型)
            if int(result['count']) > poiNum :    #如果返回的poi个数 大于规定的个数 poiNum
                rects = cutRect(rect)                       #将rect分割为四等份
                for subRect in rects :                      #递归四个子矩形rect
                    self.getSubRect(subRect, poiNum, proxy)     # 调用自己 不能用return
            elif int(result['count']) <= poiNum :        #如果 返回的rect内的POI个数 小于规定的个数 poiNum
                rectPoiCount = dict({'rect': rect, 'count': int(result['count'])})            #整理为字典格式的数据  如:{'rect': [[107.889573, 35.269261], [108.406868, 34.76011]], 'count': 367}
                self.subRects.append(rectPoiCount)       #将返回包含矩形内POI数量和矩形rect的列表 添加到self.subRectPosCount
                print("最小子矩形: ", rectPoiCount)
                return rectPoiCount  # 返回  正常
        else :
            print(result)
            return result           #如果返回值为 int, 说明返回的是出错代码 为 0


    def getPoiInfo(self, rect, proxy=requests.session):
        '''
        根据矩形范围获取矩形范围内的 POI 的是数量 和 POI的列表的列表[count, poiList]
        :param rect: # 接收的参数为 矩形框的 坐标 [[108.889573,34.269261], [108.924163,34.250959]]
        :param proxy: # 一个使用代理的 requests.session 对象
        :return: # 返回 该参数定义的矩形范围内的 POI 的是数量 和 POI的列表
        '''
        self.currentRect = rect                # 保存此 rect 为 当前的rect
        while int(rect['count'])>(self.currentPage -1) * int(self.searchUrlParams['offset']):
            resultJson = self.getPoiPage(rect['rect'], proxy)  # 传入的参数为 rect,获取rect范围内的POI数量
            if not isinstance(resultJson, int) and 'pois' in resultJson.keys():  # 如果返回值为不为int型(为字典类型)
                self.currentPage += 1          # 页数加1
                self.searchUrlParams['page'] = str(self.currentPage)
                for poi in resultJson['pois']:
                    adcode = poi.get('adcode', '')
                    address = poi.get('address', '')

                    alias = poi.get('alias', '')
                    if isinstance(alias,list): alias = "".join(alias)

                    businessArea = poi.get('business_area', '')
                    if isinstance(businessArea,list): businessArea = ";".join(businessArea)

                    cityCode = poi.get('citycode', '')
                    cityName = poi.get('cityname', '')
                    discountNum = poi.get('discount_num', '')
                    email = ";".join(poi.get('email', ''))
                    entrLocation = poi.get('entr_location', '')
                    if entrLocation and isinstance(entrLocation,list):     # entrLocation 有的时候是个列表 有的时候是个字符串
                        entrLocation = entrLocation[0].split(",")
                    elif entrLocation and isinstance(entrLocation,str):
                        entrLocation = entrLocation.split(",")
                    if entrLocation:                                #gcj 坐标系转化为 wgs 坐标系
                        wgsEntrCoordi = self.gcjToWgs(float(entrLocation[1]), float(entrLocation[0]))
                        entrLocation = str(wgsEntrCoordi['lon'])  + "," + str(wgsEntrCoordi['lat'])
                    gridCode = poi.get('gridcode', '')
                    id = poi.get('id', '')
                    indoorMap = poi.get('indoor_map', '')
                    location = poi.get('location', '').split(",")
                    if location:                                       #gcj 坐标系转化为 wgs 坐标系
                        wgsLocation = self.gcjToWgs(float(location[1]), float(location[0]))
                        location = str(wgsLocation['lon']) + "," + str(wgsLocation['lat'])
                    name = poi.get('name', '')
                    naviPoiId = poi.get('navi_poiid', '')
                    photos = str(poi.get('photos', ''))
                    parkingType =poi.get('parking_type', '')
                    pcode = poi.get('pcode', '')
                    panme = poi.get('pname', '')
                    recommend = poi.get('recommend', '')
                    shopId = ";".join(poi.get('shopid', ''))
                    shopInfo = poi.get('shopinfo', '')
                    tag = ";".join(poi.get('tag', ''))
                    tel = str(poi.get('tel', ''))
                    type = poi.get('type', '')
                    typeCode = poi.get('typecode', '')
                    webSite = ";".join(poi.get('website', ''))
                    detail = self.getPoiBound(id,proxy)

                    poiInfo = [adcode, address, alias, businessArea, cityCode, cityName, discountNum,
                                email, entrLocation, gridCode, id, indoorMap, location,
                                name, naviPoiId, photos, parkingType, pcode, panme, recommend, shopId,
                                shopInfo, tag, tel, type, typeCode, webSite, address
                                ] + detail
                    poiInfo = list(["'" + str(item) + "'" for item in poiInfo])  # 增加csv界定符
                    self.pois.append(poiInfo)       # 添加到self.pois 列表

            else:
                print(resultJson)
                return resultJson  # 如果返回值为 int, 说明返回的是getRectPoiCount()的出错代码 为 0
        else:
            print(rect['rect'],"采集到POI:",len(self.pois))
            self.saveFile()       # 保存POI文件 和 进度文件



    def saveFile(self):
        csvfile = open(self.poisFileName, 'a+', newline='', encoding='utf8')  # 内容写入 csv文件
        writer = csv.writer(csvfile)
        writer.writerows(self.pois)
        csvfile.close()
        with open(self.currentPoiFileName, 'w', encoding='utf-8', errors=None) as f:  # 将采集进度写入文件
            self.currentRect['page'] = self.currentPage
            f.writelines(str(self.currentRect))
        self.pois = []   # 清空 self.pois
        self.searchUrlParams['page'] = '1'
        self.currentPage = 1    #正在采集页 置为 0
        print("保存文件完成!")

    def loadCurrent(self,rect):
        """
        rect 查找分割后的子矩形保存的文件,若找到则 载入, 如果未找到,则获取
        查找存储poi数据的csv文件 如果未找到,则新建此文件,并写入表头,
        如果找到,则继续查找保存采集进度的文件,若未找到,则设置进度从头开始,若找到进度文件, 则载入并设置采集进度
        :param rect: 原始的rect
        :return: 无返回值
        """
        self.currentPoi = [0, 1]
        # 若存在文件,则载入 subRects 列表文件 , 若不存在,则获取 subRects 的列表
        if not isExistPath(self.subRectsFileName):  # 如果不存在 self.subRectsFileName  (源矩形分割后的子矩形列表文件)
            noProxy = requests.session()
            self.getSubRect(rect, 100, noProxy)                                             # 分割RECT
            self.strSubRects = [str(subRect) for subRect in self.subRects]           # 把rect列表转化为str字符串 字典的序列化
            with open(self.subRectsFileName, 'w', encoding='utf-8', errors=None) as f:  # 将采集进度写入文件
                f.writelines('\n'.join(self.strSubRects))
        else:
            with open(self.subRectsFileName, 'r', encoding='utf-8', errors=None) as f:  # 将采读取进度文件
                self.strSubRects = f.readlines()                                        # 从文件读取 subRects的列表
                self.subRects = [json.loads(subRect.strip('\n').replace("'",'"')) for subRect in self.strSubRects]  # 将字符串反序列化
                # 注意此处json.loads() 转化的json字符串的key要使用 双引号 引用 否则会出错
        #  载入进度, 写入表头
        if not isExistPath(self.poisFileName):  # 如果不存在 pois.csv
            with open(self.poisFileName, 'a+', encoding='utf-8', errors=None) as f:
                f.writelines(','.join(["'adcode'", "'address'", "'alias'", "'businessArea'",
                                       "'cityCode'", "'cityName'", "'discountNum'", "'email'",
                                       "'entrLocation'", "'gridCode'", "'id'",
                                       "'indoorMap'", "'location'", "'name'", "'naviPoiId'",
                                       "'photos'", "'parkingType'", "'pcode'", "'panme'",
                                       "'recommend'", "'shopId'", "'shopInfo'", "'tag'",
                                       "'tel'", "'type'", "'typeCode'", "'webSite'", "'address'",
                                       "'bcsBase'",  "'businessBase'",  "'classIfyBase'",
                                       "'codeBase'",  "'nameBase'",  "'tagBase'",  "'titleBase'",
                                       "'aoisBase'",  "'xy'",  "'buildingTypesDeep'",  "'businessDeep'",
                                       "'priceDeep'",  "'propertyFeeDeep'",  "'reviewDeep'",
                                       "'CountReview'",  "'aoiidShape'",  "'areaShape'",
                                       "'centerShape'",  "'levelShape'",  "'pylgonShape'",
                                       "'spTypeShape'",  "'typeShape'" +
                                         "\n"]))         # 写入表头
        elif isExistPath(self.currentPoiFileName):  # 如果存在 currentPoiFileName.dat
            with open(self.currentPoiFileName, 'r', encoding='utf-8', errors=None) as f:  # 将采读取进度文件
                self.currentRect = f.readline().replace("'", '"')    # 从文件 currentPoi.dat 读取采集进度.
                self.currentRect = json.loads(self.currentRect)       # 转化为字典

            if "rect" in self.currentRect.keys():
                subRects = [subRect['rect'] for subRect in self.subRects]  # 提取self.subRects['rect']
                if str(self.currentRect.get('rect')) in str(subRects):  # 转化为字符串 然后查找是否存在
                    self.currentPoi[0] = subRects.index(self.currentRect.get('rect'))  # 查找到索引
            if "page" in self.currentRect.keys():
                self.currentPoi[1] = self.currentRect.get('page')

            self.currentRectIndex, self.searchUrlParams['page'] = self.currentPoi


    def getMainRect(self):
        rect = self.rect
        self.loadCurrent(rect)
        for subRect in self.subRects[self.currentRectIndex:]:
            self.currentSubRect = subRect  # 保存当前采集的subRect
            test.getPoiInfo(subRect, self.noProxy)  # 获取RECT内的POI 信息

    def getPoiBound(self,id, proxy=requests.session()):
        resultJson = self.getPoiBoundJson(id, proxy)
        base = []
        deep = []
        review = []
        shape = []
        if isinstance(resultJson,dict):
                # if not isinstance(resultJson,int):
                itemBase = resultJson.get('data','').get('base','')
                """ base 字典数据提取,  不是字典,则此列表为空字符列表"""
                if isinstance(itemBase, str):
                    base = [""]*8
                else:
                    bcsBase= itemBase.get('bcs','')
                    businessBase= itemBase.get('business','')
                    classIfyBase= itemBase.get('classify','')
                    codeBase= itemBase.get('code','')
                    nameBase= itemBase.get('name','')
                    tagBase= itemBase.get('tag','')
                    titleBase= itemBase.get('title','')
                    aois = itemBase.get('geodata', '').get('aoi', '')
                    aoisBase = ";".join([str(list(aoi.values())) for aoi in aois])
                    xy = [itemBase.get('x',''),itemBase.get('y','')]
                    if xy:                                       #gcj 坐标系转化为 wgs 坐标系
                        wgsLocation = self.gcjToWgs(float(xy[1]), float(xy[0]))
                        xy = str(wgsLocation['lon']) + "," + str(wgsLocation['lat'])
                    base = [bcsBase, businessBase, classIfyBase, codeBase, nameBase, tagBase, titleBase, aoisBase, xy]

                itemDeep = resultJson.get('data', '').get('Deep', '')
                """ deep 字典数据提取,  不是字典,则此列表为空字符列表"""
                if isinstance(itemDeep, str):
                    deep = [""] * 5
                else:
                    buildingTypesDeep = itemDeep.get('building_types', '')
                    businessDeep = itemDeep.get('business','')
                    priceDeep = itemDeep.get('price','')
                    propertyFeeDeep = itemDeep.get('property_fee','')
                    reviewDeep =  str(itemDeep.get('review',''))
                    deep = [buildingTypesDeep, businessDeep, priceDeep, propertyFeeDeep, reviewDeep]

                itemReview = resultJson.get('data', '').get('rti', '')
                """ rti 字典数据提取, 不是字典,则此字段为空字符"""
                if isinstance(itemReview, str):
                    CountReview = ""
                else :
                    CountReview = itemReview.get('review_count','')
                review = [CountReview]

                itemShape = resultJson.get('data', '').get('spec', '').get('mining_shape', '')
                """ mining_shape 字典数据提取,  不是字典,则此列表为空字符列表"""
                if isinstance(itemShape, str):
                    shape = [""]*7
                else:
                    aoiidShape = itemShape.get('aoiid','')
                    areaShape = itemShape.get('area','')
                    centerShape = itemShape.get('center','')
                    levelShape = itemShape.get('level','')
                    pylgonShape =  itemShape.get('shape','')
                    spTypeShape =  itemShape.get('sp_type','')
                    typeShape =  itemShape.get('type','')
                    shape = [aoiidShape, areaShape, levelShape, spTypeShape, typeShape, centerShape, pylgonShape]

        return  base + deep + review + shape



    def getPoiBoundJson(self, poiID, proxy=requests.session):
        '''
        返回 包含 pylgon 的 request.get返回的 字典对象
        :param poiID:poi id
        :param proxy: requests.session 附带一个代理
        :return: 返回 包含 pylgon 的 request.get返回的 字典对象
        '''
        self.changeUserAgnet('pylgon')              # 更换 http header 的 浏览器用户代理
        self.changeCookie('pylgon', cookie="")      # 更换 http header 的  cookie
        self.polygonUrlParams = {'id': poiID}
        try:
            result = proxy.get(self.polygonUrl, params=self.polygonUrlParams, timeout=10, headers=self.polygonUrlHeaders)
            if result.status_code==200:
                # 判断返回的 http status_code 状态码 是否为200,  200:返回正常, 404:页面未找到 500:服务器内部错误
                if self.isJsonStr(result.text):
                    # 判断返回的页面是否为json 序列
                    resultJson = result.json()
                    # 得到json格式的数据
                    if resultJson['status'] == '1':
                    # 在高德地图的api中 'status' 返回  '1'为正常, '6'为'too fast'请求过快, '0' 为 'invalid key' key出问题了
                        return  dict(resultJson)
                        # 返回 resultJson 字典

                    elif resultJson['status'] == '6':
                        sleep(triangular(3.0,6.0))
                        # 暂停脚本 1到3秒的时间
                        print("错误,被Amap ban了,amap status:", resultJson['status'], "\nInfo:", resultJson['data'], ",Retry...")
                        return self.getPoiBoundJson(poiID, self.changeProxy())
                        # 更换代理 迭代本方法

                    elif resultJson['status'] == '0':
                        sleep(triangular(1.0,3.0))
                        print("错误,被Amap ban了,amap status:", resultJson['status'], "\nInfo:", resultJson['data'], ",Retry...")
                        return self.getPoiBoundJson(poiID, self.changeProxy())
                        # 更换代理 迭代本方法
                else:
                    print("页面返回值为无效的json序列!")
                    sleep(triangular(0, 2.0))
                    return self.getPoiBoundJson(poiID, self.changeProxy())
                    # 更换代理 迭代本方法

            elif result.status_code==403:
                sleep(triangular(0, 2.0))
                print("Http错误:", result.reason, "Retry...")
                return self.getPoiBoundJson(poiID, self.changeProxy())
                # 更换代理 迭代本方法

            else:
                print("http status_code 错误:", result.status_code,"\nreason :", result.reason, "Retry...")
                sleep(triangular(0, 2.0))
                return self.getPoiBoundJson(poiID, self.changeProxy())
                # 更换代理 迭代本方法

        except Exception as e:
            print('出现异常:', e, '\nRetry...')
            sleep(triangular(0, 2.0))
            return self.getPoiBoundJson(poiID, self.changeProxy())



if __name__ == '__main__' :
    #获取经纬度rect 范围内的 高德地图poi 建筑物边界 并生成shp 图形文件
    #   [108.774989,34.41341], [109.149898,34.102978]
    #rect = [[108.897814, 34.2752], [108.9256255, 34.2661305]]       #注意 此处的经纬度 为 GPS经纬度经过偏置后的  高德地图 经纬度
    rect = [[108.783916,34.443428],[109.157794,34.095302]]                  # 大西安
    # rect =[[108.924463,34.269687], [108.946908,34.259437]]                # 测试区域
    typecodes = ["060000","061000","070000","071000","072000","080000","090000","100000","110000","120000","130000","140000","141000","150000","151000","160000","170000","180000","190000","200000","220000","970000","990000","991000"]
    for typecode in typecodes:
        noProxy = requests.session()
        test = GetRectPoi(rect,typecode)         #初始化类
        test.getMainRect()
        print(len(test.pois))
        print(len(test.pois))
