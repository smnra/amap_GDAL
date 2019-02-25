#!usr/bin/env python  
#-*- coding:utf-8 _*-  

""" 
@author:Administrator 
@file: 高德坐标转wgs-84.py 
@time: 2018/11/{DAY} 
描述: 读取csv文件的 lon列 和lat 列 并由高德坐标系 转为 wgs-84坐标系

"""

import  os
import coordinateTranslate

def readCsv(fileName):
    with open(fileName, mode='r', encoding='gbk', errors='ignore') as f:  # 将采集进度写入文件
        csvList = f.readlines()
        print(csvList[0])
        return list(csvList)

def getLonLatIndex(lineTitle):
    lineTitle = lineTitle.replace("\n","").split(",")
    if "lon" in lineTitle:
        lonIndex = lineTitle.index("lon")
    else:
        lonIndex = -1

    if "lat" in lineTitle:
        latIndex = lineTitle.index("lat")
    else:
        latIndex = -1

    return [lonIndex, latIndex]

def transCoord(line, lonIndex, latIndex):
    line = line.replace("\n","")
    lineList = line.split(",")

    sLon = float(lineList[lonIndex])
    sLat = float(lineList[latIndex])
    coord= tranCoord(sLat,sLon)

    lineList[lonIndex], lineList[latIndex] = str(coord['lon']), str(coord['lat'])
    line = ",".join(lineList)+"\n"
    return line



if __name__=="__main__":

    fileName = r'E:\工具\资料\宝鸡\研究\当前任务\fast\宝鸡\大众点评_宝鸡.csv'

    csvLines = readCsv(fileName)

    # 确定 lon 和 lat 在表中的列的 位置
    lonIndex, latIndex = getLonLatIndex(csvLines[0])

    tran = coordinateTranslate.GPS()
    tranCoord = tran.gcj_encrypt
    info = []
    for i,line in enumerate(csvLines[1:-1]):
        print(csvLines[i+1])
        csvLines[i+1] = transCoord(line, lonIndex, latIndex)
        info.append(csvLines[i+1])
        if i/100==1.0 :
            with open(fileName + ".tran", mode='a+', encoding='gbk', errors='ignore') as f:
            # 将采集进度写入文件
                f.writelines(info)
            info = []

    with open(fileName + ".tran", mode='a+', encoding='gbk', errors='ignore') as f:
        # 将采集进度写入文件
        f.writelines(info)
