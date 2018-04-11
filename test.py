#!/usr/bin/python
# -*- coding: utf-8 -*-


import sys
import os
import osr
try:
    from osgeo import ogr
except:
    import ogr

# 在GDAL 中 feature 指的就是 mapinfo中的 点 线 折线  区域等
#driver = ogr.GetDriverByName("ESRI Shapefile")    # .shp 文件驱动
driver = ogr.GetDriverByName("Mapinfo File")      # mapinfo   .tab 文件驱动
filename = r'E:\工具\资料\宝鸡\研究\Python\python3\gaode_range\tab\mapinfo.TAB'
dataSource = driver.Open(filename,1)               #其中 第二个参数 0是只读，为1是可写
if dataSource is None:
    print('could not open')
    sys.exit(1)
print('done!')

layer = dataSource.GetLayer(0)
n = layer.GetFeatureCount()      # 看看这个数据层里面有几个点呢？
print('feature count:', n)


extent = layer.GetExtent()      #读出上下左右边界
print('extent:', extent)
print('ul:', extent[0], extent[3])
print('lr:', extent[1], extent[2])


point = layer.GetFeature(2)    #读取某一对象，这里读取的是一个点
field_1 = point.GetField('index')
print(field_1)



###############################另外还有按顺序读取地理对象，循环遍历所有的feature
point = layer.GetNextFeature()  #读取下一个
while point:
    print(point.GetField('index'))
    #geom = point.GetGeometryRef()  #提取feature的几何形状
    #print(geom.GetX(),geom.GetY())  #不知道什么原因,这两句能是python崩溃

    fieldCount = point.GetFieldCount()  # 表有几个字段
    geomFieldCount = point.GetGeomFieldCount()  # 获取几何图形有几个节点
    fieldName = point.GetFieldIndex("lon")  # 获取字段在表的第几列
    geomFieldIndex = point.GetGeomFieldIndex("lon")  # 获取几何字段的 ????
    fieldType = point.GetFieldType("lon")  # 获取字段的数据类型  0为整数  2 为浮点数   4 为字符串
    styleString = point.GetStyleString()  # 获取Feature 的样式字符串
    fieldNull = point.IsFieldNull(1)  # 判断 第一个 字段(列) 是否为空

    point.SetField("index",1)    # 设置字段的值i
    point.SetField2(1, 1)    # 设置字段的值
    point.Destroy()  # 释放对象内存
    point = layer.GetNextFeature()  # 读取下一个对象

layer.ResetReading()  #复位
dataSource.Destroy()    #关闭数据源，相当于文件系统操作中的关闭文件







#创建新文件
path = r'./tab/'
filename = r'newmap.tab'
if os.path.isfile(path + filename) :            #如果文件存在的话 重新起一个文件名
    filename = path +  "new_" + filename
    print("File is exist,Create anothor, name is :" + filename)
else:
    filename = path + filename
    print("Create file, name is :" + filename)

dataSource2 = driver.CreateDataSource(filename)        # 创建 文件
#driver.DeleteDataSource(filename)    #删除一个文件
newLayer = dataSource2.CreateLayer('testLayer2', geom_type=ogr.wkbPoint)    #创建图层testLayer2

newField = ogr.FieldDefn('index', ogr.OFTInteger)#添加一个新字段，只能在layer里面加
#newField.SetWidth(4)                            #如果新字段是字符串类则必须要指定宽度
newLayer.CreateField(newField)                       #将新字段指配到layer

#########################################################################
#添加一个新的Feature
featureDefn = newLayer.GetLayerDefn()        # 获取Feature 的类型
newFeature = ogr.Feature(featureDefn)      #创建Feature

#设定几何形状
point = ogr.Geometry(ogr.wkbPoint)          #创建一个点
point.AddPoint(10,20,10)                       #设置 point的坐标
newFeature.SetGeometry(point)              #设置Featur的几何形状为point
newFeature.SetField('index',12)            #设定Featur某字段的数值,这里设置 index 字段的值为 12
newLayer.CreateFeature(newFeature)          #将newFeature写入 newLayer
#################################################################################


##########################################################################
#添加一个新的Feature
featureDefn = newLayer.GetLayerDefn()        # 获取Feature 的类型
newFeature = ogr.Feature(featureDefn)      #创建Feature

#设定几何形状
line = ogr.Geometry(ogr.wkbLineString)          #创建一条直线(折线)
line.AddPoint(10,10)                       #给line添加一个点
line.AddPoint(20,20)                       #给line添加一个点
line.AddPoint(0,20)                       #给line添加一个点
line.SetPoint(1,25,25)                      #修改 line 的第 1 个点的坐标 为 25,25
print(line.GetPointCount())                 #获取 直线line的 节点数
print(line.GetX(0))                         #读取0号点的x坐标和y坐标
print(line.GetY(0))

newFeature.SetGeometry(line)              #设置Featur的几何形状为line (设置newFeature 为 直线 line )
newFeature.SetField('index',13)            #设定Featur某字段的数值,这里设置 index 字段的值为 12
newLayer.CreateFeature(newFeature)          #将newFeature写入 newLayer

######################################################################################



#新建多边形，首先要新建环(ring)，然后把环添加到多边形对象中。
#添加一个新的Feature
featureDefn = newLayer.GetLayerDefn()        # 获取Feature 的类型
newFeature = ogr.Feature(featureDefn)      #创建Feature

ring = ogr.Geometry(ogr.wkbLinearRing)
ring.AddPoint(0,0)          #添加点到Ring中
ring.AddPoint(0,10)
ring.AddPoint(10,10)
ring.AddPoint(10,0)
ring.CloseRings()  #用CloseRings关闭Ring，
#ring.AddPoint(0,0)  #或者将最后一个点的坐标设定为与第一个点相同 也可以关闭Ring

inring = ogr.Geometry(ogr.wkbLinearRing)
inring.AddPoint(2.5,2.5)
inring.AddPoint(7.5,2.5)
inring.AddPoint(7.5,7.5)
inring.AddPoint(2.5,7.5)
inring.CloseRings()  #用CloseRings关闭inring，

polygon = ogr.Geometry(ogr.wkbPolygon)     #创建polygon区域
polygon.AddGeometry(ring)                   # 把环 ring添加到  polygon
polygon.AddGeometry(inring)                 # 把环 ring添加到  polygon
print(polygon.GetGeometryCount())           # 查看polygon 有几个 ring
inring = polygon.GetGeometryRef(1)          # 从polygon中读取ring

newFeature.SetGeometry(polygon)              #设置Featur的几何形状为polygon (设置newFeature 为 区域 polygon )
newFeature.SetField('index',15)            #设定Featur某字段的数值,这里设置 index 字段的值为 15
newLayer.CreateFeature(newFeature)          #将newFeature写入 newLayer
###########################################################################################


###########################################################################################
#用AddGeometry把普通的几何形状加到复合几何形状中 例如MultiPoint, MultiLineString, MultiPolygon
#添加一个新的Feature
featureDefn = newLayer.GetLayerDefn()        # 获取Feature 的类型
newFeature = ogr.Feature(featureDefn)      #创建Feature

multipoint = ogr.Geometry(ogr.wkbMultiPoint)             #定义复合图形
point = ogr.Geometry(ogr.wkbPoint)
point.AddPoint(5,5)
multipoint.AddGeometry(point)
point.AddPoint(15,15)
multipoint.AddGeometry(point)
print(multipoint.GetGeometryCount())           # 查看multipoint 有几个 point

newFeature.SetGeometry(multipoint)           #设置Featur的几何形状为multipoint (设置newFeature 为 复合图形 multipoint )
newFeature.SetField('index',18)            #设定Featur某字段的数值,这里设置 index 字段的值为 18
newLayer.CreateFeature(newFeature)          #将newFeature写入 newLayer

#读取MultiGeometry中的Geometry，方法和从Polygon中读取ring是一样的，可以说Polygon是一种内置的MultiGeometry。



#不要删除一个已存在的Feature的Geometry，会把python搞崩溃的

#只能删除脚本运行期间创建的Geometry，比方说手工创建出来的，或者调用其他函数自动创建的。就算这个Geometry已经用来创建别的Feature，你还是可以删除它。

#例如：Polygon.Destroy()








