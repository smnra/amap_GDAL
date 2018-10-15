#!usr/bin/env python
#-*- coding:utf-8 _*-

"""
@author:Administrator
@file: amap_selenium_chrome.py
@time: 2018/10/07
描述: selenium  高德地图 chrome  采集小区边界

"""


import requests,re,time,os, random,json,math,time
from bs4  import BeautifulSoup
import coordinateTranslate
import createNewDir
#导入webdriver
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver import ActionChains
from selenium.webdriver.support import  expected_conditions as EC
from fake_useragent import UserAgent
#要想调用键盘按键操作需要引入keys包
from selenium.webdriver.common.keys import Keys



class GetBaiduMap():
    def __init__(self,fileName):
        self.url = 'https://map.baidu.com/'
        # 边界查询
        self.geoUrl = 'https://map.baidu.com/?newmap=1&reqflag=pcmap&biz=1&from=webmap&da_par=direct&pcevaname=pc4.1&qt=ext&c=233&ext_ver=new&tn=B_NORMAL_MAP&nn=0&ie=utf-8&l=17&uid=3c753948c9a2427235b06c64'
        # poi查找
        self.searchUrl = 'http://api.map.baidu.com/?qt=s&c=131&rn=100&ie=utf-8&oue=1&res=api&wd='
        ''' https://map.baidu.com/?qt=ext&uid=da961f7ddadb6962deee8bb8&ext_ver=new&&nn=0&l=18 '''

        # 搜索 名字 搜索 id
        'https://map.baidu.com/su?wd=%E8%9E%8D%E4%BE%A8%20&cid=233&type=0&newmap=1&b=(12121496.865%2C4038346.77%3B12121862.365%2C4038655.77)&t=1539339239819&pc_ver=2'
        # 查询边界的url



        # self.wdToUuidUrl = 'https://map.baidu.com/su?wd=%E8%9E%8D%E4%BE%A8%20&cid=233&type=0&newmap=1&b=(12121496.865%2C4038346.77%3B12121862.365%2C4038655.77)&t=1539339239819&pc_ver=2'
        self.wdToUuidUrl = 'http://map.baidu.com/su?cid=233&type=0&newmap=1&pc_ver=2&wd='
        ## 用 url 搜索出可能的 名字 和 uuid

        # self.getGeoUrl = 'https://map.baidu.com/?newmap=1&reqflag=pcmap&biz=1&from=webmap&da_par=direct&pcevaname=pc4.1&qt=ext&c=233&ext_ver=new&tn=B_NORMAL_MAP&nn=0&ie=utf-8&l=17&uid='
        self.getGeoUrl = 'https://map.baidu.com/?newmap=1&reqflag=pcmap&biz=1&from=webmap&da_par=direct&pcevaname=pc4.1&qt=ext&ext_ver=new&tn=B_NORMAL_MAP&nn=0&ie=utf-8&l=17&c=233&uid='
        # 然后用这个url查找 是否存在 pylgon

        #获取poi详细信息 的url
        #https://map.baidu.com/?ugc_type=3&ugc_ver=1&qt=detailConInfo&device_ratio=1&compat=1&t=1539394773310&uid=827202426e2c6305f33cba83&primaryUid=15840892553483683032&auth=fevy6Dcex31fdLP9AOdODI998f0Z3edJuxHBTBTENxVtComRB199A1GgvPUDZYOYIZuVt1cv3uVtGccZcuVtPWv3GuzEtXzljPaVjyBDEHKOQUWYxcEWe1GD8zv7u%40ZPuVteuztghxehwzJDVD66zJGvpHhOaQD2JKGpt66FUExcc%40AZ
        self.getInfoUrl = 'https://map.baidu.com/?ugc_type=3&ugc_ver=1&qt=detailConInfo&device_ratio=1&compat=1&t=1539394773310&uid='


        # 通过搜索框 获取poi的列表信息
        self.searchBoxUrl = 'https://map.baidu.com/?newmap=1&reqflag=pcmap&biz=1&from=webmap&da_par=direct&pcevaname=pc4.1&qt=s&da_src=searchBox.button&c=231&src=0&wd2=&pn=0&sug=0&l=16&from=webmap&sug_forward=&device_ratio=1&tn=B_NORMAL_MAP&nn=0&ie=utf-8&wd='

        self.fileName = fileName
        self.pois = []  # 保存 poi数据
        self.ua = UserAgent()  # 初始化 随机'User-Agent' 方法
        self.userAnent =  'user-agent="'+ self.ua.random + '"'
        print(self.userAnent)
        coordTrans = coordinateTranslate.GPS()
        self.bd09miTowgs84 = coordTrans.convert_BD09MI_to_WGS84

        self.path = createNewDir.createDir(r'./tab/baidu_map/')
        self.currFile = self.path + r'/curr.dat'
        self.nameFile = self.path + r'/name.dat'
        self.poisFile = self.path + r'/baidu_poi.csv'
        with open(self.nameFile, mode='r', encoding='gbk', errors=None) as f:  # 将采集进度写入文件
            self.nameList = [name.strip('\n') for name in f.readlines()]





    def seleniumChromeInit(self):

        # 模拟创建一个浏览器对象，然后可以通过对象去操作浏览器
        driverPath = r'./Chrome/Application/chromedriver.exe'
        self.downloadPath = r'C:\Users\Administrator\Downloads'
        # 浏览器驱动


        options = webdriver.ChromeOptions()
        prefs = {'profile.default_content_settings.popups': 0, 'download.default_directory': self.downloadPath}
        options.add_experimental_option('prefs', prefs)
        # 更换头部
        options.add_argument(self.userAnent)
        #options.add_argument("--no-sandbox")
        # options.add_argument('--headless')
        browserDriver = webdriver.Chrome(executable_path=driverPath, chrome_options=options)
        # browserDriver.maximize_window()     # 设置最大化
        # browserDriver.set_window_size(1366,900)
        self.browserDriver = browserDriver
        self.action = ActionChains(self.browserDriver)
        return browserDriver


    def openAmap(self,browserDriver,id):
        # 打开amap 首页 等待网页加载完成
        # self.url = 'https://map.baidu.com/'
        browserDriver.get(self.url)
        # 暂停2秒，已达到完全模拟浏览器的效果
        time.sleep(2)
        #等待 id 元素 加载完成
        searchBox = self.webLoadComplate(browserDriver, id)
        return browserDriver

    def webLoadComplate(self,browserDriver,id):
        # 等到id 元素载入完成 返回该元素
        try:
            # 等待到 元素载入完成  元素 出现
            element = WebDriverWait(browserDriver, 20).until(EC.presence_of_element_located((By.ID, id)))
        except Exception as e:
            print(e)
            time.sleep(1)
            return self.webLoadComplate(browserDriver,id)
            # 迭代本方法 直到加载完成...
        return element


    def searchAmap(self,browserDriver,id,word):
        searchBox = browserDriver.find_element_by_id(id)
        # 查找搜索框
        if searchBox:
            searchBox.send_keys(word)
            searchBox.send_keys(Keys.RETURN)
            return True
        else:
            print("未找到搜索框,id:",word)
            return False


    def authSlideAmap(self,browserDriver):
        #等待 iframe 加载完成
        iframeTag = self.webLoadComplate(browserDriver, "sufei-dialog-content")
        # 切换到 ifream
        browserDriver.switch_to.frame('sufei-dialog-content')

        # 等待 ifream 的 id:nc_1_n1z 的 元素加载完成
        iframeTag = self.webLoadComplate(browserDriver, "nc_1_n1z")
        # 请按住滑块，拖动到最右边
        element =browserDriver.find_element_by_xpath("//*[@id='nc_1_n1z']")
        time.sleep(2.15)
        if element:
            print("第一步,点击元素")
            ActionChains(browserDriver).click_and_hold(on_element=element).perform()
            time.sleep(0.15)
            print("第二步，拖动元素")
            x = 0
            y = 1
            while x<= 200:
                try:
                    element = browserDriver.find_element_by_xpath("//*[@id='nc_1_n1z']")
                except Exception as e:
                    print("Error, nc_1_n1z 元素不存在!!!")
                    element = None
                if element:
                    x = x+10
                    ActionChains(browserDriver).move_to_element_with_offset(to_element=element, xoffset=x,yoffset=y*(-1)).perform()
                    print(x,y)
                    time.sleep(random.randint(10, 50) / 100)
                else:
                    print("Error!!!")
                    break
            print("第三步，释放鼠标")
            # 释放鼠标
            ActionChains(browserDriver).release(on_element=element).perform()
            time.sleep(3)

        # 切换到默认的ifream
        browserDriver.switch_to.default_content()


    def get(self,url):
        htm = requests.get(url)

    def newTabGet(self,browserDriver,url):
        js = " window.open('')"
        browserDriver.execute_script(js)
        # 可以看到是打开新的标签页 不是窗口
        window = browserDriver.window_handles
        # 获取窗口(标签)列表
        browserDriver.switch_to.window(window[1])
        # 切换到新标签
        browserDriver.get(url)
        html = browserDriver.page_source

        try:
            preTag = jsonText= ''
            preTag = browserDriver.find_element_by_xpath("//pre")
            # 查找<pre> 标签
            if preTag and self.isJsonStr(preTag.text):
                jsonText = self.toJson(preTag.text)

            if html and self.isJsonStr(html):
                jsonText = self.toJson(jsonText.text)

        except Exception as e: print(e)

        browserDriver.close()
        browserDriver.switch_to.window(window[0])

        return jsonText



    def isJsonStr(self,jsonStr):
        try:
            json.loads(jsonStr)
        except ValueError:
            return False
        return True

    def toJson(self,text):
        # 字符串 反序列化
        if self.isJsonStr(text):
            return json.loads(text)


    def clearCoord(self,coordStr):
        coordStr = coordStr.split('|')[2]
        coordStr = coordStr.replace("1-","").replace(";","")
        coordList = '[' + coordStr + ']'
        coordList = eval(coordList)
        return list(zip(*(iter(coordList),) * 2))



    def miToGPS(self,lon, lat):
        coord = self.bd09miTowgs84(float(lon), float(lat))
        return coord

    def isDictKey(self,mDict,*mKey):
        # 判断 字典 mDict 存在 mKey, 并且 mKey 的值为 字典类型 返回True 否则返回 False
        tempDict = dict(mDict)
        tag = True  # 是否无效标记
        rdict = None
        for key in mKey:
            if key in tempDict.keys() and isinstance(tempDict[key],dict):
                tempDict = tempDict.get(key,'')
                if not isinstance(tempDict,dict):
                    print(key, "is not dict.")
                    tag = False
                else:
                    tag = True
            else :
                tag = False
        if tag:
            rdict = dict(tempDict)
        return rdict

    def getUuid(self,url):
        # 根据关键字返回建议的 poi 及 uuid
        try:
            result = requests.get(url)
            if result.status_code==200:
                jsonStr = result.content.decode('utf-8')
                if self.isJsonStr(jsonStr):
                    resultJson = json.loads(jsonStr)
                    sugList = resultJson.get('s', '')
                if isinstance(sugList, list):
                    return [sug.split("$") for sug in sugList]
        except Exception as e:
            print("line 1 : \n",e )


    def getPoiInfo(self,uuid):
        # 根据uuid 获取 poi 信息
        try:
            result = requests.get(self.getInfoUrl+uuid)
            if result.status_code==200:
                # http 返回状态码正常 为200

                jsonStr = result.content.decode('utf-8')
                # 将返回的数据 用 utf-8 解码

                if self.isJsonStr(jsonStr):
                    # 若jsonStr 为 json 字符串
                    resultJson = json.loads(jsonStr)
                    # 转化为 字典对象
                else:
                    print("is not json string: ",jsonStr)
                    return False

                if 'content' in resultJson.keys() and isinstance(resultJson['content'], dict):
                    # 如果字典存在 key : 'content' 且它的值是 字典对象
                    poi = resultJson.get('content', '')
                    # poi信息的字典
                else:
                    print("not found key: 'content!'")
                    return False

            else:
                print("Http respone status_code failure:", result.status_code)
                return False

            try:
                (x, y, lon, lat) = ['', '', '', '']
                # 初始化变量

                name = self.stripStr(poi.get('name', ''))
                # poi的百度 名称

                uid = self.stripStr(poi.get('uid', '')) or ''
                # poi的 uuid

                alias = self.stripStr(poi.get('alias', ''))
                # poi的 别名

                addr = self.stripStr(poi.get('addr', ''))
                # poi的 地址

                address_norm = self.stripStr(poi.get('address_norm', ''))
                # poi的 详细地址

                area = self.stripStr(poi.get('area', ''))
                # poi的面积

                area_name = self.stripStr(poi.get('area_name', ''))

                catalogID = self.stripStr(poi.get('catalogID', ''))
                # poi的 类别 id

                di_tag = self.stripStr(poi.get('di_tag', ''))
                # poi的 分类标签


                primary_uid = self.stripStr(poi.get('primary_uid', ''))
                # poi的 primary_uid

                showtag = self.stripStr(poi.get('showtag', ''))
                # poi的 展示标签

                std_tag = self.stripStr(poi.get('std_tag', ''))
                # poi的 分类标签

                std_tag_id = self.stripStr(poi.get('std_tag_id', ''))
                # poi的 分类标签id

                tel = self.stripStr(poi.get('tel', ''))
                # poi的 电话

                if len(poi.get('x', ''))>0:
                    x = poi.get('x', '')
                    y = poi.get('y', '')

                    pointGps = self.miToGPS(x, y)
                    lon = str(pointGps.get('lon', ''))
                    lat = str(pointGps.get('lat', ''))

                    x = str(x)
                    # poi的 x坐标 wgs84

                    y = str(y)
                    # poi的 y坐标 wgs84

                return [name, uid, primary_uid, alias, addr,
                         address_norm, area, area_name, catalogID, di_tag,
                         std_tag, std_tag_id, tel, x, y, lon, lat
                        ]
            except Exception as e:
                print("line 2 : \n", e)

        except Exception as e:
            print("line 3 : \n",e )

    def uuidGetGeo(self,uuid):
        url = self.getGeoUrl + uuid
        # 获取 geo 边界的 url
        #resultGeo = self.getGeo(url)
        try:
            result = requests.get(url)
            if result.status_code == 200:
                jsonStr = result.content.decode('utf-8')
                if self.isJsonStr(jsonStr):
                    resultJson = json.loads(result.content.decode('utf-8'))

                    # 判断 key 'content' 是否是字典
                    if not self.isDictKey(resultJson, 'content'):
                        return False
                    geo = resultJson.get('content', '').get('geo', '')
                    if geo == '':
                        return []
                    else:
                        if geo:
                            pylgon = []
                            # 如果存在 多边形边界
                            poiGeo = self.clearCoord(geo)
                            # print(poiGeo)
                            for coord in poiGeo:
                                # 由百度墨卡托坐标系 转换为 WGS-84 坐标系
                                gps = self.miToGPS(coord[0], coord[1])
                                pylgon.append([str(gps['lon']), str(gps['lat'])])
                            pylgon = ";".join([' '.join(node) for node in pylgon])
                            return pylgon

        except Exception as e:
            print("line 4 : \n", e)
            print('发生错误的文件：', e.__traceback__.tb_frame.f_globals['__file__'])
            print('错误所在的行号：', e.__traceback__.tb_lineno)




    def nameToGeo(self,browserDriver,buildName):
        uudiUrl = self.wdToUuidUrl + buildName

        resultList = self.getUuid(uudiUrl)
        # 搜索 建议的 关键字的 uuid 的 url

        poiInfo = []
        # 用来存储关键字返回的 poi信息的列表

        for sugPoi in  resultList:
            pylgon = []

            buildName = buildName
            # 搜索的名字

            uuid = sugPoi[5]
            # poi 的 uuid

            city = sugPoi[6]
            # 所属城市 city

            district = sugPoi[7]
            # 所属区县 district

            baiduName = sugPoi[3]
            # 百度 上的名称

            cityId = sugPoi[4]
            # 城市代码

            poiInfoes = self.getPoiInfo(uuid)
            # uuid 获取 poi 信息

            if poiInfoes:
                address = poiInfoes[4]
                # 地址

                std_tag = poiInfoes[10]
                #　poi 类型

                x = poiInfoes[15]
                y = poiInfoes[16]
                point = poiInfoes[15] + " " + poiInfoes[16]
                # 经纬度
            else:
                (address,std_tag,point) = ['', '', '']

            geo = self.uuidGetGeo(uuid)
            if  not geo or geo==[] :geo=''
            # uuid 获取  wgs-84 坐标系的 geo

            print(','.join([buildName,baiduName,uuid,city,cityId,district,address,std_tag,point,geo+'\n']))
            poiInfo.append(','.join([buildName,baiduName,uuid,city,cityId,district,address,std_tag,point,geo+'\n']))

        with open(self.poisFile,mode='a+',encoding='gbk',errors=None) as f:  # 将采集进度写入文件
            print(poiInfo)
            f.writelines(poiInfo)

        with open(self.currFile, mode='w',encoding='gbk',errors=None) as f:  # 将采集进度写入文件
            f.writelines(buildName)

    def searchBoxGetPoiList(self,wd):
        url = self.searchBoxUrl + wd
        result = requests.get(url)
        if result.status_code==200 and self.isJsonStr(result.text):
            resultJson = result.json()

        if isinstance(resultJson,dict):
            # result 字典存在 key  'content' 并且 result['content'] 是列表
            if 'content' in resultJson.keys() and isinstance(resultJson['content'],list):
                pois = resultJson.get('content')  # poi的列表
                return  pois
            else:
                print(" Not found poi.")
                return False




    def searchBoxGetPoiInfo(self,wd):
        # 搜索框获取 关键字的 poi列表信息

        poiInfoList = []
        # 最后一个 wd关键字 搜索出的所有poi的集合列表

        poiList = self.searchBoxGetPoiList(wd)
        # 搜索框的结果列表

        if poiList:
            for poi in poiList:

                try:
                    csvName = wd
                    name = self.stripStr(poi.get('name',''))
                    uid =  self.stripStr(poi.get('uid', '')) or ''
                    alias =  self.stripStr(poi.get('alias', ''))
                    addr =  self.stripStr(poi.get('addr',''))
                    address_norm =  self.stripStr(poi.get('address_norm',''))
                    area =  self.stripStr(poi.get('area',''))
                    area_name =  self.stripStr(poi.get('area_name',''))
                    catalogID =  self.stripStr(poi.get('catalogID',''))
                    di_tag =  self.stripStr(poi.get('di_tag',''))
                    primary_uid = self.stripStr(poi.get('primary_uid', ''))
                    std_tag =  self.stripStr(poi.get('std_tag', ''))
                    std_tag_id =  self.stripStr(poi.get('std_tag_id', ''))
                    tel =  self.stripStr(poi.get('tel', ''))

                    if isinstance(poi.get('x', ''),int):
                        x = poi.get('x', '')/100
                        y = poi.get('y', '')/100

                        pointGps = self.miToGPS(x, y)
                        lon = str(pointGps.get('lon', ''))
                        lat = str(pointGps.get('lat', ''))
                        x=str(x)
                        y=str(y)

                    geo = self.uuidGetGeo(uid)
                    if geo==[]: geo=''
                    print(",".join(
                        [csvName, name, uid, primary_uid, alias, addr,
                         address_norm, area, area_name, catalogID, di_tag,
                         std_tag, std_tag_id, tel, x, y, lon, lat, geo]))

                    poiInfoList.append(",".join(
                        [csvName, name, uid, primary_uid, alias, addr,
                         address_norm, area, area_name, catalogID, di_tag,
                         std_tag, std_tag_id, tel, x, y, lon, lat, geo + '\n'])
                        )

                    (pylgon, csvName, name, uid, primary_uid, alias, addr,
                     address_norm, area, area_name, catalogID, di_tag, std_tag,
                     std_tag_id, tel, x, y, lon, lat, geo
                     ) = [[], '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '']
                except Exception as e: print(e)

            with open(self.poisFile, mode='a+', encoding='gbk', errors=None) as f:  # 将采集进度写入文件
                f.writelines(poiInfoList)
            with open(self.currFile, mode='w', encoding='gbk', errors=None) as f:  # 将采集进度写入文件
                f.writelines(wd)

    def searchPoi(self,browserDriver,buildName):
        # if self.searchAmap(browserDriver,searchBoxId, "安康学院"):
        #     print(browserDriver.title)
        # 返回 请求的返回数据
        poiInfo = []
        url = self.searchUrl + buildName
        result = self.newTabGet(browserDriver, url)
        if isinstance(result,dict):
            # result 字典存在 key  'content' 并且 result['content'] 是列表
            if 'content' in result.keys() and isinstance(result['content'],list):
                pois = result.get('content')  # poi的列表
            else:
                print(" Not found poi.")
                return False

            for poi in pois:
                (pylgon, geoMi, x, y, lon, lat) = [[],'','','','','']  # 清空变量
                try:
                    geoMi = self.isDictKey(poi, 'ext', 'detail_info', 'guoke_geo')
                    if isinstance(geoMi,dict):
                        geoMi = geoMi.get('geo','')
                        if geoMi:
                            # 如果存在 多边形边界
                            poiGeo = self.clearCoord(geoMi)
                            # print(poiGeo)
                            for coord in poiGeo:
                                # 由百度墨卡托坐标系 转换为 WGS-84 坐标系
                                gps = self.miToGPS(coord[0], coord[1])
                                pylgon.append([str(gps['lon']),str(gps['lat'])])
                            pylgon = ";".join([' '.join(node) for node in pylgon])
                            print(pylgon)
                    if not pylgon: pylgon=''

                except Exception as e: print(e)

                try:
                    csvName = buildName
                    name = self.stripStr(poi.get('name',''))
                    uid =  self.stripStr(poi.get('uid', '')) or ''
                    alias =  self.stripStr(poi.get('alias', ''))
                    addr =  self.stripStr(poi.get('addr',''))
                    address_norm =  self.stripStr(poi.get('address_norm',''))
                    area =  self.stripStr(poi.get('area',''))
                    area_name =  self.stripStr(poi.get('area_name',''))
                    catalogID =  self.stripStr(poi.get('catalogID',''))
                    di_tag =  self.stripStr(poi.get('di_tag',''))
                    primary_uid = self.stripStr(poi.get('primary_uid', ''))
                    std_tag =  self.stripStr(poi.get('std_tag', ''))
                    std_tag_id =  self.stripStr(poi.get('std_tag_id', ''))
                    tel =  self.stripStr(poi.get('tel', ''))

                    if isinstance(poi.get('x', ''),int):
                        x = poi.get('x', '')/100
                        y = poi.get('y', '')/100

                        pointGps = self.miToGPS(x, y)
                        lon = str(pointGps.get('lon', ''))
                        lat = str(pointGps.get('lat', ''))
                        x=str(x)
                        y=str(y)

                    poiInfo.append(",".join(
                        [csvName, name, uid, primary_uid, alias, addr,
                         address_norm, area, area_name, catalogID, di_tag,
                         std_tag, std_tag_id, tel, x, y, lon, lat, pylgon + '\n'])
                    )


                except Exception as e: print(e)

            with open(self.poisFile,mode='a+',encoding='gbk',errors=None) as f:  # 将采集进度写入文件
                f.writelines(poiInfo)
            with open(self.currFile, mode='w',encoding='gbk',errors=None) as f:  # 将采集进度写入文件
                f.writelines(buildName )

    def stripStr(self,tmp):
        result = str(tmp)
        result = result.strip()
        result = result.replace(",", ';')
        result = result.replace("\n", '')
        result = result.replace("\r", '')
        result = result.replace("\t", ' ')
        result = result.strip()
        return result

    def readCurr(self):
        # 从文件中读取 最后一次采集的 name   并返回这个名字 在列表中的index 未找到返回 0
        if os.path.isfile(self.currFile):
            with open(self.currFile, mode='r', encoding='gbk', errors=None) as f:  # 将采集进度写入文件
                currName = f.readline()
            if currName in self.nameList:
                return self.nameList.index(currName)

        return 0

    def main(self):
        # browserDriver = self.seleniumChromeInit()
        # 初始化selenium Chrome 对象
        # searchBoxId = 'sole-input'
        # browserDriver = self.openAmap(browserDriver,searchBoxId)
        # 打开amap首页

        # 如果不存在 poiFile 则建立并写入表头
        if not os.path.isfile(self.poisFile):
            with open(self.poisFile, mode='a+', encoding='gbk', errors=None) as f:  # 将表头写入文件
                # f.writelines("csvName,name,uid,primary_uid,alias,addr,address_norm,area,area_name,catalogID,di_tag,std_tag,std_tag_id,tel,x,y,lon,lat,pylgon\n")
                f.writelines("csvName,name,uid,primary_uid,alias,addr,address_norm,area,area_name,catalogID,di_tag,std_tag,std_tag_id,tel,x,y,lon,lat,geo\n")



        curr = self.readCurr()

        for name in self.nameList[curr:-1]:
            # self.searchPoi(browserDriver, name)
            self.searchBoxGetPoiInfo(name)
            # self.nameToGeo(browserDriver, name)
            print(name)







if __name__=="__main__":
    baiduMap = GetBaiduMap("./build.csv")
    baiduMap.main()


    print("complate!")


































































