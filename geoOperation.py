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


def isInvalidBound(ring):
    # 根据传入的列表  创建相邻两个元素的 直线(也就是 多边形的每一条边), 添加到 lines 列表中 ,再分别判断这些直线是否 交叉 Crosses
    lines = []

    for i in range(len(ring) - 1):
        line = ogr.Geometry(ogr.wkbLineString)  # 创建一条折线
        line.AddPoint(float(ring[i][0]), float(ring[i][1]))  # 直线的第一个点
        line.AddPoint(float(ring[i + 1][0]), float(ring[i + 1][1]))  # 直线的第二个点
        lines.append(line)  # 添加到列表中

    line = ogr.Geometry(ogr.wkbLineString)  # 创建最后一个点和第一个点的直线
    line.AddPoint(float(ring[-1][0]), float(ring[-1][1]))
    line.AddPoint(float(ring[0][0]), float(ring[0][1]))
    lines.append(line)

    for i in range(len(lines)):  # 遍历每一条直线
        for j in range(i, len(lines)):
            if lines[i].Crosses(lines[j]):  # 判断其他直线与这条直线是否交叉
                return True  # 如果交叉 返回True
    return False  # 默认返回False

def isInvalidBound2(ring):
    # 根据 polygon 的中心的来判断 amap的 建筑物边界是否错乱
    # ring  为组成多边形的点的坐标列表 如 :[(0, 0), (0, 10), (10, 10), (10, 0)]
    # center 为建筑物边界的中心点.
    polygon = ogr.Geometry(ogr.wkbPolygon)  # 创建多边形
    ring = ogr.Geometry(ogr.wkbLinearRing)  # 创建一个环 ring
    for tmpRing in ring:
        ring.AddPoint(float(tmpRing[0]), float(tmpRing[1]))  # 循环添加点到Ring中
    if ring[0] != ring[-1]:  # 如果ring的第一个元素和最后一个元素不相等
        ring.CloseRings()  # 用CloseRings闭合Ring，
    polygon.AddGeometry(ring)  # 把环 ring添加到  polygon
    area= polygon.GetArea()
    center = polygon.Centroid()
    return False  # 默认返回False


class Polygon() :
    def __init__(self, ringList):
        # 根据 polygon 的中心的来判断 amap的 建筑物边界是否错乱
        # ring  为组成多边形的点的坐标列表 如 :[(0, 0), (0, 10), (10, 10), (10, 0)]
        # center 为建筑物边界的中心点.
        self.ringList = ringList
        self.polygon = ogr.Geometry(ogr.wkbPolygon)  # 创建多边形
        self.ring = ogr.Geometry(ogr.wkbLinearRing)  # 创建一个环 ring
        for tmpRing in ringList:
            self.ring.AddPoint(float(tmpRing[0]), float(tmpRing[1]))  # 循环添加点到Ring中
        if ringList[0] != ringList[-1]:  # 如果ring的第一个元素和最后一个元素不相等
            self.ring.CloseRings()  # 用CloseRings闭合Ring，
        self.polygon.AddGeometry(self.ring)  # 把环 ring添加到  polygon

    def getArea(self):
        #返回 多边形的面积
        return  self.polygon.GetArea()

    def getCenter(self):
        # 返回 多边形的中心点坐标
        center = self.polygon.Centroid()
        center = [round(center.GetPoint()[0],6),round(center.GetPoint()[1],6)]
        return center

    def isLineCrosses(self):
        # 根据传入的列表  创建相邻两个元素的 直线(也就是 多边形的每一条边), 添加到 lines 列表中 ,再分别判断这些直线是否 交叉 Crosses
        lines = []
        for i in range(len(self.ringList) - 1):
            line = ogr.Geometry(ogr.wkbLineString)  # 创建一条折线
            line.AddPoint(float(self.ringList[i][0]), float(self.ringList[i][1]))  # 直线的第一个点
            line.AddPoint(float(self.ringList[i + 1][0]), float(self.ringList[i + 1][1]))  # 直线的第二个点
            lines.append(line)  # 添加到列表中
        line = ogr.Geometry(ogr.wkbLineString)  # 创建最后一个点和第一个点的直线
        line.AddPoint(float(self.ringList[-1][0]), float(self.ringList[-1][1]))
        line.AddPoint(float(self.ringList[0][0]), float(self.ringList[0][1]))
        lines.append(line)

        for i in range(len(lines)):  # 遍历每一条直线
            for j in range(i, len(lines)):
                if lines[i].Crosses(lines[j]):  # 判断其他直线与这条直线是否交叉
                    return True  # 如果交叉 返回True
        return False  # 默认返回False

    def isInvalidBound(self,center):
        #center 为amap 上获取到的 mining_shape 的 中心点的坐标
        #self.center 为从polygon 计算出的 中心点的坐标
        #本方法先判断 ring组成的 polygon 的各个直线相互之间没有 Crosses,再判断 经过计算的 center的 坐标 和  传入的参数的 center 的坐标 之差 小于 0.000001 则认为 这个 polygon 是有效的  没有错乱的
        if self.isLineCrosses() :
            self.center = self.getCenter()          #计算polygon的 中心点的坐标
            if abs(self.center[0] - float([0])) < 0.000001 and abs(self.center[1] - float([1])) < 0.000001 :   #经过计算的 center的 坐标 和  传入的参数的 center 的坐标 之差 小于 0.000001
                return True                                                                                   #返回True
            else :
                return False
        else:
            return False


if __name__ =='__main__':
    ringList = [ [108.920221,34.229893], [108.919324,34.228498],
                 [108.918226,34.228962], [108.91807,34.228619],
                 [108.917882,34.22827], [108.917899,34.228202],
                 [108.918644,34.227877],[108.918532,34.22768],
                 [108.91871,34.227589], [108.918368,34.227061],
                 [108.918225,34.227143], [108.917874,34.227175],
                 [108.917499,34.227166], [108.917472,34.227143],
                 [108.91747,34.226853], [108.917231,34.226879],
                 [108.916865,34.226906], [108.916775,34.226906],
                 [108.9167,34.226872], [108.916647,34.226729],
                 [108.916625,34.226595], [108.916611,34.226479],
                 [108.916589,34.225973], [108.916583,34.225845],
                 [108.915273,34.226421], [108.913974,34.227001],
                 [108.912467,34.227643], [108.91172,34.228003],
                 [108.911351,34.228187], [108.912176,34.22949],
                 [108.913284,34.231225], [108.9134,34.231409],
                 [108.913748,34.231933], [108.91398,34.232289],
                 [108.91468,34.233376], [108.915528,34.234652],
                 [108.915828,34.235148], [108.916176,34.235715],
                 [108.91634,34.235975], [108.918181,34.235185],
                 [108.919077,34.234666], [108.919593,34.234304],
                 [108.919966,34.234129], [108.920601,34.233842],
                 [108.921532,34.233411], [108.921765,34.2333],
                 [108.921939,34.233193], [108.921992,34.233072],
                 [108.92206,34.232919], [108.922026,34.23282],
                 [108.921604,34.232184], [108.9215,34.231932],
                 [108.921029,34.231153], [108.920221,34.229893] ]

    tmpPolygon = Polygon(ringList)
    area = tmpPolygon.getArea()
    print(area)

    center = tmpPolygon.getCenter()
    print(center)

    if tmpPolygon.isLineCrosses():
        print('This polygon\'s  lines Not Crosses!')









