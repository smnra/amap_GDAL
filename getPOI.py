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

    def setParams(self,keyDict):
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
                return self.getRectPoi(rect)             #暂停120秒后 迭代 本函数
            elif result.json()['status'] == '0' :            #在高德地图的api中 'status' 返回  '0' 为 'invalid key' key出问题了
                print('invalid key, 3s retry!')             #暂停3秒
                time.sleep(3)
                self.setParams({'key': amapKey.getKey()})      #更换key
                return self.getRectPoi(rect)             # 迭代 本函数
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

    def getRectPoiNumber(self,rect):
        rectPoiCount = self.getRectPoiCount(rect)
        if  not isinstance(rectPoiCount,int) :
            if int(rectPoiCount['count']) > 800 :
                rects = cutRect(rect)
                for subRect in rects :
                    self.getRectPoiNumber(subRect)
            elif int(rectPoiCount['count']) <= 800 :
                self.subRectPosCount.append(rectPoiCount)
                return self.subRectPosCount
        else :
            return rectPoiCount







if __name__ == '__main__' :
    amapKey = Keys()  # 初始化Keys 类对象
    amap_web_key = amapKey.keyCurrent  # 初始值
    # amapKey.getKey()                #更换Key
    rect = [[107.889573, 35.269261], [108.924163, 34.250959]]
    rectPoi = GetRectPoi()
    poiCount =  rectPoi.getRectPoiNumber(rect)
    print(rectPoi.subRectPosCount)

    createTime = arrow.now().format('YYYYMMDDHHmmss')
    filePath = os.getcwd() + '\\tab\\' + createTime + '\\'  # 拼接文件夹以当天日期命名
    if os.path.exists(filePath):  # 判断路径是否存在
        print(u"目标已存在:", filePath)  # 如果存在 打印路径已存在,
    else:
        os.makedirs(filePath)  # 如果不存在 创建目录

    newMap = createShapeFile.CreateMapFeature(filePath)
    fieldList = (("name",(4,254)), ("poiCount",(4,254)), ("rect",(4,254)))
    dataSource = newMap.newFile('polygon.shp')
    newLayer = newMap.createLayer(dataSource, fieldList)
    for i, subRect in enumerate(rectPoi.subRectPosCount) :
        ringList = [rectToPoint(subRect['rect'])]
        fieldValues = ('SubRect_'.join(str(i)), str(subRect['count']), str(subRect['rect']) )
        newMap.createPolygon(newLayer, ringList, ('SubRect_'.join(str(i)), str(subRect['count']), str(subRect['rect']) ))