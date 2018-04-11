# -*- coding:UTF-8 -*-

import json
import requests
import time
from createShapeFile import CreateMapFeature

def cutRect(rect):
    #参数为 左上角 和 右下角坐标的 列表    例如 leftTop:[0,10]   rightBottom:[10,0]
    #把矩形框分割为四等份
    rects = []            #列表用于保存分割后的四个矩形
    leftTopRect = []      #用于左上角矩形的坐标
    rightTopRect = []       #用于右上角矩形的坐标
    leftBottomRect = []      #用于左下角矩形的坐标
    rightBottomRect = []       #用于右下角矩形的坐标

    leftTop = rect[0]           #左上角坐标
    rightBottom = rect[1]       #右下角坐标

    width = rightBottom[0] - leftTop[0]             #Rect的宽度
    height = leftTop[1] - rightBottom[1]            #Rect的高度

    leftTopRect = [[leftTop[0],leftTop[1]],[leftTop[0] + width/2 ,rightBottom[1] + height/2]]   #左上角Rect的坐标
    rightTopRect = [[leftTop[0] + width/2, leftTop[1]],[rightBottom[0], rightBottom[1] + height/2]]  # 右上角Rect的坐标
    leftBottomRect = [[leftTop[0], rightBottom[1] + height/2], [leftTop[0] + width/2, rightBottom[1]]]  # 左下角Rect的坐标
    rightBottomRect = [[leftTop[0] + width/2 ,rightBottom[1] + height/2], [rightBottom[0], rightBottom[1]]]  # 左下角Rect的坐标
    rects = [leftTopRect, rightTopRect, leftBottomRect, rightBottomRect]
    return rects

def rectToPoint(rect):
    # 参数为 左上角 和 右下角坐标的 列表    例如 leftTop:[0,10]   rightBottom:[10,0]
    leftTop = rect[0]           #左上角坐标
    rightBottom = rect[1]       #右下角坐标
    points = []
    leftTopPoint = [leftTop[0],leftTop[1]]   #左上角Point的坐标
    rightTopPoint = [rightBottom[0],leftTop[1]]  # 右上角Point的坐标
    rightBottomPoint = [rightBottom[0], rightBottom[1]]  # 左下角Point的坐标
    leftBottomPoint = [leftTop[0], rightBottom[1]]  # 左下角Point的坐标
    points = [leftTopPoint, rightTopPoint, rightBottomPoint, leftBottomPoint]
    return points


if __name__ == '__main__' :
    newMap = CreateMapFeature('E:\\工具\\资料\\宝鸡\\研究\\Python\\python3\\gaode_range\\tab\\')
    fieldList = (("index",(4,254)), ("name",(4,254)), ("lon", 2), ("lat" , 2))
    dataSource = newMap.newFile('polygon.shp')
    newLayer = newMap.createLayer(dataSource, fieldList)

    rect = [[0, 10], [10,0]]
    newMap.createPolygon(newLayer,[rectToPoint(rect)], ("1", "源矩形", 23.8, 102.85))

    rects = cutRect(rect)
    for i,subRect in enumerate(rects,1) :
        print(subRect)
        newMap.createPolygon(newLayer,[rectToPoint(subRect)], (i,"分割后的Rect_" + str(i),23.8,102.85))



