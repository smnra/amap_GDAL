# -*- coding:UTF-8 -*-

import requests
from changeKey import Keys              #导入自定义模块
import time
from cutRect import cutRect, rectToPoint
import createShapeFile
import arrow, os


poi_search_url = "http://restapi.amap.com/v3/place/text"
poi_boundary_url = "https://ditu.amap.com/detail/get/detail"
url = 'http://restapi.amap.com/v3/place/polygon'



class GetRectPoi():
    url = 'http://restapi.amap.com/v3/place/polygon?polygon=108.889573,34.269261;108.924163,34.250959&key=dc44a8ec8db3f9ac82344f9aa536e678&extensions=all&offset=10&page=1'
    # 在此处 polygon 字段为 要取得POI的 矩形框的左上角坐标 和右下角坐标 例如 '108.889573,34.269261;108.924163,34.250959'
    # key 为高德地图的 key 如 : 'dc44a8ec8db3f9ac82344f9aa536e678'
    # extensions 表示 是要获取基本POI  还是全部POI  值为 'base' 或  'all'
    # offset 为 每一页返回的POI 的个数 建议不超过15个 10 个最好 值为 '10'
    # page 为页数  '1'
    headers = {'Upgrade-Insecure-Requests': '1',
               'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
               'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
               'Accept-Encoding': 'gzip, deflate, sdch, br',
               'Accept-Language': 'zh-CN,zh;q=0.8',
               }
    def __init__(self):
        self.sourceRect = ''          #定义源矩形的对象坐标
        self.url = 'http://restapi.amap.com/v3/place/polygon'
        self.urlParams = {'key': 'dc44a8ec8db3f9ac82344f9aa536e678',
                          'polygon': '',                   #self.rectToPolygonStr(rect),
                          'extensions': 'all',
                          'offset': '10',
                          'page': '1' }
        self.subRectPosCount = []       #分割rect后的 信息
        self.createTime = arrow.now().format('YYYYMMDDHHmmss')
        self.filePath = os.getcwd()  +  '\\tab\\' + self.createTime + '\\'        #拼接文件夹以当天日期命名
        self.pois = []

    def add_parameters(self,params, **kwargs):      #将字典中 key  转化为 'key'　
        return params.update(kwargs)

        #>> > params = {}
        #>> > add_parameters(params, f1=1, f2=3, f3=9)
        #>> > params
        #{'f1': 1, 'f2': 3, 'f3': 9}

    def rectToPolygonStr(self, rect) :
        #rect格式为 [[108.889573,34.269261], [108.924163,34.250959]]
        polygon = str(rect[0][0]) + ',' + str(rect[0][1]) + ';' + str(rect[1][0]) + ',' + str(rect[1][1])
        # '108.889573,34.269261;108.924163,34.250959'
        return  polygon

    def setParams(self,keyDict):            #设置url的 参数值
        for key,value in keyDict.items() :              #遍历 keyDict
            if key in self.urlParams :   #如果 keyDict 中的key 在 self.urlParams中存在,
                self.urlParams[key] = value      #把 keyDict 中的value 更新到 self.urlParams 中

    def getRectPoiCount(self,rect):            #接收的参数为 矩形框的 坐标 [[108.889573,34.269261], [108.924163,34.250959]]
        rectParam = {'polygon': self.rectToPolygonStr(rect)}
        self.setParams(rectParam)                               #使用 self.setParams() 方法 更新 'polygon' 字段的值
        try:
            result = requests.get(self.url, params = self.urlParams, timeout = 10, headers = GetRectPoi.headers)
            if result.json()['status'] == '1' :             #在高德地图的api中 'status' 返回  '1' 为正常
                resultJson = result.json()                    #得到json格式的数据
                #poiCount = int(resultJson['count'])          #从 'count' 字段 得到 poi的 个数
                rectPoiCount = {'rect' : rect, 'count': int(resultJson['count'])}         # 把 键值对 {'rect' : rect} 更新到 resultJson
                return rectPoiCount
            elif result.json()['status'] == '6' :           #在高德地图的api中 'status' 返回  '6' 为 'too fast'
                print('too fast, 120s retry!')
                time.sleep(120)                                #暂停120秒后 迭代 本函数
                return self.getRectPoiCount(rect)             #暂停120秒后 迭代 本函数
            elif result.json()['status'] == '0' :            #在高德地图的api中 'status' 返回  '0' 为 'invalid key' key出问题了
                print('invalid key, 3s retry!')             #暂停3秒
                time.sleep(3)
                self.setParams({'key': amapKey.getKey()})      #更换key
                return self.getRectPoiCount(rect)             # 迭代 本函数
            else :
                return 0
        except requests.exceptions.ConnectionError:
            print('ConnectionError -- please wait 3 seconds')
            return -1
        except requests.exceptions.ChunkedEncodingError:
            print('ChunkedEncodingError -- please wait 3 seconds')
            return -2
        except:
            print('Unfortunitely -- An Unknow Error Happened, Please wait 3 seconds')
            return -3

    def getRectPoiNumber(self,rect):                #分割RECT矩形,如果经纬度矩形内的POI个数大于800个 就把此矩形递归的分割成四等份,类似于四叉树,并且返回包含矩形内POI数量和矩形rect的列表
        result = self.getPoi(rect)       #传入的参数为 rect,获取rect范围内的POI数量,
        if  not isinstance(result,int) :          #如果返回值为不为int型(为列表)
            if int(result['count']) > 800 :       #如果返回的poi个数 大于 800
                rects = cutRect(rect)                       #将rect分割为四等份
                for subRect in rects :                      #递归四个子矩形rect
                    self.getRectPoiNumber(subRect)
            elif int(result['count']) <= 800 :        #如果 返回的rect内的POI个数 小于800,
                rectPoiCount = {'rect': rect, 'count': int(result['count'])}            #整理为字典格式的数据  如:{'rect': [[107.889573, 35.269261], [108.406868, 34.76011]], 'count': 367}
                self.subRectPosCount.append(rectPoiCount)       #将返回包含矩形内POI数量和矩形rect的列表 添加到self.subRectPosCount
                return 1                    #返回 1 表示正常
        else :
            print(result)
            return result           #如果返回值为 int, 说明返回的是出错代码 小于1的整数

    def getPoi(self,rect):                                          #返回 poi 的列表
        rectParam = {'polygon': self.rectToPolygonStr(rect)}
        self.setParams(rectParam)  # 使用 self.setParams() 方法 更新 'polygon' 字段的值
        try:
            result = requests.get(self.url, params=self.urlParams, timeout=10, headers=GetRectPoi.headers)
            if result.json()['status'] == '1':  # 在高德地图的api中 'status' 返回  '1' 为正常
                resultJson = result.json()  # 得到json格式的数据
                # poiCount = int(resultJson['count'])          #从 'count' 字段 得到 poi的 个数
                poisPage = resultJson  # 把 键值对 {'rect' : rect} 更新到 resultJson
                return poisPage         #返回 poi 的列表
            elif result.json()['status'] == '6':  # 在高德地图的api中 'status' 返回  '6' 为 'too fast'
                print('too fast, 120s retry!')
                time.sleep(120)  # 暂停120秒后 迭代 本函数
                return self.getPoi(rect)  # 暂停120秒后 迭代 本函数
            elif result.json()['status'] == '0':  # 在高德地图的api中 'status' 返回  '0' 为 'invalid key' key出问题了
                print('invalid key, 3s retry!')  # 暂停3秒
                time.sleep(3)
                self.setParams({'key': amapKey.getKey()})  # 更换key
                return self.getPoi(rect)  # 迭代 本函数
            else:
                return 0
        except requests.exceptions.ConnectionError:
            print('ConnectionError -- please wait 3 seconds')
            return -1
        except requests.exceptions.ChunkedEncodingError:
            print('ChunkedEncodingError -- please wait 3 seconds')
            return -2
        except:
            print('Unfortunitely -- An Unknow Error Happened, Please wait 3 seconds')
            return -3

    def getPoiID(self,rect):
        result = {}
        if self.getRectPoiNumber(rect) == 1 :    #getRectPoiNumber()方法的返回值正常

            if len(self.subRectPosCount) > 0 :      # getRectPoiNumber()  添加到 列表  self.subRectPosCount[] 的元素不为0
                for subRect in self.subRectPosCount:        #遍历每一个子矩形
                    notEnd = True                    #isEnd 如果此页的poi数量小于10 并且 存储poi 的 列表 self.pois 长度 和 网页返回 的 poi数量 result['counter'] 差小于9 则认为此页是最后一页
                    while notEnd:
                        result = self.getPoi(subRect['rect'])           #一个result 就是一页 POI
                        currentPagePoiNumber = len(result['pois'])      #currentPagePoiNumber 当前页的POI的数量
                        if (currentPagePoiNumber - 10 < 0) and  (result['counter']  - len(self.pois) < 9 ) :                 #isEnd 如果此页的poi数量小于10 并且 存储poi 的 列表 self.pois 长度 和 网页返回 的 poi数量 result['counter'] 差小于9 则认为此页是最后一页
                            notEnd = False                              #如果当前页获取到的poi数量小于10 则 认为是最后一页
                        if currentPagePoiNumber > 0:                                   # 如果获取到前页的POI的数量不为0
                            for poi in result['pois'] : #遍历每一个 POI
                                self.pois.append(poi)
                                print(str(poi))
        return  self.pois




if __name__ == '__main__' :
    amapKey = Keys()  # 初始化Keys 类对象
    amap_web_key = amapKey.keyCurrent  # 初始值
    # amapKey.getKey()                #更换Key
    rect = [[107.889573, 35.269261], [108.924163, 34.250959]]
    rectPoi = GetRectPoi()
    poiCount =  rectPoi.getPoiID(rect)      #此方法执行完返回值并不是所有分割后的 rect
    print(rectPoi.subRectPosCount)                  #分割后所有的子rect 保存在 self.subRectPosCount 属性中



    createTime = arrow.now().format('YYYYMMDDHHmmss')
    filePath = os.getcwd() + '\\tab\\' + createTime + '\\'  # 拼接文件夹以当天日期命名
    if os.path.exists(filePath):  # 判断路径是否存在
        print(u"目标已存在:", filePath)  # 如果存在 打印路径已存在,
    else:
        os.makedirs(filePath)  # 如果不存在 创建目录



    rectMap = createShapeFile.CreateMapFeature(filePath)                         #创建map对象
    fieldList = [("name",(4,254)), ("poiCount",(4,254)), ("rect",(4,254))]     #feature对象对应表的字段的数据类型 4表示字符串 254 为字符串的长度
    dataSource = rectMap.newFile('rect.shp')                                    #创建文件
    newLayer = rectMap.createLayer(dataSource, fieldList)                             #创建Layer对象
    for i, subRect in enumerate(rectPoi.subRectPosCount) :                          #循环生成 rect 的  Polygon
        ringList = [rectToPoint(subRect['rect'])]                                   #  ring的坐标对 列表
        fieldValues = ['SubRect_'.join(str(i)), str(subRect['count']), str(subRect['rect']) ]           #Polygon 对应的 表的值
        rectMap.createPolygon(newLayer, ringList, ('SubRect_'.join(str(i)), str(subRect['count']), str(subRect['rect']) ))  #创建   Polygon  并添加到地图中



    pointMap = createShapeFile.CreateMapFeature(filePath)                         #创建map对象

    for fieldName in rectPoi.pois[0].keys() :
        fieldList.append((fieldName,(4,254)))                   #fieldList = (("name",(4,254)), ("poiCount",(4,254)), ("rect",(4,254)))      #feature对象对应表的字段的数据类型 4表示字符串 254 为字符串的长度
    dataSource = pointMap.newFile('point.shp')                                    #创建文件
    pointLayer = pointMap.createLayer(dataSource, fieldList)                             #创建Layer对象
    for poi in rectPoi.pois :
        fieldValues = []                                        #定义(清空)字段值的列表
        for fieldName in fieldList :                            #生成 字段值的列表
            fieldValues.append(str(poi[fieldName]))
        x = float(poi.locate[0])
        y = float(poi.locate[1])
        pointMap.createPoint(pointLayer,x,y,fieldValues)

