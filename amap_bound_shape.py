# -*- coding: utf-8 -*-


from urllib.parse import quote
from urllib import request
from urllib import error
import json, time, random
import xlwt
import createShapeFile



poi_search_url = "http://restapi.amap.com/v3/place/text"
poi_boundary_url = "https://ditu.amap.com/detail/get/detail"



# 获取key
class Keys():
    amap_web_keys = ['3a00e107b4ff451b9306fe3d0405d386', '771b45888c08fcd20c0cf04ed882483a', '9700dfeb2bbaf277dd856f1cd84e7975',  'e12b356d1573935e75f064c571e6e5a2',  '2a3bebd5eedaabc4cfa5c04eb6989365']
    keyCount = len(amap_web_keys)  # 可用的key的数量

    def __init__(self):
        self.keyCurrentIndex = random.randint(0,4)  # 初始化当前使用的key的 index
        self.keyCurrent = self.amap_web_keys[self.keyCurrentIndex]  # 初始化当前key
        print('Current used key is :',self.keyCurrent, ', Index is :', self.keyCurrentIndex)


    def getKey(self):
        self.keyCurrentIndex = self.keyCurrentIndex - 1  # 把当前正在使用的key的index 减去1

        if self.keyCurrentIndex < 0:  # 如果 当前正在使用的key的index 小于0
            self.keyCurrentIndex = self.keyCount - 1  # 则重新初始化当前正在使用的key的index(复位keyCurrentIndex)

        self.keyCurrent = self.amap_web_keys[self.keyCurrentIndex]  # 获取key 为 列表中的 当前正在使用的Key的上一个 Key
        print('Current used key is :',self.keyCurrent, ', Index is :', self.keyCurrentIndex)
        return self.keyCurrent



amapKey = Keys()                #初始化Keys 类对象
amap_web_key = amapKey.keyCurrent       # 初始值
#amapKey.getKey()                #更换Key



# 根据城市名称和分类关键字获取poi数据
def getpois(cityname, keywords):
    i = 1
    poilist = []
    while True:  # 使用while循环不断分页获取数据
        result = getpoi_page(cityname, keywords, i)
        if result :                     #如果返回结果为正常 则
            result = json.loads(result)  # 将字符串转换为json
            if result['count'] == '0':
                break
            hand(poilist, result)
            i = i + 1
        else :
            print('返回结果错误', result)                #如果返回值为 -1
            continue                    #跳过本次循环
    return poilist


# 数据写入excel
def write_to_excel(poilist, cityname, classfield):
    # 一个Workbook对象，这就相当于创建了一个Excel文件
    book = xlwt.Workbook(encoding='utf-8', style_compression=0)
    sheet = book.add_sheet(classfield, cell_overwrite_ok=True)
    # 第一行(列标题)
    sheet.write(0, 0, 'id')
    sheet.write(0, 1, 'name')
    sheet.write(0, 2, 'location')
    sheet.write(0, 3, 'pname')
    sheet.write(0, 4, 'pcode')
    sheet.write(0, 5, 'cityname')
    sheet.write(0, 6, 'citycode')
    sheet.write(0, 7, 'adname')
    sheet.write(0, 8, 'adcode')
    sheet.write(0, 9, 'address')
    sheet.write(0, 10, 'type')
    sheet.write(0, 11, 'boundary')

    # 初始化GDAL对象
    newMap = createShapeFile.CreateMapFeature('.\\tab\\')
    ##定义地图各个字段的名字和数据类型
    fieldList = (("id", (4, 16)), ("name", (4, 254)), ("location", (4, 50)), ("pname", (4, 10)), ("pcode", (4, 10)), ("cityname", (4, 32)), ("citycode", (4, 10)), ("adname", (4, 50)), ("adcode", (4, 10)), ("address", (4, 254)), ("type", (4, 254)), ("boundary", (4, 254)))

    #创建point 类型 shape文件
    pointDataSource = newMap.newFile(cityname + '_' + classfield + 'point.shp')
    pointLayer = newMap.createLayer(pointDataSource, fieldList)     #创建point的shape文件

    #创建polygon 类型 shape文件
    polygonDataSource = newMap.newFile(cityname + '_' + classfield + 'polygon.shp')
    polygonLayer = newMap.createLayer(polygonDataSource, fieldList)


    print('找到POI总数: ', len(poilist))
    for i in range(len(poilist)):
        # 根据poi的id获取边界数据
        bounstr = ''
        bounlist = getBounById(poilist[i]['id'])
        if (len(bounlist) > 1):
            bounstr = str(bounlist)
            # 每一行写入
        sheet.write(i + 1, 0, poilist[i]['id'])
        sheet.write(i + 1, 1, poilist[i]['name'])
        sheet.write(i + 1, 2, poilist[i]['location'])
        sheet.write(i + 1, 3, poilist[i]['pname'])
        sheet.write(i + 1, 4, poilist[i]['pcode'])
        sheet.write(i + 1, 5, poilist[i]['cityname'])
        sheet.write(i + 1, 6, poilist[i]['citycode'])
        sheet.write(i + 1, 7, poilist[i]['adname'])
        sheet.write(i + 1, 8, poilist[i]['adcode'])
        sheet.write(i + 1, 9, poilist[i]['address'])
        sheet.write(i + 1, 10, poilist[i]['type'])
        sheet.write(i + 1, 11, bounstr)
        # 最后，将以上操作保存到指定的Excel文件中

        location_lon = float(poilist[i]['location'].split(',')[0])      #转化经纬度为 float
        location_lat = float(poilist[i]['location'].split(',')[1])      #转化经纬度为 float
        #定义地图各个字段的值的tapul
        fieldValues = (poilist[i]['id'], poilist[i]['name'], poilist[i]['location'], poilist[i]['pname'], poilist[i]['pcode'], poilist[i]['cityname'], poilist[i]['citycode'], poilist[i]['adname'], poilist[i]['adcode'], poilist[i]['address'], poilist[i]['type'], poilist[i]['location'])

        print(poilist[i])
        newMap.createPoint(pointLayer, location_lon, location_lat, fieldValues)
        if len(bounlist) > 1 :
            newMap.createPolygon(polygonLayer,[bounlist] , fieldValues)
        print(i, poilist[i]['name'])
        #################################mapinfo 的字符串类型最多支持长度为255 大于255的部分将被砍掉  shape 的字符串类型最多支持长度为254 大于254的 将会被舍弃

    book.save(r'.//tab//' + cityname + '.xls')


# 将返回的poi数据装入集合返回
def hand(poilist, result):
    # result = json.loads(result)  # 将字符串转换为json
    pois = result['pois']
    for i in range(len(pois)):
        poilist.append(pois[i])

    # 单页获取pois


def getpoi_page(cityname, keywords, page):
    req_url = poi_search_url + "?key=" + amapKey.keyCurrent + '&extensions=all&keywords=' + quote(
        keywords) + '&city=' + quote(cityname) + '&citylimit=true' + '&offset=25' + '&page=' + str(
        page) + '&output=json'
    data = ''
    try :                                                  #带异常处理
        with request.urlopen(req_url) as f:
            data = f.read()
            data = data.decode('utf-8')
            json.loads(data)
            if json.loads(data)["status"] != '1':           #如果返回状态码异常,
                amapKey.getKey()                              # 更换Key
                data = getpoi_page(cityname, keywords, page)    #本方法迭代
        return data

    except error.URLError as e:
        print('URL Error 请检查网络连接!')
        if hasattr(e, "code"):
            print(e.code)
        if hasattr(e, "reason"):
            print(e.reason)
        return  0

    except error.HTTPError as e:
        print('HTTP Error 请检查网络连接!')
        if hasattr(e, "code"):
            print(e.code)
        if hasattr(e, "reason"):
            print(e.reason)
        return 0

        # 根据id获取边界数据
def getBounById(id):
    req_url = poi_boundary_url + "?id=" + id
    try:
        with request.urlopen(req_url) as f:
            data = f.read()
            data = data.decode('utf-8')
            dataList = []
            datajson = json.loads(data)  # 将字符串转换为json
            if json.loads(data)["status"] != '1':           #如果返回状态码异常,
                if json.loads(data)["status"] == '6' :
                    time.sleep(120)                             #如果返回值状态码为 6   即 'too fast' 则 暂停60秒
                amapKey.getKey()                              # 更换Key
                dataList = getBounById(id)                    #迭代本方法
            datajson = datajson['data']
            datajson = datajson['spec']
            if len(datajson) == 1:
                return dataList
            if datajson.get('mining_shape') != None:
                datajson = datajson['mining_shape']
                shape = datajson['shape']
                dataArr = shape.split(';')

                for i in dataArr:
                    innerList = []
                    f1 = float(i.split(',')[0])
                    innerList.append(float(i.split(',')[0]))
                    innerList.append(float(i.split(',')[1]))
                    dataList.append(innerList)
            return dataList

    except error.URLError as e:
        print('URL Error 请检查网络连接!')
        if hasattr(e, "code"):
            print(e.code)
        if hasattr(e, "reason"):
            print(e.reason)
        return  0

    except error.HTTPError as e:
        print('HTTP Error 请检查网络连接!')
        if hasattr(e, "code"):
            print(e.code)
        if hasattr(e, "reason"):
            print(e.reason)
        return 0


    # 获取城市分类数据


cityname = "西安"
classfiled = "小区"
pois = getpois(cityname, classfiled)

# 将数据写入excel
write_to_excel(pois, cityname, classfiled)
print('写入成功')

# 根据获取到的poi数据的id获取边界数据
# dataList = getBounById('B02F4027LY')
# print(type(dataList))

# print(str(dataList))
