#!usr/bin/env python  
#-*- coding:utf-8 _*-  

""" 
@author:SMnRa
@file: shapeMake.py 
@time: 2018/08/{DAY} 
描述: 从csv文件读取表格 并使用GDAL库创建 多边形 shape文件

"""
import os,sys
from createShapeFile import *
from createNewDir import *
class CsvData():
    def __init__(self,csvFileName):
        self.csvFileName = csvFileName
        self.path = createDir(r'./tab')
        self.title = []
        self.dataList = []


    def csvFileRead(self):
        """ 读取 csv 文件 返回 行字符串列表"""
        if os.path.isfile(self.csvFileName):
            with open(self.csvFileName, 'r', encoding='utf-8', errors=None) as f:  #
                csvData = f.readlines()
                return csvData
        else:
            print(self.csvFileName, "File Not Found,Please Check!")
            sys.exit()

    def newMapFile(self,i):
        newMap = CreateMapFeature(self.path)
        # 初始化类
        fieldList = [(title[:8], (4, 254)) for title in self.title]
        # (("index", (4, 254)), ("name", (4, 254)), ("lon", 2), ("lat", 2))
        # 生成 字段列表
        dataSource = newMap.newFile('pylgon' + str(i) +'.shp')
        # 创建shape文件
        newLayer = newMap.createLayer(dataSource, fieldList)
        # 创建 图层Layer 对象



    def createPylgon(self,datas):
        """ 把行字符串列表整理为 可用的数据格式 返回"""
        self.title = datas[0].replace('"','').strip().split(',')

        newMap = CreateMapFeature(self.path)
        # 初始化类
        fieldList = [(title[:8], (4, 254)) for title in self.title]
        # (("index", (4, 254)), ("name", (4, 254)), ("lon", 2), ("lat", 2))
        # 生成 字段列表
        dataSource = newMap.newFile('pylgon.shp')
        # 创建shape文件
        newLayer = newMap.createLayer(dataSource, fieldList)
        # 创建 图层Layer 对象


        content = []
        datas.pop(0)
        for i,csvLine in enumerate(datas):
            if csvLine:
                one = csvLine.replace('"','').strip('\n').split(',')
                info = one[:-1]
                strCoordinate = one[-1].split(';')
                Coordinate = [[float(coor) for coor in coordi.split(' ')] for coordi in strCoordinate]
                # 先用";" 分割, 再发分割的每一个元素转化为浮点型

                newMap.createPolygon(newLayer, [Coordinate], info + [str(Coordinate)])
                # 创建 shape对象
                if i%1000000==0:
                    newMap = CreateMapFeature(self.path)
                    # 初始化类
                    fieldList = [(title[:8], (4, 254)) for title in self.title]
                    # (("index", (4, 254)), ("name", (4, 254)), ("lon", 2), ("lat", 2))
                    # 生成 字段列表
                    dataSource = newMap.newFile('pylgon' + str(i) + '.shp')
                    # 创建shape文件
                    newLayer = newMap.createLayer(dataSource, fieldList)
                    # 创建 图层Layer 对象

                    print(i)

                one.clear()
                info.clear()


if __name__=="__main__":
    csvData = CsvData(r'./mi10.csv')
    # 初始化类
    datas = csvData.csvFileRead()
    # 读取csv文件 并返回 行数据列表
    csvData.createPylgon(datas)
    # 整理csv文件 并保存self.data 中
