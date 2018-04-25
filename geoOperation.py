#!usr/bin/env python  
#-*- coding:utf-8 _*-  

""" 
@author:Administrator 
@file: geoOperation.py 
@time: 2018/04/{DAY} 
描述:通过GDAL库来 判断 两条线段  line 是否相交  或  穿过 Crosses
用于在 AMAP采集 建筑物bound边界的时候 判断 bound 的边界是否错乱!
"""



import osr
try:
    from osgeo import ogr,gdal
except:
    import ogr


testSR = osr.SpatialReference()              #设置坐标系投影
testSR.SetWellKnownGeogCS("WGS84")
print(testSR.ExportToPrettyWkt())
testSR.ImportFromEPSG(4326)#returns 6                #设置坐标系投影


def isInvalidBound(pointList):
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


if __name__ =='__main__':
    boundPoints = [(0, 0), (0, 5), (5, 5), (5,0), (-2,3), (6, 6)]
    isCross = isInvalidBound(boundPoints)
    print(isCross)













