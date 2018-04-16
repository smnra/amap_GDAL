# -*- coding:UTF-8 -*-


import pandas as pd
import os
import arrow


class toExcel():
    def __init__(self,fileName):
        now = arrow.now()  # 当前时间
        self.createTime = now.format('YYYYMMDDHHmmss')
        self.filePath = os.getcwd()  +  '\\tab\\' + self.createTime + '\\'        #拼接文件夹以当天日期命名
        if os.path.exists(self.filePath):  # 判断路径是否存在
            print(u"目标已存在:", self.filePath)  # 如果存在 打印路径已存在,
        else:
            os.makedirs(self.filePath)  # 如果不存在 创建目录

    def toExcel(self, fileName, data):
        self.fileName = fileName
        self.pandasData = pd.DataFrame(data)                                    #将普通的 列表转换为 公司小星星
        if os.path.exists(self.filePath):                                                   #判断路径是否存在
            print(u"文件夹已存在:",self.filePath)                                                 #如果存在 打印路径已存在,
        else:
            os.makedirs(self.filePath)                                                           #如果不存在 创建目录
        self.writer = pd.ExcelWriter(self.fileName )       #保存表格为excel      文件名称为本月起始日期_结束日期_LTE.xlsx
        self.pandasData.to_excel(self.writer,'POI数据')                                                                  #保存表格为excel
        self.writer.save()                                                                                   #保存表格为excel