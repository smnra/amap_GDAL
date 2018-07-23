#!usr/bin/env python  
#-*- coding:utf-8 _*-  

""" 
@author:SMnRa
@file: coordinateTranslate.py 
@time: 2018/07/{DAY} 
描述: 用于坐标系之间的转化,比如常见的 WGS-84 , GCJ-02 ,BD-09 之间的转换
        WGS-84 为 硬件设备GPS采集到的经纬度,与 Google Earth 和 必应卫星地图, OpenStreetMap地图 ,的经纬度是相同的
        GCJ-02 为 高德地图,腾讯搜搜地图,灵图51ditu地图 ,谷歌电子地图,的经纬度
        BD-09 为 百度地图经纬度体系

"""
import math

class GPS():
    def __init__(self):
        self.PI = 3.14159265358979324
        self.x_pi = 3.14159265358979324 * 3000.0 / 180.0

    def delta(self, lat, lon):
        # Krasovsky 1940
        #
        # a = 6378245.0, 1/f = 298.3
        # b = a * (1 - f)
        # ee = (a^2 - b^2) / a^2
        a = 6378245.0  # a: 卫星椭球坐标投影到平面地图坐标系的投影因子。
        ee = 0.00669342162296594323  # ee: 椭球的偏心率。
        dLat = self.transformLat(lon - 105.0, lat - 35.0)
        dLon = self.transformLon(lon - 105.0, lat - 35.0)
        radLat = lat / 180.0 * self.PI
        magic = math.sin(radLat)
        magic = 1 - ee * magic * magic
        sqrtMagic = math.sqrt(magic)
        dLat = (dLat * 180.0) / ((a * (1 - ee)) / (magic * sqrtMagic) * self.PI)
        dLon = (dLon * 180.0) / (a / sqrtMagic * math.cos(radLat) * self.PI)
        return {'lat': dLat, 'lon': dLon}


    def gcj_encrypt(self, wgsLat, wgsLon):
        # WGS-84 to GCJ-02
        if self.outOfChina(wgsLat, wgsLon):
            return {'lat': wgsLat, 'lon': wgsLon}
        d = self.delta(wgsLat, wgsLon)
        return {'lat': wgsLat + d['lat'], 'lon': wgsLon + d['lon']}


    def gcj_decrypt(self, gcjLat, gcjLon):
        # GCJ-02 to WGS-84
        if self.outOfChina(gcjLat, gcjLon):
            return {'lat': gcjLat, 'lon': gcjLon}
        d = self.delta(gcjLat, gcjLon)
        return {'lat': gcjLat - d['lat'], 'lon': gcjLon - d['lon']}


    def gcj_decrypt_exact(self, gcjLat, gcjLon):
        # GCJ-02 to WGS-84 exactly
        initDelta = 0.01
        threshold = 0.000000001
        dLat = initDelta
        dLon = initDelta
        mLat = gcjLat - dLat
        mLon = gcjLon - dLon
        pLat = gcjLat + dLat
        pLon = gcjLon + dLon
        wgsLat = wgsLon = i = 0
        while True:
            wgsLat = (mLat + pLat)/2
            wgsLon = (mLon + pLon)/2
            tmp = self.gcj_encrypt(wgsLat, wgsLon)
            dLat = tmp['lat'] - gcjLat
            dLon = tmp['lon'] - gcjLon
            if ((math.fabs(dLat) < threshold) and (math.fabs(dLon) < threshold)): break
            if dLat>0 : pLat = wgsLat
            else : mLat = wgsLat
            if dLon>0 : pLon = wgsLon
            else : mLon = wgsLon
            i=i+1
            if i>10000 : break
        return {'lat': wgsLat, 'lon': wgsLon}


    def gcj_bd(self, gcjLat, gcjLon):
        # GCJ-02 to BD-09
        x = gcjLon
        y = gcjLat
        z = math.sqrt(x * x + y * y) + 0.00002 * math.sin(y * self.x_pi)
        theta = math.atan2(y, x) + 0.000003 * math.cos(x * self.x_pi)
        bdLon = z * math.cos(theta) + 0.0065
        bdLat = z * math.sin(theta) + 0.006
        return {'lat' : bdLat,'lon' : bdLon}


    def bd_gcj(self, bdLat, bdLon):
        # BD-09 to GCJ-02
        x = bdLon - 0.0065
        y = bdLat - 0.006
        z = math.sqrt(x * x + y * y) - 0.00002 * math.sin(y * self.x_pi)
        theta = math.atan2(y, x) - 0.000003 * math.cos(x * self.x_pi)
        gcjLon = z * math.cos(theta)
        gcjLat = z * math.sin(theta)
        return {'lat' : gcjLat, 'lon' : gcjLon}

    def bd_wgs(self, bdLat, bdLon):
        # BD-09 to WGS-84
        gcj = self.bd_gcj( bdLat, bdLon)
        wgs = self.gcj_decrypt_exact(gcj['lat'], gcj['lon'])
        return {'lat' : wgs['lat'], 'lon' : wgs['lon']}

    def wgs_bd(self, wgsLat, wgsLon):
        # WGS-84 to BD-09
        gcj = self.gcj_encrypt( wgsLat, wgsLon)
        bd = self.gcj_bd(gcj['lat'], gcj['lon'])
        return {'lat' : bd['lat'], 'lon' : bd['lon']}

    def mercator_encrypt(self, wgsLat, wgsLon):
        # WGS-84 to Web mercator
        # mercatorLat -> y mercatorLon -> x
        x = wgsLon * 20037508.34/180.
        y = math.log(math.tan((90.+wgsLat) * self.PI/360.)) / (self.PI/180.)
        y = y * 20037508.34/180.
        return {'lat' : y, 'lon' : x}

    def mercator_decrypt(self, mercatorLat, mercatorLon):
        # Web mercator to WGS-84
        # mercatorLat -> y mercatorLon -> x
        x = mercatorLon/20037508.34 * 180.
        y = mercatorLat/20037508.34 * 180.
        y = 180 / self.PI * (2 * math.atan(math.exp(y * self.PI / 180.)) - self.PI / 2)
        return {'lat' : y, 'lon' : x}



    def distance(self, latA, lonA, latB, lonB):
        # two point's distance
        earthR = 6371000.
        x = math.cos(latA * self.PI / 180.) * math.cos(latB * self.PI / 180.) * math.cos((lonA - lonB) * self.PI / 180)
        y = math.sin(latA * self.PI / 180.) * math.sin(latB * self.PI / 180.)
        s = x + y
        if s>1 : s = 1
        if s<-1: s = -1
        alpha = math.acos(s)
        distance = alpha * earthR
        return distance


    def outOfChina(self, lat, lon):
        if lon<72.004 or lon>137.8347 : return True
        if lat<0.8293 or lat>55.8271 : return True
        return False

    def transformLat(self, x, y):
        ret = -100.0 + 2.0 * x + 3.0 * y + 0.2 * y * y + 0.1 * x * y + 0.2 * math.sqrt(math.fabs(x))
        ret += (20.0 * math.sin(6.0 * x * self.PI) + 20.0 * math.sin(2.0 * x * self.PI)) * 2.0 / 3.0
        ret += (20.0 * math.sin(y * self.PI) + 40.0 * math.sin(y / 3.0 * self.PI)) * 2.0 / 3.0
        ret += (160.0 * math.sin(y / 12.0 * self.PI) + 320 * math.sin(y * self.PI / 30.0)) * 2.0 / 3.0
        return ret

    def transformLon(self, x, y):
        ret = 300.0 + x + 2.0 * y + 0.1 * x * x + 0.1 * x * y + 0.1 * math.sqrt(math.fabs(x))
        ret += (20.0 * math.sin(6.0 * x * self.PI) + 20.0 * math.sin(2.0 * x * self.PI)) * 2.0 / 3.0
        ret += (20.0 * math.sin(x * self.PI) + 40.0 * math.sin(x / 3.0 * self.PI)) * 2.0 / 3.0
        ret += (150.0 * math.sin(x / 12.0 * self.PI) + 300.0 * math.sin(x / 30.0 * self.PI)) * 2.0 / 3.0
        return ret



if __name__=="__main__":
    translateGps = GPS()
    result = translateGps.gcj_decrypt_exact(34.351483, 107.198623)
    print(result['lat'], ",", result['lon'],"amapjiema")

    result = translateGps.bd_wgs(34.357389, 107.205153)
    print(result['lat'], ",", result['lon'], "baidujiema")




    # 107.198623, 34.351483  amap
    # 107.205153,34.357389   baiduMap








