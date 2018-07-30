#!usr/bin/env python  
#-*- coding:utf-8 _*-  

""" 
@author:Administrator 
@file: get_rings_arcgis.py 
@time: 2018/07/{DAY} 
描述: 描述: 采集 airgis mapserver的建筑物 边界 生成 shape文件 并纠偏经纬度


"""


# -*- coding:UTF-8 -*-

import requests
import time
import createShapeFile
import arrow, os
from createNewDir import createNewDir
from coordinateTranslate import *



poi_search_url = "http://restapi.amap.com/v3/place/text"
#poi_boundary_url = "https://ditu.amap.com/detail/get/detail"
poi_boundary_url = "https://www.amap.com/detail/get/detail"
url = 'http://restapi.amap.com/v3/place/polygon'


ringUrl = 'http://10.249.23.5:6080/arcgis/rest/services/BaseMap/SHAANXIBaseMap/MapServer/find'
'''
#  获取 arcgis rings 的 url
http://10.249.23.5:6080/arcgis/rest/services/BaseMap/SHAANXIBaseMap/MapServer/44/1?f=pjson
http://10.249.23.5:6080/arcgis/rest/services/BaseMap/SHAANXIBaseMap/MapServer/find?searchText=964729&contains=false&searchFields=OBJECTID&sr=&layers=44&layerDefs=&returnGeometry=true&maxAllowableOffset=&geometryPrecision=8&dynamicLayers=&returnZ=false&returnM=false&gdbVersion=&f=html

'''

poiUrl =  'http://10.249.23.5:6080/arcgis/rest/services/POI/SHAANXI/MapServer/find'
'''
#  获取 arcgis  poi 的 url
http://10.249.23.5:6080/arcgis/rest/services/POI/SHAANXI/MapServer/find?searchText=%E5%BB%BA%E7%AD%91%E7%A7%91%E6%8A%80%E5%A4%A7%E5%AD%A6&contains=true&searchFields=&sr=&layers=POI&layerDefs=&returnGeometry=true&maxAllowableOffset=&geometryPrecision=&dynamicLayers=&returnZ=false&returnM=false&gdbVersion=&f=html

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
                          'geometryPrecision': '7',
                          'dynamicLayers': '',
                          'returnZ': 'false',
                          'returnM': 'false',
                          'gdbVersion': '',
                          'f': 'pjson'}

        self.headers = {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
                        'Accept-Encoding': 'gzip,deflate',
                        'Accept-Language': 'zh-CN,zh;q=0.9',
                        'Connection': 'keep-alive',
                        'DNT': '1',
                        'Host': '10.249.23.5:6080',
                        'If-None-Match': 'uMltzax11ZLoicsi_46c7ea75',
                        'Referer': 'http://10.249.23.5:6080/arcgis/rest/services/BaseMap/SHAANXIBaseMap/MapServer/find?searchText=964729&contains=false&searchFields=OBJECTID&sr=&layers=44&layerDefs=&returnGeometry=true&maxAllowableOffset=&geometryPrecision=8&dynamicLayers=&returnZ=false&returnM=false&gdbVersion=&f=html',
                        'Upgrade-Insecure-Requests': '1',
                        'ser-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.162 Safari/537.36 Avast/65.0.411.162'
                        }

        self.ringUrl = 'http://10.249.23.5:6080/arcgis/rest/services/BaseMap/SHAANXIBaseMap/MapServer/find'
        #  获取 arcgis rings 的 url
        self.poiUrl = 'http://10.249.23.5:6080/arcgis/rest/services/POI/SHAANXI/MapServer/find'
        #  获取 arcgis poi 的 url

        self.filePath = ''
        self.rings = []                  #用来保存rings数据的 列表
        self.pois = []                  #用来保存poi数据的 列表

        self.translateGps = GPS()
        self.gcj_wgs = self.translateGps.gcj_decrypt_exact

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


    def getRingJson(self,objectId) :
        # 获取边界的Json信息,转化为字典,并返回
        # Referer = {'Referer': 'http://10.249.23.5:6080/arcgis/rest/services/BaseMap/SHAANXIBaseMap/MapServer/find?contains=false&searchFields=OBJECTID&sr=&layers=44&layerDefs=&returnGeometry=true&maxAllowableOffset=&geometryPrecision=8&dynamicLayers=&returnZ=false&returnM=false&gdbVersion=&f=html&searchText=' + str(objectId)}
        # self.setHeader(Referer)  # 使用 self.setHeader() 方法 更新  RequestHeader 中的 Referer 字段中的 objectId
        searchTextParam = {'searchText': str(objectId)}
        self.setParams(searchTextParam)  # 使用 self.setParams() 方法 更新  requests.get()方法的 附带参数字段 'searchText' 字段的值

        #获取 Arcgis 根据 objectId 查询 建筑物图层(layers=44  44代表建筑物图层) 的 信息
        try:
            result = requests.get(self.ringUrl, params=self.urlParams, timeout=3)
            if result.status_code == 200 :             # 服务器返回状态码 status_code 为 200 则正常
                resultJson = result.json()                    #得到json格式的数据
                return resultJson
        except requests.exceptions.ConnectionError:             # 遇到错误 迭代本方法重新获取
            print('ConnectionError -- please wait 3 seconds')
            return self.getRingJson(objectId)
        except requests.exceptions.ChunkedEncodingError:         # 遇到错误 迭代本方法重新获取
            print('ChunkedEncodingError -- please wait 3 seconds')
            return self.getRingJson(objectId)
        except:                                                  # 遇到错误 迭代本方法重新获取
            print('Unfortunitely -- An Unknow Error Happened.')
            return self.getRingJson(objectId)

    def extractRingInfo(self,resultJson):
        # 将边界的字典信息,拼接为字符串的列表 保存在 self.rings列表中
        # 返回一个字典,key值为 "ringList" 对应的值为 ring的列表,用于 创建 Polygon 的 ring
        # 字典,key值为 "strList" 对应的值为 字符串列表 ,用于对象的字段值.
        # ringTitle = ['OBJECTID', 'Shape', 'Shape_Length', 'wkid', 'rings']
        ring = [None]*6
        try:
            ring[0] = str(resultJson['results'][0]['attributes']['OBJECTID'])
            ring[1] = str(resultJson['results'][0]['attributes']['Shape'])
            ring[2] = str(resultJson['results'][0]['attributes']['Shape_Length'])
            ring[3] = str(resultJson['results'][0]['geometry']['spatialReference']['wkid'])
            ring[4] = ""
            translateRings = self.translateGPSRing(resultJson['results'][0]['geometry']['rings'])  # 把Rings 中的经纬度 GCJ-02 转化为 WGS-84
            for tmpRing in translateRings : # 遍历每一个 ring
                tmpRing = [str(r[0]) + ";" + str(r[1]) for r in tmpRing]      # 把经度和纬度用 ";" 连接为字符串
                if ring[4] :  ring[4] = ring[4] + "&"                         # 如果有多个ring, 就给上一次的ring 后面多加一个 "|"
                ring[4] = ring[4]  + "|".join(tmpRing)                         # 用 "|" 连接每一个经纬度字符串对
            ring[5] = '\n'
            self.rings.append(','.join(ring))
            return {'ringList' : translateRings, 'strList': ring[0:-1]}
        except:
            print('Error,skip!\n',resultJson)
            return 0

    def ringToCsv(self,fileName,i):
        with open(fileName, 'a+') as f:
            if i<= 500 : f.writelines(','.join(['OBJECTID', 'Shape', 'Shape_Length', 'wkid', 'rings','\n']))
            f.writelines(self.rings)


    def translateGPSRing(self,rings):
        # 参数为rings的经纬度列表 如 :<class 'list'>: [[[106.847484, 34.896459], [106.847566, 34.89651], [106.847605, 34.896461], [106.847523, 34.89641], [106.847484, 34.896459]]]
        # 返回值为 GCJ-02 to WGS-84 转换结果
        for ring in rings:
            for r in ring:
                gcjlon = float(r[0])
                gcjlat = float(r[1])
                wgs = self.translateGps.gcj_decrypt_exact(gcjlat,gcjlon)
                r[0] = round(wgs['lon'],8)
                r[1] = round(wgs['lat'],8)
        return rings







if __name__ == '__main__' :
    # 获取arcgis 的 建筑物Feature ID 从0-10000000
    # 获取arcgis 的 建筑物Feature ID 从0-10000000

    arcgisObject = GetArcgisObgect()  # 初始化对类
    arcgisObject.filePath = createNewDir()  # 创建文件夹
    boundMap = createShapeFile.CreateMapFeature(arcgisObject.filePath)  # 创建map对象
    fieldList = [['OBJECTID', (4,254)], ['Shape', (4,254)], ['Shape_Length'[0:8], (4,254)], ['wkid', (4,254)], ['rings', (4,2048)]]
    # 创建字段的数据类型 列表
    dataSource = boundMap.newFile('bound.shp')  # 初始化数据源,也就是地图文件
    boundLayer = boundMap.createLayer(dataSource, fieldList)    # 创建Layer对象


    for i in range(1, 964729):                       # 根据objectid 提取建筑物边界对象的信息   共 964729  个建筑物
        resultJson = arcgisObject.getRingJson(i)     # 获取边界的Json信息,转化为字典,
        if resultJson['results'][0]['geometry']['rings'][0]:                  # 如果字典存在'ring'字段,
            ring = arcgisObject.extractRingInfo(resultJson)     #  拼接为字符串的列表 保存在 self.rings列表中 返回值 为rings的列表
            boundMap.createPolygon(boundLayer, ring['ringList'], ring['strList'])
            # print(i, ring['strList'][-1])

        if i % 500 == 0:  # 每500个保存一次
            arcgisObject.ringToCsv(arcgisObject.filePath + 'rings.csv',i)
            arcgisObject.rings = []
            print("%s rings complated." % (str(i)))
    arcgisObject.ringToCsv(arcgisObject.filePath + 'rings.csv',i)








