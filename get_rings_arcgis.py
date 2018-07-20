#!usr/bin/env python  
#-*- coding:utf-8 _*-  

""" 
@author:Administrator 
@file: get_rings_arcgis.py 
@time: 2018/07/{DAY} 
描述: 

"""


# -*- coding:UTF-8 -*-

import requests
import time
import createShapeFile
import arrow, os
from createNewDir import createNewDir
import geoOperation



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
                          'geometryPrecision': '10',
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
        except requests.exceptions.ConnectionError:
            print('ConnectionError -- please wait 3 seconds')
            return -1
        except requests.exceptions.ChunkedEncodingError:
            print('ChunkedEncodingError -- please wait 3 seconds')
            return -2
        except:
            print('Unfortunitely -- An Unknow Error Happened.')
            return -3

    def extractRingInfo(self,resultJson):
        # ringTitle = ['OBJECTID', 'Shape', 'Shape_Length', 'wkid', 'rings']
        ring = [None]*6
        try:
            ring[0] = str(resultJson['results'][0]['attributes']['OBJECTID'])
            ring[1] = str(resultJson['results'][0]['attributes']['Shape'])
            ring[2] = str(resultJson['results'][0]['attributes']['Shape_Length'])
            ring[3] = str(resultJson['results'][0]['geometry']['spatialReference']['wkid'])
            tmpRings = resultJson['results'][0]['geometry']['rings'][0]
            tmpRings = [str(tmpRing[0]) + ";" + str(tmpRing[1]) for tmpRing in tmpRings]
            ring[4] = "|".join(tmpRings)
            ring[5] = '\n'
            self.rings.append(','.join(ring))
        except:
            print('Error,skip!\n',resultJson)
            time.sleep(1)
            return 0

    def ringToCsv(self,fileName):
        with open(fileName, 'a+') as f:
            f.writelines(','.join(['OBJECTID', 'Shape', 'Shape_Length', 'wkid', 'rings','\n']))
            f.writelines(self.rings)


if __name__ == '__main__' :
    # 获取arcgis 的 建筑物Feature ID 从0-10000000
    arcgisObject = GetArcgisObgect()                #初始化对类
    arcgisObject.filePath = createNewDir()  # 创建文件夹
    for i in range(1,964729):
        resultJson = arcgisObject.getRingJson(i)
        if resultJson: arcgisObject.extractRingInfo(resultJson)
        #print(i)
        if i%500==0:                               #每500个保存一次
            arcgisObject.ringToCsv('E:\\工具\\资料\\宝鸡\\研究\\Python\\python3\\amap_GDAL\\tab\\' + 'rings.csv')
            arcgisObject.rings = []
            print("%s rings complated." % (str(i)))
    arcgisObject.ringToCsv('E:\\工具\\资料\\宝鸡\\研究\\Python\\python3\\amap_GDAL\\tab\\' + 'rings.csv')
