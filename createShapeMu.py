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
import shapefile

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


    def createPylgon(self,datas):
        """ 把行字符串列表整理为 可用的数据格式 返回"""
        self.title = datas[0].replace('"','').strip().split(',')

        w = shapefile.Writer(shapefile.POLYGON)
        for title in self.title:
            w.field(title, 'C', '254')


        content = []
        datas.pop(0)
        for i,csvLine in enumerate(datas):
            if csvLine:
                one = csvLine.replace('"','').strip('\n').split(',')
                info = one[:-1]
                strCoordinate = one[-1].split(';')
                Coordinate = [[float(coor) for coor in coordi.split(' ')] for coordi in strCoordinate]
                # 先用";" 分割, 再发分割的每一个元素转化为浮点型

                w.poly(parts=[[Coordinate]], shapeType=shapefile.POLYGON)
                w.record(info + [str(Coordinate)])


                # 创建 shape对象
                if i%10000==0:
                    print(i)
                one.clear()
                info.clear()
        w.save(r'./tab')







if __name__=="__main__":
    csvData = CsvData(r'./grid.csv')
    # 初始化类
    datas = csvData.csvFileRead()
    # 读取csv文件 并返回 行数据列表
    csvData.createPylgon(datas)
    # 整理csv文件 并保存self.data 中
