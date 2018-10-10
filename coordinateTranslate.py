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
        self.MCBAND = (12890594.86, 8362377.87, 5591021, 3481989.83, 1678043.12, 0)
        self.MC2LL = ([1.410526172116255e-8, 0.00000898305509648872, -1.9939833816331,
                  200.9824383106796, -187.2403703815547, 91.6087516669843, - 23.38765649603339,
                  2.57121317296198, -0.03801003308653, 17337981.2],
                 [-7.435856389565537e-9, 0.000008983055097726239, -0.78625201886289,
                  96.32687599759846, -1.85204757529826, -59.36935905485877, 47.40033549296737,
                  -16.50741931063887, 2.28786674699375, 10260144.86],
                 [-3.030883460898826e-8, 0.00000898305509983578, 0.30071316287616,
                  59.74293618442277, 7.357984074871, -25.38371002664745, 13.45380521110908,
                  -3.29883767235584, 0.32710905363475, 6856817.37],
                 [-1.981981304930552e-8, 0.000008983055099779535, 0.03278182852591, 40.31678527705744,
                  0.65659298677277, -4.44255534477492, 0.85341911805263, 0.12923347998204,
                  -0.04625736007561, 4482777.06],
                 [3.09191371068437e-9, 0.000008983055096812155, 0.00006995724062, 23.10934304144901,
                  -0.00023663490511, -0.6321817810242, -0.00663494467273, 0.03430082397953,
                  -0.00466043876332, 2555164.4],
                 [2.890871144776878e-9, 0.000008983055095805407, -3.068298e-8, 7.47137025468032,
                  -0.00000353937994, -0.02145144861037, -0.00001234426596, 0.00010322952773,
                  -0.00000323890364, 826088.5])


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
        return {'lat': round(wgsLat,7), 'lon': round(wgsLon,7)}


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




    class GISError(Exception):
        """GIS Exception
        """

    def convert_MCT_2_BD09(self,lon, lat):
        """将墨卡托坐标(BD09MI)转换成BD09
                Args:
                    lon: float, 经度
                    lat: float, 维度
                Returns:
                    (x, y): tuple, 经过转换的x, y
        """
        ax = None

        # 获取常量ax
        for j in range(len(self.MCBAND)):
            if lat >= self.MCBAND[j]:
                ax = self.MC2LL[j]
                break

        if ax is None:
            raise print("error lat:%s" % lat)

        e = ax[0] + ax[1] * abs(lon)
        i = abs(lat) / ax[9]
        aw = ax[2] + ax[3] * i + ax[4] * i * i + ax[5] * i * i * i + \
             ax[6] * i * i * i * i + ax[7] * i * i * i * i * i + ax[8] * i * i * i * i * i * i
        if lon < 0:
            e *= -1
        if lat < 0:
            aw *= -1

        return {'lat':aw, 'lon': e}


    def convert_BD09_2_GCJ02(self,lon, lat):
        """坐标转换，将BD09转成GCJ03
                Args:
                    lon: float, 经度
                    lat: float, 维度
                Returns:
                    (x, y): tuple, 转换后的结果
        """
        x = lon - 0.0065
        y = lat - 0.006
        z = math.sqrt(x * x + y * y) - 0.00002 * math.sin(y * self.x_pi)
        theta = math.atan2(y, x) - 0.000003 * math.cos(x * self.x_pi)
        gg_lon = z * math.cos(theta)
        gg_lat = z * math.sin(theta)
        return gg_lon, gg_lat



    def convert_BD09MI_to_WGS84(self,lon, lat):
        """将墨卡托坐标(BD09MI)转换成WGS84
                Args:
                    lon: float, 经度
                    lat: float, 维度
                Returns:
                    (x, y): tuple, 经过转换的x, y
        """
        ax = None

        # 获取常量ax
        for j in range(len(self.MCBAND)):
            if lat >= self.MCBAND[j]:
                ax = self.MC2LL[j]
                break

        if ax is None:
            raise print("error lat:%s" % lat)

        e = ax[0] + ax[1] * abs(lon)
        i = abs(lat) / ax[9]
        aw = ax[2] + ax[3] * i + ax[4] * i * i + ax[5] * i * i * i + \
             ax[6] * i * i * i * i + ax[7] * i * i * i * i * i + ax[8] * i * i * i * i * i * i
        if lon < 0:
            e *= -1
        if lat < 0:
            aw *= -1
        bdlon = e
        bdlat = aw
        return self.bd_wgs(bdlat, bdlon)









if __name__=="__main__":
    translateGps = GPS()
    result = translateGps.gcj_decrypt_exact(34.351483, 107.198623)
    print(result['lat'], ",", result['lon'],"amapjiema")

    result = translateGps.bd_wgs(34.357389, 107.205153)
    print(result['lat'], ",", result['lon'], "baidujiema")

    resultm = translateGps.convert_MCT_2_BD09(12132394.6,4037825.41)
    print("墨卡托坐标为:12132394.6,4037825.41")
    print("百度经纬度坐标为:" , resultm['lat'], ",", resultm['lon'])


    resultmt = translateGps.convert_BD09MI_to_WGS84(12132394.6,4037825.41)
    print("墨卡托坐标为:12132394.6,4037825.41")
    print("WGS-84坐标为:", resultmt['lat'], ",", resultmt['lon'])

    # 107.198623, 34.351483  amap
    # 107.205153,34.357389   baiduMap






'''
# 定义一些常量
x_PI = 3.14159265358979324 * 3000.0 / 180.0
PI = 3.1415926535897932384626
a = 6378245.0
ee = 0.00669342162296594323

/**
* 百度坐标系 (BD-09) 与 火星坐标系 (GCJ-02)的转换
* 即 百度 转 谷歌、高德
* @param bd_lon
* @param bd_lat
* @returns {*[]}
*/

def bd09togcj02(bd_lon, bd_lat):
    x_pi = 3.14159265358979324 * 3000.0 / 180.0;
    x = bd_lon - 0.0065;
    y = bd_lat - 0.006;
    z = math.sqrt(x * x + y * y) - 0.00002 * math.sin(y * x_pi);
    theta = math.atan2(y, x) - 0.000003 * math.cos(x * x_pi);
    gg_lng = z * math.cos(theta);
    gg_lat = z * math.sin(theta);
    return [gg_lng, gg_lat]



/**
* GCJ02 转换为 WGS84
* @param lng
* @param lat
* @returns {*[]}
*/

def gcj02towgs84(lng, lat):
    if (out_of_china(lng, lat)):
        return [lng, lat]
    else:
        dlat = transformlat(lng - 105.0, lat - 35.0)
        dlng = transformlng(lng - 105.0, lat - 35.0)
        radlat = lat / 180.0 * PI
        magic = math.sin(radlat)
        magic = 1 - ee * magic * magic
        sqrtmagic = math.sqrt(magic)
        dlat = (dlat * 180.0) / ((a * (1 - ee)) / (magic * sqrtmagic) * PI)
        dlng = (dlng * 180.0) / (a / sqrtmagic * math.cos(radlat) * PI)
        mglat = lat + dlat
        mglng = lng + dlng
        return [lng * 2 - mglng, lat * 2 - mglat]




/**
* WGS84转GCj02
* @param lng
* @param lat
* @returns {*[]}
*/

def wgs84togcj02(lng, lat):
    if (out_of_china(lng, lat)):
        return [lng, lat]
    else:
       dlat = transformlat(lng - 105.0, lat - 35.0)
       dlng = transformlng(lng - 105.0, lat - 35.0)
       radlat = lat / 180.0 * PI
       magic = math.sin(radlat)
       magic = 1 - ee * magic * magic
       sqrtmagic = math.sqrt(magic)
       dlat = (dlat * 180.0) / ((a * (1 - ee)) / (magic * sqrtmagic) * PI)
       dlng = (dlng * 180.0) / (a / sqrtmagic * math.cos(radlat) * PI)
       mglat = float(lat) + float(dlat)
       mglng = float(lng) + float(dlng)
       return [mglng, mglat]

/**
* 火星坐标系 (GCJ-02) 与百度坐标系 (BD-09) 的转换
* 即谷歌、高德 转 百度
* @param lng
* @param lat
* @returns {*[]}
*/
def gcj02tobd09(lng, lat):
    z = math.sqrt(lng * lng + lat * lat) + 0.00002 * math.sin(lat * x_PI)
    theta = math.atan2(lat, lng) + 0.000003 * math.cos(lng * x_PI)
    bd_lng = z * math.cos(theta) + 0.0065
    bd_lat = z * math.sin(theta) + 0.006
    return [bd_lng, bd_lat]


def transformlat(lng, lat):
    ret = -100.0 + 2.0 * lng + 3.0 * lat + 0.2 * lat * lat + 0.1 * lng * lat + 0.2 * math.sqrt(math.fabs(lng))
    ret += (20.0 * math.sin(6.0 * lng * PI) + 20.0 * math.sin(2.0 * lng * PI)) * 2.0 / 3.0
    ret += (20.0 * math.sin(lat * PI) + 40.0 * math.sin(lat / 3.0 * PI)) * 2.0 / 3.0
    ret += (160.0 * math.sin(lat / 12.0 * PI) + 320 * math.sin(lat * PI / 30.0)) * 2.0 / 3.0
    return ret


def transformlng(lng, lat):
    ret = 300.0 + lng + 2.0 * lat + 0.1 * lng * lng + 0.1 * lng * lat + 0.1 * math.sqrt(math.fabs(lng))
    ret += (20.0 * math.sin(6.0 * lng * PI) + 20.0 * math.sin(2.0 * lng * PI)) * 2.0 / 3.0
    ret += (20.0 * math.sin(lng * PI) + 40.0 * math.sin(lng / 3.0 * PI)) * 2.0 / 3.0
    ret += (150.0 * math.sin(lng / 12.0 * PI) + 300.0 * math.sin(lng / 30.0 * PI)) * 2.0 / 3.0
    return ret



/**
* 判断是否在国内，不在国内则不做偏移
* @param lng
* @param lat
* @returns {boolean}
*/

def out_of_china(self, lat, lon):
    if lon < 72.004 or lon > 137.8347: return True
    if lat < 0.8293 or lat > 55.8271: return True
    return False






/**
* 百度墨卡托转经纬度坐标
* @param lng
* @param lat
* @param divId
* @returns{lngLatPt}
*/
var baiduMercatoToLngLat=function(x,y,divId){
var baiduMap = new BMap.Map(divId);
//通过web mercato坐标构建起点终点
var ptXY = new BMap.Pixel(x,y);
//通过相应接口将起点终点的web mercato坐标转换为经纬度坐标
   var projection2 = baiduMap.getMapType().getProjection();
   var lngLatPt=projection2.pointToLngLat(ptXY);
   return lngLatPt;
}

/**
* 百度经纬度坐标转百度墨卡托坐标
* @param lng
* @param lat
* @param divId
* @returns{mercatoPt}
*/
   var baiduLngLatToMercato=function(lng,lat,divId){
var bdXY = new BMap.Point(lng,lat);
var baiduMap = new BMap.Map(divId);
   var projection2 = baiduMap.getMapType().getProjection();
   var mercatoPt = projection2.lngLatToPoint(bdXY);
return mercatoPt;
}


'''
