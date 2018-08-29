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
            with open(self.csvFileName, 'r', errors=None) as f:  #
                csvData = f.readlines()
                return csvData
        else:
            print(self.csvFileName, "File Not Found,Please Check!")
            sys.exit()


    def clearUpData(self,csvData):
        """ 把行字符串列表整理为 可用的数据格式 返回"""
        self.title = csvData[0].strip().split(',')
        content = []
        csvData.pop(0)
        for csvLine in csvData:
            if csvLine:
                one = csvLine.split('"')
                info = one[0].split(',')[:-1]
                strCoordinate = one[1].split(',')
                Coordinate = [[float(coor) for coor in coordi.split(';')] for coordi in strCoordinate]
                # 先用";" 分割, 再发分割的每一个元素转化为浮点型
                info.append(Coordinate)
                content.append(list(info))
                one.clear()
                info.clear()
        self.dataList = list(content)

if __name__=="__main__":
    csvData = CsvData(r'./grid.csv')
    # 初始化类
    data = csvData.csvFileRead()
    # 读取csv文件 并返回 行数据列表
    csvData.clearUpData(data)
    # 整理csv文件 并保存self.data 中


    newMap = CreateMapFeature(csvData.path)
    # 初始化类
    fieldList = [(title[:8],(4,254)) for title in csvData.title]
    # (("index", (4, 254)), ("name", (4, 254)), ("lon", 2), ("lat", 2))
    # 生成 字段列表
    dataSource = newMap.newFile('pylgon.shp')
    #创建shape文件
    newLayer = newMap.createLayer(dataSource, fieldList)
    #创建 图层Layer 对象

    for data in csvData.dataList:
        """ 生成多边形"""
        newMap.createPolygon(newLayer,[data[-1]],data[:-1]+[str(data[-1])])

