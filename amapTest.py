# -*- coding:UTF-8 -*-

import requests
from changeKey import Keys              #导入更换Key 的模块
from fake_useragent import UserAgent
from time import sleep
from cutRect import cutRect, rectToPoint
import createShapeFile
import arrow, os, json
from random import triangular,randint
import geoOperation
from getProxyFromProxyPools import ChangeProxy



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


    def __init__(self):
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
                                  'offset': '10',
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
        self.changeProxy = self.proxyPools.changeProxyIP()     # 调用更换代理方法
        self.noProxy = requests.session                     # 无代理的requests.session 对象
        self.ua = UserAgent()  # 初始化 随机'User-Agent' 方法
        self.amapKey = Keys()                                  # 实例化 Keys 类对象
        self.retryCount = 0                                    # 重试次数
        self.sourceRect = ''
        ''' 定义源矩形的对象坐标 '''
        self.subRects = []       #分割rect后的列表  信息

        self.createTime = arrow.now().format('YYYYMMDDHHmmss')
        self.filePath = os.getcwd()  +  '\\tab\\' + self.createTime + '\\'        #拼接文件夹以当天日期命名
        self.pois = []                  #用来保存poi数据的 列表

    def changeKey(self):
        self.key = self.amapKey.getKey()  # 调用更换Key 的方法

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
                        return self.getPoiPage(rect, self.changeProxy)
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
                return self.getPoiPage(rect, self.changeProxy)
                # 更换代理 迭代本方法

        except Exception as e:
            print('出现异常:', e, '\nRetry...')
            sleep(triangular(0, 2.0))
            return self.getPoiPage(rect, self.changeProxy)


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
                    print(self.getSubRect(subRect, poiNum, proxy))
            elif int(result['count']) <= poiNum :        #如果 返回的rect内的POI个数 小于规定的个数 poiNum
                rectPoiCount = {'rect': rect, 'count': int(result['count'])}            #整理为字典格式的数据  如:{'rect': [[107.889573, 35.269261], [108.406868, 34.76011]], 'count': 367}
                self.subRects.append(dict(rectPoiCount))       #将返回包含矩形内POI数量和矩形rect的列表 添加到self.subRectPosCount
                return 1  # 返回 1 表示正常
        else :
            print(result)
            return result           #如果返回值为 int, 说明返回的是出错代码 为 0











    def getPoiID(self,rect):
        #此方法执行完将返回 rect内 POI信息 将保存在self.pois 列表中
        result = {}
        result = self.getRectPoiNumber(rect)
        if result == 1 :    #getRectPoiNumber()方法的返回值正常
            if len(self.subRectPosCount) > 0 :      # getRectPoiNumber()  添加到 列表  self.subRectPosCount[]  此列表为获取到的所有子矩形 保存的列表
                for subRect in self.subRectPosCount:        #遍历每一个子矩形
                    notEnd = True                    #isEnd 如果此页的poi数量小于10 并且 存储poi 的 列表 self.pois 长度 和 网页返回 的 poi数量 result['counter'] 差小于9 则认为此页是最后一页
                    page = 0                          #定义当前获取页索引
                    while notEnd:
                        page = page + 1             #页数加1
                        rectParam = {'page': str(page)}
                        self.setParams(rectParam)  # 使用 self.setParams() 方法 更新 get()方法  'page' 的字段 的值
                        result = self.getPoi(subRect['rect'])           #一个result 就是一页 POI
                        if not isinstance(result,int) :                 #如果返回的result 为int 类型 则为出错
                            currentPagePoiNumber = len(result['pois'])      #currentPagePoiNumber 当前页的POI的数量
                            if (currentPagePoiNumber - 10 < 0) and  (int(result['count'])  - len(self.pois) < 9 ) :                 #isEnd 如果此页的poi数量小于10 并且 存储poi 的 列表 self.pois 长度 和 网页返回 的 poi数量 result['counter'] 差小于9 则认为此页是最后一页
                                notEnd = False                              #如果当前页获取到的poi数量小于10 则 认为是最后一页
                            if currentPagePoiNumber > 0:                                   # 如果获取到前页的POI的数量不为0
                                for poi in result['pois'] : #遍历每一个 POI
                                    self.pois.append(poi)
                                    print(str(poi))
        return  self.pois

    def getPoiBound(self,poiID,proxyRequest) :
        Referer = {'Referer': 'https://www.amap.com/place/' + poiID}
        self.setHeader(Referer)  # 使用 self.setHeader() 方法 更新  RequestHeader 中的 Referer 字段中的 poiID

        #根据高德地图POI 的 ID , 获取POI 的建筑物边界 bound的坐标
        params = {'id' : poiID }
        try:
            result = proxyRequest.get(self.boundURL, params = params, timeout = 10, headers = GetRectPoi.headers)
            if result.json()['status'] == '1' :             #在高德地图的api中 'status' 返回  '1' 为正常
                resultJson = result.json()                    #得到json格式的数据
                if 'mining_shape' in resultJson.get('data','').get('spec','') :
                    strRing = resultJson.get('data','').get('spec','').get('mining_shape','').get('shape','')
                    if len(strRing) > 0 :
                        pointList = strRing.split(';')                       #使用';'  把pointList 分割为列表,
                        ring =  [x.split(',') for x in pointList]           #使用列表推导式把 pointList 中的每一项使用 ',' 分割为 列表
                        polygon = geoOperation.Polygon(ring)                         #实例化 geoOperation 对象
                        center = resultJson.get('data','').get('spec','').get('mining_shape','').get('center','')          #获得中心点的坐标 , 默认为 ''
                        if polygon.isInvalidBound(center) == False:                 #如果 bound 的 各条边有出现交叉 Crosses    (判断高德地图返回的bound 是否有效)
                            print('Polygon\'s line is Crosses, change a http proxy to retry!')
                            changeProxyRequest = self.proxyPools.changeProxyIP()  # 更换一次代理
                            return self.getPoiBound(poiID, changeProxyRequest)  #   迭代 本函数
                        else :
                            print(poiID + u' 边界正常: ' + str(ring) )
                            return ring                                  # 没有交叉  则 返回 ring
                    else:
                        return -4
                else:
                    print(poiID + u'此 POI 不存在 mining_shape!')
                    return -5
            elif result.json()['status'] == '6' :           #在高德地图的api中 'status' 返回  '6' 为 'too fast'
                print('Too fast, change a http proxy to retry!')
                time.sleep(1)                                #暂停120秒后 迭代 本函数
                changeProxyRequest = self.proxyPools.changeProxyIP()  # 更换一次代理
                return self.getPoiBound(poiID, changeProxyRequest)  # 迭代 本函数
            elif result.json()['status'] == '8':  # 在高德地图的api中 'status' 返回  '8' 为 poi ID 无效
                print('Not found this id!')
                time.sleep(1)  # 暂停1秒
                return -6
            elif result.json()['status'] == '0' :            #在高德地图的api中 'status' 返回  '0' 为 'invalid key' key出问题了
                print('invalid key, 3s retry!')             #暂停3秒
                time.sleep(1)
                self.setParams({'key': self.amapKey.getKey()})      #更换key
                return self.getPoiBound(poiID, proxyRequest)             # 迭代 本函数
            else :
                return -7
        except requests.exceptions.ConnectionError:
            print('ConnectionError -- please wait 3 seconds')
            time.sleep(1)
            changeProxyRequest = self.proxyPools.changeProxyIP()   # 更换一次代理changeProxyIP
            return self.getPoiBound(poiID, changeProxyRequest)         #更换代理,迭代本方法
            # return -1
        except requests.exceptions.ChunkedEncodingError:
            print('ChunkedEncodingError -- please wait 3 seconds')
            return -2
        except:
            print('Unfortunitely -- An Unknow Error Happened.')
            return -3


def getAmapInfo(rect) :
    # 参数 rect 为 [[108.897814, 34.2752], [108.953437, 34.257061]]   为要获取poi的矩形框的  左上角和右下角坐标的列表 此处分割了 四个子 rect
    # proxyPools = changeProxy.ChangeProxy(r'./proxy.txt')                        #实例化代理模块 从 ./proxy.txt 文件读取
    proxyPools = getProxyFromProxyPools.ChangeProxy()                              #实例化代理池类
    #amapKey = Keys()  # 初始化Keys 类对象
    #amap_web_key = amapKey.keyCurrent  # 初始值 Key列表
    # amapKey.getKey()                #更换Key

    #rect = [[108.897814, 34.2752], [108.9256255, 34.2661305]]
    #rect = [[108.897814,34.2752], [108.953437,34.257061]]       #定义要获取poi的矩形框的  左上角和右下角坐标的列表 此处分割了 四个子 rect
    getBoundCount = 0                                           #amap 初步计算 一个ip请求30 个 bound 后 ,再取出的 bound值  就完全错乱的 或者说加密了, 此变量就是为了计数


    createTime = arrow.now().format('YYYYMMDDHHmmss')           #创建要保存数据的文件夹
    filePath = os.getcwd() + '\\tab\\' + createTime + '\\'  # 拼接文件夹以当天日期命名
    if os.path.exists(filePath):  # 判断路径是否存在
        print(u"目标已存在:", filePath)  # 如果存在 打印路径已存在,
    else:
        os.makedirs(filePath)  # 如果不存在 创建目录


    rectPoi = GetRectPoi()      #实例化对象
    #print(rectPoi.getPoiBound('B001D09SOI'))
    poiCount =  rectPoi.getPoiID(rect)      #此方法执行完将返回所有分割后的 rect 的 POI信息 将保存在self.pois 列表中
    print(rectPoi.subRectPosCount)                  #分割后所有的子rect 保存在 self.subRectPosCount 属性中
    # WriteToExcel.toExcel(filePath.join('poi.xlsx'), rectPoi.pois)



    ##########################################################以下为创建所有POI 建筑物边界 的 shape图层文件



    boundMap = createShapeFile.CreateMapFeature(filePath)                         #创建map对象
    fieldList = []
    ring = []
    '''
    for fieldName in list(rectPoi.pois[0].keys()) :
        fieldList.append(fieldName[:10],(4,254))                 #fieldList = (("name",(4,254)), ("poiCount",(4,254)), ("rect",(4,254)))      #feature对象对应表的字段的数据类型 4表示字符串 254 为字符串的长度 , fieldName[:10]取fieldName的前十个字符
    '''
    fieldList = [(fieldName[:10],(4,254)) for fieldName in list(rectPoi.pois[0].keys())]           #用列表推导式生成fieldList 可以代替上面的 for 循环
    fieldList = sorted(fieldList)           # fieldList 排序
    dataSource = boundMap.newFile('bound.shp')                                    #创建文件
    boundtLayer = boundMap.createLayer(dataSource, fieldList)                             #创建Layer对象
    for poi in rectPoi.pois :
        fieldValues = []                                        #定义(清空)字段值的列表
        proxyRequest = proxyPools.noProxyIP()                   #首次传入一个无代理的 session对象实例

        '''
       for fieldName in fieldList :                            #生成 字段值的列表
            value = str(poi.get(fieldName[0],'') )                   #此处为 获取 字典poi  key名为 fieldName[0]值的 键值 ,如果没有此 key 则 使用第二个参数代替
            fieldValues.append(value)                           ##将value添加到fieldValues ##!!!!
       '''
        fieldValues = [str(poi.get(x[0], '')) for x in fieldList]           #用列表推导式代替上方的 for 循环 生成 fieldValues 列表

        podId = poi.get('id',False)                              #从'id' 字段获取 poi 的 ID  如果没有 key  'id' 则默认为 ''
        if podId :                                              #如果 podId 存在
            if getBoundCount + 1 % 30 == 0 :
                proxyRequest = proxyPools.changeProxyIP()        #每30次更换一次代理
            ring = rectPoi.getPoiBound(podId,proxyRequest)
            time.sleep(1)
            getBoundCount += 1
            if isinstance(ring,list) :
                boundMap.createPolygon(boundtLayer,[ring],fieldValues)
    ##########################################################为创建所有POI 建筑物边界 的 shape图层文件







    ##########################################################以下为创建所有子矩形框的 shape图层文件
    rectMap = createShapeFile.CreateMapFeature(filePath)                         #创建map对象
    fieldList = [("name",(4,254)), ("poiCount",(4,254)), ("rect",(4,254))]     #feature对象对应表的字段的数据类型 4表示字符串 254 为字符串的长度
    dataSource = rectMap.newFile('rect.shp')                                    #创建文件
    rectLayer = rectMap.createLayer(dataSource, fieldList)                             #创建Layer对象
    for i, subRect in enumerate(rectPoi.subRectPosCount) :                          #循环生成 rect 的  Polygon
        ringList = [rectToPoint(subRect['rect'])]                                   #  ring的坐标对 列表
        fieldValues = ['SubRect_'.join(str(i)), str(subRect['count']), str(subRect['rect']) ]           #Polygon 对应的 表的值
        rectMap.createPolygon(rectLayer, ringList, ('SubRect_'.join(str(i)), str(subRect['count']), str(subRect['rect']) ))  #创建   Polygon  并添加到地图中
    ##########################################################以上为创建所有子矩形框的 shape图层文件



    ##########################################################以下为创建所有POI点 的 shape图层文件
    pointMap = createShapeFile.CreateMapFeature(filePath)                         #创建map对象
    fieldList = []
    for fieldName in list(rectPoi.pois[0].keys()) :
        fieldList.append((fieldName[:10],(4,254)))                   #fieldList = (("name",(4,254)), ("poiCount",(4,254)), ("rect",(4,254)))      #feature对象对应表的字段的数据类型 4表示字符串 254 为字符串的长度
    fieldList = sorted(fieldList)                                   # fieldList 排序

    dataSource = pointMap.newFile('point.shp')                                    #创建文件
    pointLayer = pointMap.createLayer(dataSource, fieldList)                             #创建Layer对象
    for poi in rectPoi.pois :
        fieldValues = []                                        #定义(清空)字段值的列表
        for fieldName in fieldList :                            #生成 字段值的列表
            value = poi.get(fieldName[0],'')                    #此处为 获取 字典poi  key名为 fieldName[0]值的 键值 ,如果没有此 key 则 使用第二个参数代替
            fieldValues.append(value)             ####!!!!
        x = float(poi['location'].split(',')[0])
        y = float(poi['location'].split(',')[1])
        pointMap.createPoint(pointLayer,x,y,fieldValues)
    ##########################################################以上为创建所有POI点 的 shape图层文件






if __name__ == '__main__' :
    #获取经纬度rect 范围内的 高德地图poi 建筑物边界 并生成shp 图形文件
    #   [108.774989,34.41341], [109.149898,34.102978]
    #rect = [[108.897814, 34.2752], [108.9256255, 34.2661305]]       #注意 此处的经纬度 为 GPS经纬度经过偏置后的  高德地图 经纬度
    rect =[[108.924463,34.269687], [108.946908,34.259437]]
    noProxy = requests.session()

    test = GetRectPoi()
    countTest = test.getRectPoiCount(rect,noProxy)
    print(countTest)