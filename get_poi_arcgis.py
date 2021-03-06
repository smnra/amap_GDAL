#!usr/bin/env python  
#-*- coding:utf-8 _*-  

""" 
@author:Administrator 
@file: get_rings_arcgis.py
@time: 2018/07/{DAY}
描述: 采集 airgis mapserver poi 生成 shape文件 并纠偏经纬度

"""


# -*- coding:UTF-8 -*-

import requests
import time
import createShapeFile
from createNewDir import createNewDir
from coordinateTranslate import *



poi_search_url = "http://restapi.amap.com/v3/place/text"
#poi_boundary_url = "https://ditu.amap.com/detail/get/detail"
poi_boundary_url = "https://www.amap.com/detail/get/detail"
url = 'http://restapi.amap.com/v3/place/polygon'


ringUrl = 'http://10.249.23.5:6080/arcgis/rest/services/BaseMap/SHAANXIBaseMap/MapServer/find'
'''
#  获取 arcgis rings 的 url
http://10.249.23.5:6080/arcgis/rest/services/BaseMap/SHAANXIBaseMap/MapServer/find?searchText=964729&contains=false&searchFields=OBJECTID&sr=&layers=44&layerDefs=&returnGeometry=true&maxAllowableOffset=&geometryPrecision=8&dynamicLayers=&returnZ=false&returnM=false&gdbVersion=&f=html

'''

poiUrl =  'http://10.249.23.5:6080/arcgis/rest/services/POI/SHAANXI/MapServer/0/57198?f=pjson'
'''
#  获取 arcgis  poi 的 url
http://10.249.23.5:6080/arcgis/rest/services/POI/SHAANXI/MapServer/0/57198?f=pjson
'''





class GetArcgisObgect():
    headers = { 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
                'Accept-Encoding': 'gzip,deflate',
                'Accept-Language': 'zh-CN,zh;q=0.9',
                'Connection': 'keep-alive',
                'DNT': '1',
                'Host': '10.249.23.5:6080',
                'If-None-Match': 'uMltzax11ZLoicsi_46c7ea75',
                'Referer': 'http://10.249.23.5:6080/arcgis/rest/services/BaseMap/SHAANXIBaseMap/MapServer/find?searchText=1&contains=false&searchFields=OBJECTID&sr=&layers=44&layerDefs=&returnGeometry=true&maxAllowableOffset=&geometryPrecision=8&dynamicLayers=&returnZ=false&returnM=false&gdbVersion=&f=html',
                'Upgrade-Insecure-Requests': '1',
                'ser-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.162 Safari/537.36 Avast/65.0.411.162'
                }

    def __init__(self):
        self.urlParams = {'searchText': '',
                          'contains': 'false',
                          'searchFields': 'OBJECTID',
                          'sr': '',
                          'layers': '44',
                          'layerDefs': '',
                          'returnGeometry': 'true',
                          'maxAllowableOffset': '',
                          'geometryPrecision': '10',
                          'dynamicLayers': '',
                          'returnZ': 'false',
                          'returnM': 'false',
                          'gdbVersion': '',
                          'f': 'pjson'}

        self.ringUrl = 'http://10.249.23.5:6080/arcgis/rest/services/BaseMap/SHAANXIBaseMap/MapServer/find'
        #  获取 arcgis rings 的 url
        self.poiUrl =  'http://10.249.23.5:6080/arcgis/rest/services/POI/SHAANXI/MapServer/0/57198?f=pjson'
        #  获取 arcgis poi 的 url

        self.translateGps = GPS()
        self.gcj_wgs = self.translateGps.gcj_decrypt_exact

        self.filePath = ''
        self.rings = []                  #用来保存rings数据的 列表
        self.pois = []                  #用来保存poi数据的 列表

    def add_parameters(self,params, **kwargs):
        #将字典中 key  转化为 'key'　
        return params.update(kwargs)
        #>> > params = {}
        #>> > add_parameters(params, f1=1, f2=3, f3=9)
        #>> > params
        #{'f1': 1, 'f2': 3, 'f3': 9}

    def setParams(self,keyDict):
        #设置requests.get() 方法 url附带的的 参数
        for key,value in keyDict.items() :              #遍历 keyDict
            if key in self.urlParams :   #如果 keyDict 中的key 在 self.urlParams中存在,
                self.urlParams[key] = value      #把 keyDict 中的value 更新到 self.urlParams 中

    def setHeader(self,keyDict):
        #设置requests.get() 方法 url附带的的 参数
        for key,value in keyDict.items() :              #遍历 keyDict
            if key in self.headers :   #如果 keyDict 中的key 在 self.urlParams中存在,
                self.headers[key] = value      #把 keyDict 中的value 更新到 self.urlParams 中


    def getPoiJson(self,objectId) :
        #获取 Arcgis 根据 objectId 查询 建筑物图层(layers=44  44代表建筑物图层) 的 信息
        self.poiUrl =  'http://10.249.23.5:6080/arcgis/rest/services/POI/SHAANXI/MapServer/0/' + str(objectId)

        try:
            result = requests.get(self.poiUrl, params={'f': 'pjson'}, timeout=3)
            if result.status_code == 200 :             # 服务器返回状态码 status_code 为 200 则正常
                resultJson = result.json()                    #得到json格式的数据
                return resultJson
        except requests.exceptions.ConnectionError:
            print('ConnectionError -- please wait 3 seconds')
            time.sleep(1)
            return self.getPoiJson(objectId)
        except requests.exceptions.ChunkedEncodingError:
            print('ChunkedEncodingError -- please wait 3 seconds')
            time.sleep(1)
            return self.getPoiJson(objectId)
        except:
            print('Unfortunitely -- An Unknow Error Happened.')
            time.sleep(1)
            return self.getPoiJson(objectId)

    def extractRingInfo(self,resultJson):
        # poiTitle = ['ADDRESS', 'CODE', 'CTYPE', 'LABEL', 'NAME', 'NAME_PY', 'NTYPE', 'OBJECTID', 'TELEPHONE', 'x', 'y','\n']
        poi = [None]*12
        try:
            poi[0] = str(resultJson['feature']['attributes']['ADDRESS']).replace(',','_')
            poi[1] = str(resultJson['feature']['attributes']['CODE'])
            poi[2] = str(resultJson['feature']['attributes']['CTYPE'])
            poi[3] = str(resultJson['feature']['attributes']['LABEL']).replace(',','_')
            poi[4] = str(resultJson['feature']['attributes']['NAME']).replace(',','_')
            poi[5] = str(resultJson['feature']['attributes']['NAME_PY'])
            poi[6] = str(resultJson['feature']['attributes']['NTYPE'])
            poi[7] = str(resultJson['feature']['attributes']['OBJECTID'])
            poi[8] = str(resultJson['feature']['attributes']['TELEPHONE'])
            point = [float(resultJson['feature']['geometry']['x']), float(resultJson['feature']['geometry']['y'])]
            point = self.translateGPSPoint(point)
            poi[9] = str(point[0])
            poi[10] = str(point[1])
            poi[11] = '\n'
            self.pois.append(','.join(poi))
            return  poi[0:-1]
        except:
            print('Error,skip!\n',resultJson)
            return 0


    def poiToCsv(self,fileName,i):
        with open(fileName, 'a+') as f:
            if i <= 500: f.writelines(','.join(['ADDRESS', 'CODE', 'CTYPE', 'LABEL', 'NAME', 'NAME_PY', 'NTYPE', 'OBJECTID', 'TELEPHONE', 'x', 'y','\n']))
            f.writelines(self.pois)

    def translateGPSPoint(self,point):
        # 参数为list 的经纬度列表 如 :<class 'list'>: [106.847484, 34.896459]
        #  返回值为 GCJ-02 to WGS-84 转换结果
        wgs = self.translateGps.gcj_decrypt_exact(point[1],point[0])
        return [wgs['lon'], wgs['lat']]





if __name__ == '__main__' :
    # 获取arcgis 的 建筑物Feature ID 从0-10000000
    arcgisObject = GetArcgisObgect()                #初始化对类
    arcgisObject.filePath = createNewDir()  # 创建文件夹

    pointMap = createShapeFile.CreateMapFeature(arcgisObject.filePath)  # 创建map对象
    fieldList = [['ADDRESS'[0:8], (4,254)], ['CODE', (4,254)], ['CTYPE', (4,254)], ['LABEL', (4,254)], ['NAME', (4,254)], ['NAME_PY', (4,254)],['NTYPE', (4,254)], ['OBJECTID'[0:8], (4,254)], ['TELEPHONE'[0:8], (4,254)], ['x', (4,254)], ['y', (4,254)]]
    # 创建字段的数据类型 列表
    dataSource = pointMap.newFile('point.shp')  # 初始化数据源,也就是地图文件
    pointLayer = pointMap.createLayer(dataSource, fieldList)    # 创建Layer对象



    for i in range(1,571980):                      # 共 571980 个 objectid
        resultJson = arcgisObject.getPoiJson(i)
        if resultJson:
            point = arcgisObject.extractRingInfo(resultJson)
            pointMap.createPoint(pointLayer, point[-2], point[-1], point)

        if i%500==0:                               #每500个保存一次
            arcgisObject.poiToCsv(arcgisObject.filePath + 'pois.csv', i)
            arcgisObject.pois = []
            print("%s pois complated." % (str(i)))
    arcgisObject.poiToCsv(arcgisObject.filePath + 'pois.csv', i)