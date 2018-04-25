#!/usr/bin/python
# -*- coding: CP936 -*-


import sys
import os
import osr
try:
    from osgeo import ogr,gdal
except:
    import ogr



# 在GDAL 中 feature 指的就是 mapinfo中的 点 线 折线  区域等
#driver = ogr.GetDriverByName("ESRI Shapefile")    # .shp 文件驱动
#driver = ogr.GetDriverByName("Mapinfo File")      # mapinfo   .tab 文件驱动


testSR = osr.SpatialReference()
testSR.SetWellKnownGeogCS("WGS84")
print(testSR.ExportToPrettyWkt())
testSR.ImportFromEPSG(4326)#returns 6
                                        #设置坐标系投影

gdal.SetConfigOption("GDAL_FILENAME_IS_UTF8", "YES")
# 读取字段属性值时设置，否则有中文乱码
gdal.SetConfigOption("SHAPE_ENCODING","UTF8")


class CreateMapFeature():
    def __init__(self,path):
        self.path = path
        self.driver = ogr.GetDriverByName("ESRI Shapefile")  # .shp 文件驱动
        #self.driver = ogr.GetDriverByName("Mapinfo File")  # mapinfo   .tab 文件驱动

    def createLayer(self, dataSource, fieldList):
        self.dataSource = dataSource                        #创建的图形文件的 dataSource
        self.fieldList = fieldList                      #fieldList ,图层的表格字段  列表格式,(("index", 0), ("name",(4,255)), ("lon", 2), ("lat" , 2))
                                                        # 列表为 字段的名字 和 数据类型, 0代表整数 , 2 代表 浮点数 , 4代表字符串(如果是字符串格式 则列表的第二个元素为 4和字符串的长度的列表        self.layerName = layerName                      #创建图层 Layer 的 名字
        self.newLayer = self.dataSource.CreateLayer('newLayer')  # 创建图层 layerName
        for self.field in self.fieldList:                 #创建字段名字典中的所有字段
            if self.field[1] == 0 :
                self.fieldType = ogr.OFTInteger
                self.newField = ogr.FieldDefn(self.field[0], self.fieldType)  # 添加一个新字段
            elif self.field[1] == 2 :
                self.fieldType = ogr.OFTReal
                self.newField = ogr.FieldDefn(self.field[0], self.fieldType)  # 添加一个新字段
            elif self.field[1][0] == 4 :
                self.fieldType = ogr.OFTString
                self.newField = ogr.FieldDefn(self.field[0], self.fieldType)  # 添加一个新字段
                self.newField.SetWidth(self.field[1][1])          #如果新字段是字符串类则必须要指定宽度
            self.newLayer.CreateField(self.newField)  # 将新字段指配到layer
        return  self.newLayer                           # 返回值为新建文件的图层 Layer 对象



    def newFile(self, filename):
        #创建新文件
        self.filename = filename                        #filename文件名,不包含路径 字符串格式
        if os.path.isfile(self.path + self.filename):  # 如果文件存在的话 重新起一个文件名
            self.filename = self.path + r"/new_" + self.filename
            print("File is exist,Create anothor, Name is :" + self.filename)
        else:
            self.filename = self.path + self.filename
            print("Create file, Name is :" + self.filename)

        self.dataSource = self.driver.CreateDataSource(self.filename)        # 创建 文件
        return  self.dataSource                           # 返回值为新建文件的dataSource 对象

    def deleteFile(self, filename):
        self.filename = filename
        self.filename = self.path + self.filename
        if os.path.isfile(self.filename):  # 如果文件存在的话删除
            self.driver.DeleteDataSource(self.filename)  # 删除一个文件
            print("File well be delete :" + self.filename)
        else:
            print("File is not exist :" + self.filename + ",Plase Check it!")

    def setFieldValue(self,newLayer,fieldList,valueList):     #newLayer 为 图层 fieldList 为 列名列表, valueList为字段值列表
        self.newLayer = newLayer
        self.fieldList = fieldList
        self.valueList = valueList
        for self.tmpField,self.tmpValue  in zip(self.fieldList, self.valueList) :
            #设定Featur某字段的数值,这里设置 index 字段的值为 12
            if isinstance(self.tmpField, int) :
                self.newFeature.SetField(self.tmpField[0], self.tmpValue)
            else :
                self.newFeature.SetField(self.tmpField[0], toStr(self.tmpValue))

    def createPoint(self, newLayer, x, y, fieldValues = []):        #layer 为要将Feature添加到的 Layer x ,y 为 坐标 values 为字段值列表
        self.newLayer = newLayer
        self.x = x
        self.y = y
        self.fieldValues = fieldValues
        # 添加一个新的Feature
        self.featureDefn = self.newLayer.GetLayerDefn()  # 获取Feature 的类型
        self.newFeature = ogr.Feature(self.featureDefn)  # 创建Feature
        # 设定几何形状
        self.point = ogr.Geometry(ogr.wkbPoint)  # 创建一个点
        self.point.AddPoint(float(self.x), float(self.y))  # 设置 point的坐标
        self.newFeature.SetGeometry(self.point)  # 设置Featur的几何形状为point
        self.setFieldValue(self.newLayer, self.fieldList, self.fieldValues)
        # 将newFeature写入 self.layer
        self.newLayer.CreateFeature(self.newFeature)
        self.point.Destroy()  # 释放对象内存
        return  self.newFeature                  # 返回值为Feature 对象

    def createLine(self, newLayer,pointList, fieldValues = []):           #layer 为要将Feature添加到的 Layer , points 为折线的节点x,y坐标的列表如 :((1,1),(3,3),(4,2))
        self.newLayer = newLayer
        self.pointList = pointList
        self.fieldValues = fieldValues
        # 添加一个新的Feature
        self.featureDefn = self.newLayer.GetLayerDefn()  # 获取Feature 的类型
        self.newFeature = ogr.Feature(self.featureDefn)  # 创建Feature
        # 设定几何形状
        self.line = ogr.Geometry(ogr.wkbLineString)  # 创建一条折线
        for self.pointPos in self.pointList :
            self.line.AddPoint(float(self.pointPos[0]), float(self.pointPos[1]))  # 循环添加所有的节点
        self.newFeature.SetGeometry(self.line)  # 设置Featur的几何形状为line
        #设定Featur某字段的数值,这里设置 index 字段的值为 12
        self.setFieldValue(self.newLayer, self.fieldList, self.fieldValues)
        # 将newFeature写入 self.layer
        self.newLayer.CreateFeature(self.newFeature)
        self.line.Destroy()  # 释放对象内存
        return  self.newFeature                  # 返回值为Feature 对象

    def createPolygon(self, newLayer,ringList, fieldValues = []):           #layer 为要将Feature添加到的 Layer ,
        self.newLayer = newLayer                              #rings 为封闭的折线ring 的列表,可以有1个或者2个元素(内环和外环)
        self.ringList = ringList                   #如:1个环:((0,0),(0,10),(10,10),(10,0))     2个环: (((0,0),(0,10),(10,10),(10,0)),((2.5,2.5),(7.5,2.5),(7.5,7.5),(2.5,7.5)))
        self.fieldValues = fieldValues
        # 添加一个新的Feature
        self.featureDefn = self.newLayer.GetLayerDefn()  # 获取Feature 的类型
        self.newFeature = ogr.Feature(self.featureDefn)  # 创建Feature
        # 设定几何形状
        self.polygon = ogr.Geometry(ogr.wkbPolygon)  # 创建polygon区域
        self.ring = []      #定义ring的列表
        for i,self.ringPos in enumerate(self.ringList) :
            self.ring.append(ogr.Geometry(ogr.wkbLinearRing)) # 创建一个环 ring 并添加到列表 self.ring 中
            for self.tmpRing in self.ringPos :
                self.ring[i].AddPoint(float(self.tmpRing[0]), float(self.tmpRing[1]))  #循环添加点到Ring中
            if self.ringPos[0] != self.ringPos[-1] : #如果ring的第一个元素和最后一个元素不相等
                self.ring[i].CloseRings()  # 用CloseRings闭合Ring，
            self.polygon.AddGeometry(self.ring[i])   # 把环 ring添加到  polygon
        self.newFeature.SetGeometry(self.polygon)   #设置Featur的几何形状为polygon (设置newFeature 为 区域 polygon )
        #设定Featur某字段的数值,这里设置 index 字段的值为 12
        self.setFieldValue(self.newLayer, self.fieldList,self.fieldValues)
        # 将newFeature写入 self.layer
        self.newLayer.CreateFeature(self.newFeature)
        self.polygon.Destroy()  # 释放对象内存
        return  self.newFeature                  # 返回值为Feature 对象

    def close(self,layer):
        layer.ResetReading()  # 复位
        self.dataSource.Destroy()  # 关闭数据源，相当于文件系统操作中的关闭文件

    def isInvalidBound(self, pointList):
        # 根据传入的列表  创建相邻两个元素的 直线(也就是 多边形的每一条边), 添加到 lines 列表中 ,再分别判断这些直线是否 交叉 Crosses
        lines = []
        for i in range(len(pointList) - 1):
            line = ogr.Geometry(ogr.wkbLineString)  # 创建一条折线
            line.AddPoint(float(pointList[i][0]), float(pointList[i][1]))  # 直线的第一个点
            line.AddPoint(float(pointList[i + 1][0]), float(pointList[i + 1][1]))  # 直线的第二个点
            lines.append(line)  # 添加到列表中

        line = ogr.Geometry(ogr.wkbLineString)  # 创建最后一个点和第一个点的直线
        line.AddPoint(float(pointList[-1][0]), float(pointList[-1][1]))
        line.AddPoint(float(pointList[0][0]), float(pointList[0][1]))
        lines.append(line)

        for i in range(len(lines)):  # 遍历每一条直线
            for j in range(i, len(lines)):
                if lines[i].Crosses(lines[j]):  # 判断其他直线与这条直线是否交叉
                    return True  # 如果交叉 返回True
        return False  # 默认返回False

        '''
        if __name__ =='__main__':
            boundPoints = [(0, 0), (0, 5), (5, 5), (5,0), (-2,3), (6, 6)]
            newGeo = CreateMapFeature()
            isCross = newGeo.isInvalidBound(boundPoints)
            print(isCross)

        '''


def toStr(var_to_str) :
    if isinstance(var_to_str, list) or isinstance(var_to_str, tuple) :
        if len(var_to_str) >=1 :
            return toStr(var_to_str[0])
        else:
            return ''
    elif isinstance(var_to_str, dict) :
        return toStr(list(var_to_str.values())[0])
    else:
        return str(var_to_str)



if __name__ == '__main__':
    newMap = CreateMapFeature('E:\\工具\\资料\\宝鸡\\研究\\Python\\python3\\gaode_range\\tab\\')
    fieldList = (("index",(4,254)), ("name",(4,254)), ("lon", 2), ("lat" , 2))

    #注意 shape 的结构与 mapinfo的图层结构可能有所不同,mapinfo一个图层Layer中可以包含多种Feature(点,线 面).
    # 但是一个shape 的 Layer只能有一种 Frature 否则会报错 ERROR 1: Attempt to write non-point (POLYGON) geometry to point shapefile.

    dataSource = newMap.newFile('point.shp')                                        #创建shape文件
    newLayer = newMap.createLayer(dataSource, fieldList)                              #创建 图层Layer 对象
    newMap.createPoint(newLayer, 10, 10,("无啥电视","阿萨斯阿萨德",23.5,102.55))     #创建 点 Feature 并设置字段值
    newMap.createPoint(newLayer, 10, 15,("无啥电视","阿萨斯阿萨德",23.6,102.65))
    newMap.createPoint(newLayer, 10, 17,("无啥电视","阿萨斯阿萨德",23.7,102.75))
    newMap.createPoint(newLayer, 10, 18,("无啥电视","阿萨斯阿萨德",23.8,102.85))

    dataSource = newMap.newFile('polygon.shp')
    newLayer = newMap.createLayer(dataSource, fieldList)
    newMap.createPolygon(newLayer,(((0, 0), (0, 10), (10, 10), (10, 0)), ((2.5, 2.5), (7.5, 2.5), (7.5, 7.5), (2.5, 7.5))),("无啥电视","阿萨斯阿萨德",23.8,102.85))

    dataSource = newMap.newFile('line.shp')
    newLayer = newMap.createLayer(dataSource, fieldList)
    newMap.createLine(newLayer,[(0,0),(3,4),(5,6),(7,8)], ("无啥电视","阿萨斯阿萨德",23.8,102.85))
    newMap.createLine(newLayer,[(10,10),(8,9),(7,6),(3,5)], ("无啥电视","阿萨斯阿萨德",23.8,102.85))


    newMap.close(newLayer)