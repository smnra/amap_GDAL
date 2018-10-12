#!usr/bin/env python
#-*- coding:utf-8 _*-

"""
@author:Administrator
@file: amap_selenium_chrome.py
@time: 2018/10/07
描述: selenium  高德地图 chrome  采集小区边界

"""


import requests,re,time,os, random,json,math
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

'''
用 url:  'https://map.baidu.com/su?wd=%E8%9E%8D%E4%BE%A8%20&cid=233&type=0&newmap=1&b=(12121496.865%2C4038346.77%3B12121862.365%2C4038655.77)&t=1539339239819&pc_ver=2'
搜索出可能的 名字 和 uuid

'https://map.baidu.com/?newmap=1&reqflag=pcmap&biz=1&from=webmap&da_par=direct&pcevaname=pc4.1&qt=ext&c=233&ext_ver=new&tn=B_NORMAL_MAP&nn=0&ie=utf-8&l=17&uid=3c753948c9a2427235b06c64'
然后用这个url查找 是否存在 pylgon

'''



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



    def miToGPS(self,browserDriver,lon, lat):
        coord = self.bd09miTowgs84(lon, lat)
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
                                gps = self.miToGPS(browserDriver, coord[0], coord[1])
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

                        pointGps = self.miToGPS(browserDriver, x, y)
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
        browserDriver = self.seleniumChromeInit()
        # 初始化selenium Chrome 对象
        searchBoxId = 'sole-input'
        browserDriver = self.openAmap(browserDriver,searchBoxId)
        # 打开amap首页

        # 如果不存在 poiFile 则建立并写入表头
        if not os.path.isfile(self.poisFile):
            with open(self.poisFile, mode='a+', encoding='gbk', errors=None) as f:  # 将表头写入文件
                f.writelines("csvName,name,uid,primary_uid,alias,addr,address_norm,area,area_name,catalogID,di_tag,std_tag,std_tag_id,tel,x,y,lon,lat,pylgon\n")

        curr = self.readCurr()

        for name in self.nameList[curr:-1]:
            self.searchPoi(browserDriver, name)
            print(name)




    def searchWd(self,browserDriver,wd):
        url = 'http://map.baidu.com/?newmap=1&reqflag=pcmap&biz=1&from=webmap&da_par=direct&pcevaname=pc4.1&qt=s&da_src=searchBox.button&wd='
        browserDriver.get(url+wd);



if __name__=="__main__":
    baiduMap = GetBaiduMap("./build.csv")
    baiduMap.main()


    print("complate!")


































































