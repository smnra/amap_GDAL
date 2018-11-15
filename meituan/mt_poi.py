#!usr/bin/env python  
#-*- coding:utf-8 _*-  

""" 
@author:Administrator 
@file: mt_poi.py 
@time: 2018/11/{DAY} 
描述: 

"""

# coding=utf-8
import csv
import time
import requests
import json
import meituan.meituan_selenium as mt
import requests
from requests.cookies import RequestsCookieJar


# 区域店铺id ct_Poi cateName抓取，传入参数为区域id
def crow_id(areaid,cookie):
    id_list = []
    url = 'https://meishi.meituan.com/i/api/channel/deal/list'
    head = {"Accept": "application/json",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Content-Length": "371",
            "Content-Type": "application/json",
            "DNT": "1",
            "Host": "meishi.meituan.com",
            "Origin": "https://meishi.meituan.com",
            "Pragma": "no-cache",
            "Referer": "https://meishi.meituan.com/i/?ci=42&stid_b=0",
            "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.162 Safari/537.36 Avast/65.0.411.162",
            "x-requested-with": "XMLHttpRequest",
            "Cookie": "__mta=45888155.1541148357549.1542187318996.1542187328326.18; iuuid=EE5893B5D2C219A684B1BA25271AB6F834A1DC9634EADB340BFDB6BDA984E46F; _lxsdk_cuid=1653bf57b9e42-064eff1fa336df-252b1971-100200-1653bf57b9f61; _lxsdk=EE5893B5D2C219A684B1BA25271AB6F834A1DC9634EADB340BFDB6BDA984E46F; _hc.v=7ef28d0d-ed51-ad2f-1b7f-662935ef4790.1541148357; rvct=30%2C91%2C42; uuid=03df37e63fdb4de19ac1.1542094402.1.0.0; client-id=2e5d402c-e65f-45ca-99c4-e9dd7aee824f; IJSESSIONID=qgbfrpr6vha8ws656dcrwxpg; webp=1; __utmc=74597006; ci3=1; cityname=%E8%A5%BF%E5%AE%89; ci=42; latlng=; __utma=74597006.49736465.1542178395.1542178395.1542184151.2; __utmz=74597006.1542184151.2.2.utmcsr=meishi.meituan.com|utmccn=(referral)|utmcmd=referral|utmcct=/i/; i_extend=H__a100001__b2",
            }
    p = {'https': 'https://27.157.76.75:4275'}
    data = {"app":"",
            "areaId":907,
            "cateId":1,
            "deal_attr_23":"",
            "deal_attr_24":"",
            "deal_attr_25":"",
            "limit":15,
            "lineId":0,
            "offset":0,
            "optimusCode":10,
            "originUrl":"http://meishi.meituan.com/i/?ci=42&stid_b=0",
            "partner":126,
            "platform":3,
            "poi_attr_20033":"",
            "poi_attr_20043":"",
            "riskLevel":1,
            "sort":"default",
            "stationId":0,
            "uuid":"15405c529f2e42959aa8.1542243858.1.0.0",
            "version":"8.2.0"
            }
    # r = requests.post(url, headers=head, data=data, cookies=cookie,proxies=p)
    r = requests.post(url, headers=head, data=data, cookies=cookie)
    result = json.loads(r.text)
    totalcount = result['data']['poiList']['totalCount']  # 获取该分区店铺总数，计算出要翻的页数
    datas = result['data']['poiList']['poiInfos']
    print(len(datas), totalcount)
    for d in datas:
        d_list = ['', '', '', '']
        d_list[0] = d['name']
        d_list[1] = d['cateName']
        d_list[2] = d['poiid']
        d_list[3] = d['ctPoi']
        id_list.append(d_list)
    print('Page：1')
    # 将数据保存到本地csv
    with open('meituan_id.csv', 'a', newline='', encoding='gb18030')as f:
        write = csv.writer(f)
        for i in id_list:
            write.writerow(i)

    # 开始爬取第2页到最后一页
    offset = 0
    if totalcount > 15:
        totalcount -= 15
        while offset < totalcount:
            id_list = []
            offset += 15
            m = offset / 15 + 1
            print('Page:%d' % m)
            # 构造post请求参数，通过改变offset实现翻页
            data2 = {"uuid": "09dbb48e-4aed-4683-9ce5-c14b16ae7539", "version": "8.3.3", "platform": 3, "app": "",
                     "partner": 126, "riskLevel": 1, "optimusCode": 10,
                     "originUrl": "http://meishi.meituan.com/i/?ci=30&stid_b=1&cevent=imt%2Fhomepage%2Fcategory1%2F1",
                     "offset": offset, "limit": 15, "cateId": 1, "lineId": 0, "stationId": 0, "areaId": areaid,
                     "sort": "default",
                     "deal_attr_23": "", "deal_attr_24": "", "deal_attr_25": "", "poi_attr_20043": "",
                     "poi_attr_20033": ""}
            try:
                r = requests.post(url, headers=head, data=data2, proxies=p)
                print(r.text)
                result = json.loads(r.text)
                datas = result['data']['poiList']['poiInfos']
                print(len(datas))
                for d in datas:
                    d_list = ['', '', '', '']
                    d_list[0] = d['name']
                    d_list[1] = d['cateName']
                    d_list[2] = d['poiid']
                    d_list[3] = d['ctPoi']
                    id_list.append(d_list)
                # 保存到本地
                with open('meituan_id.csv', 'a', newline='', encoding='gb18030')as f:
                    write = csv.writer(f)
                    for i in id_list:
                        write.writerow(i)
            except Exception as e:
                print(e)

def getCtycode(provinceName):
    result = requests.get('https://www.meituan.com/ptapi/getprovincecityinfo/')
    resultJson = result.json()
    return resultJson


def getCookies():
    # 初始化 selenium Chrome
    meituan = mt.GetMeituan()
    browserDriver = meituan.seleniumChromeInit()

    # 获取selenium Cookies
    cookies = meituan.getCookie()

    # 准备处理 requests cookie 模块
    mtCookie = RequestsCookieJar()
    for cookie in cookies:
        mtCookie.set(cookie['name'], cookie['value'])
    print(mtCookie)
    #　r = s.get("https://www.baidu.com/p/setting/profile/basic", cookies=mtCookie)
    return mtCookie




if __name__ == '__main__':
    cityCode = getCtycode('陕西')

    # 直接将html代码中区域的信息复制出来，南澳新区的数据需要处理下，它下面没有分区
    # https://meishi.meituan.com/i/?ci=42&stid_b=25#
    a = {"areaObj": {"113":[{"id":113,"name":"全部","regionName":"碑林区","count":1816},
                            {"id":6835,"name":"东大街","regionName":"东大街","count":114},
                            {"id":7137,"name":"南大街","regionName":"南大街","count":75},
                            {"id":897,"name":"钟楼/鼓楼","regionName":"钟楼/鼓楼","count":239},
                            {"id":898,"name":"西北大/西工大","regionName":"西北大/西工大","count":87},
                            {"id":899,"name":"和平门/建国门","regionName":"和平门/建国门","count":30},
                            {"id":908,"name":"交大/理工大","regionName":"交大/理工大","count":72},
                            {"id":7402,"name":"南稍门","regionName":"南稍门","count":283},
                            {"id":7404,"name":"东关正街","regionName":"东关正街","count":100},
                            {"id":8974,"name":"立丰国际","regionName":"立丰国际","count":16},
                            {"id":8975,"name":"太乙路","regionName":"太乙路","count":19},
                            {"id":9012,"name":"长安立交","regionName":"长安立交","count":26},
                            {"id":15634,"name":"怡丰城/西荷花园","regionName":"怡丰城/西荷花园","count":62},
                            {"id":15639,"name":"互助路立交","regionName":"互助路立交","count":46},
                            {"id":15642,"name":"李家村","regionName":"李家村","count":186},
                            {"id":15643,"name":"朱雀大街北段","regionName":"朱雀大街北段","count":59},
                            {"id":15664,"name":"文艺路","regionName":"文艺路","count":101},
                            {"id":15667,"name":"黄雁村","regionName":"黄雁村","count":73},
                            {"id":15784,"name":"劳动南路","regionName":"劳动南路","count":15},
                            {"id":15785,"name":"广济街","regionName":"广济街","count":136}],
                     "114":[{"id":114,"name":"全部","regionName":"新城区","count":1194},
                            {"id":7476,"name":"新城广场","regionName":"新城广场","count":55},
                            {"id":7142,"name":"民乐园","regionName":"民乐园","count":272},
                            {"id":901,"name":"解放路/火车站","regionName":"解放路/火车站","count":79},
                            {"id":6838,"name":"互助立交","regionName":"互助立交","count":5},
                            {"id":7143,"name":"胡家庙","regionName":"胡家庙","count":57},
                            {"id":902,"name":"金花路","regionName":"金花路","count":153},
                            {"id":8985,"name":"韩森寨","regionName":"韩森寨","count":52},
                            {"id":18674,"name":"矿山路","regionName":"矿山路","count":17},
                            {"id":36710,"name":"大明宫遗址公园","regionName":"大明宫遗址公园","count":19},
                            {"id":37380,"name":"建工路","regionName":"建工路","count":254},
                            {"id":39163,"name":"万寿路","regionName":"万寿路","count":23},
                            {"id":39296,"name":"康复路","regionName":"康复路","count":2}],
                     "115":[{"id":115,"name":"全部","regionName":"莲湖区","count":1269},
                            {"id":903,"name":"劳动公园","regionName":"劳动公园","count":59},
                            {"id":7479,"name":"丰庆公园","regionName":"丰庆公园","count":25},
                            {"id":7405,"name":"北关正街","regionName":"北关正街","count":29},
                            {"id":904,"name":"汉城路沿线","regionName":"汉城路沿线","count":56},
                            {"id":905,"name":"莲湖公园","regionName":"莲湖公园","count":74},
                            {"id":906,"name":"西大街","regionName":"西大街","count":48},
                            {"id":6839,"name":"北大街","regionName":"北大街","count":21},
                            {"id":7408,"name":"西稍门","regionName":"西稍门","count":115},
                            {"id":7480,"name":"劳动南路","regionName":"劳动南路","count":119},
                            {"id":8982,"name":"土门","regionName":"土门","count":62},
                            {"id":14024,"name":"大兴新区","regionName":"大兴新区","count":167},
                            {"id":14025,"name":"红庙坡","regionName":"红庙坡","count":180}],
                     "116":[{"id":116,"name":"全部","regionName":"雁塔区","count":2480},
                            {"id":907,"name":"小寨","regionName":"小寨","count":492},
                            {"id":1099,"name":"电子城","regionName":"电子城","count":286},
                            {"id":4763,"name":"曲江新区","regionName":"曲江新区","count":194},
                            {"id":6836,"name":"大雁塔","regionName":"大雁塔","count":324},
                            {"id":7403,"name":"朱雀大街南段","regionName":"朱雀大街南段","count":68},
                            {"id":8977,"name":"南二环西段","regionName":"南二环西段","count":54},
                            {"id":8978,"name":"南二环东段","regionName":"南二环东段","count":17},
                            {"id":8979,"name":"明德门","regionName":"明德门","count":96},
                            {"id":8984,"name":"雁翔路","regionName":"雁翔路","count":136},
                            {"id":15630,"name":"西影路","regionName":"西影路","count":57},
                            {"id":15632,"name":"电视塔","regionName":"电视塔","count":166},
                            {"id":15635,"name":"含光路南段","regionName":"含光路南段","count":101},
                            {"id":15640,"name":"政法/师大","regionName":"政法/师大","count":118},
                            {"id":15641,"name":"吉祥村","regionName":"吉祥村","count":75}],
                     "117":[{"id":117,"name":"全部","regionName":"未央区","count":2343},
                            {"id":909,"name":"未央路","regionName":"未央路","count":662},
                            {"id":7407,"name":"朱宏路","regionName":"朱宏路","count":69},
                            {"id":7478,"name":"明光路","regionName":"明光路","count":100},
                            {"id":7477,"name":"文景路","regionName":"文景路","count":231},
                            {"id":7406,"name":"太华路","regionName":"太华路","count":187},
                            {"id":8950,"name":"龙首村","regionName":"龙首村","count":23},
                            {"id":7140,"name":"大明宫","regionName":"大明宫","count":66},
                            {"id":8951,"name":"赛高街区","regionName":"赛高街区","count":48},
                            {"id":8952,"name":"城市运动公园","regionName":"城市运动公园","count":51},
                            {"id":7141,"name":"辛家庙","regionName":"辛家庙","count":209},
                            {"id":7138,"name":"北大学城","regionName":"北大学城","count":98},
                            {"id":9309,"name":"大明宫万达","regionName":"大明宫万达","count":25},
                            {"id":9477,"name":"红旗厂","regionName":"红旗厂","count":62},
                            {"id":13026,"name":"三桥","regionName":"三桥","count":183},
                            {"id":25592,"name":"和平村","regionName":"和平村","count":48},
                            {"id":37367,"name":"西安北站","regionName":"西安北站","count":21}],
                     "119":[{"id":119,"name":"全部","regionName":"高新区","count":1399},
                            {"id":910,"name":"高新路","regionName":"高新路","count":64},
                            {"id":8980,"name":"光华路","regionName":"光华路","count":47},
                            {"id":8983,"name":"科技路西口","regionName":"科技路西口","count":250},
                            {"id":8991,"name":"唐延路南段","regionName":"唐延路南段","count":120},
                            {"id":15629,"name":"大寨路","regionName":"大寨路","count":140},
                            {"id":15631,"name":"唐延路北段","regionName":"唐延路北段","count":42},
                            {"id":15633,"name":"绿地世纪城","regionName":"绿地世纪城","count":167},
                            {"id":15636,"name":"西万路口","regionName":"西万路口","count":32},
                            {"id":15637,"name":"枫林绿洲","regionName":"枫林绿洲","count":199},
                            {"id":15638,"name":"徐家庄","regionName":"徐家庄","count":83},
                            {"id":15646,"name":"高新软件园","regionName":"高新软件园","count":117},
                            {"id":15647,"name":"玫瑰大楼","regionName":"玫瑰大楼","count":126}],
                     "235":[{"id":235,"name":"全部","regionName":"长安区","count":1114},
                            {"id":7145,"name":"秦岭沿线","regionName":"秦岭沿线","count":123},
                            {"id":7146,"name":"长安广场","regionName":"长安广场","count":223},
                            {"id":7147,"name":"郭杜","regionName":"郭杜","count":150},
                            {"id":7148,"name":"南大学城","regionName":"南大学城","count":198},
                            {"id":15644,"name":"三森","regionName":"三森","count":59},
                            {"id":15645,"name":"紫薇田园都市","regionName":"紫薇田园都市","count":83},
                            {"id":15665,"name":"韦曲西街","regionName":"韦曲西街","count":101},
                            {"id":15666,"name":"韦曲南站","regionName":"韦曲南站","count":45},
                            {"id":15668,"name":"航天城","regionName":"航天城","count":57}],
                     "4251":[{"id":4251,"name":"全部","regionName":"灞桥区","count":695},
                            {"id":7398,"name":"纺织城","regionName":"纺织城","count":177},
                            {"id":7399,"name":"十里铺","regionName":"十里铺","count":72},
                            {"id":7400,"name":"白鹿原","regionName":"白鹿原","count":56},
                            {"id":7401,"name":"浐灞半岛/世园会","regionName":"浐灞半岛/世园会","count":114},
                            {"id":14199,"name":"田洪正街","regionName":"田洪正街","count":56},
                            {"id":16010,"name":"城东客运站","regionName":"城东客运站","count":101},
                            {"id":16013,"name":"灞桥火车站","regionName":"灞桥火车站","count":51},
                            {"id":25659,"name":"长乐坡","regionName":"长乐坡","count":46}],
                     "4253":[{"id":4253,"name":"全部","regionName":"临潼区","count":355},
                            {"id":8986,"name":"兵马俑","regionName":"兵马俑","count":31},
                            {"id":8987,"name":"人民路/文化路","regionName":"人民路/文化路","count":97},
                            {"id":8989,"name":"华清宫","regionName":"华清宫","count":47},
                            {"id":8990,"name":"东三岔","regionName":"东三岔","count":44},
                            {"id":17228,"name":"芷阳湖","regionName":"芷阳湖","count":69}],
                     "4254":[{"id":4254,"name":"全部","regionName":"蓝田县","count":88},
                            {"id":23761,"name":"向阳路","regionName":"向阳路","count":23},
                            {"id":23762,"name":"北环路","regionName":"北环路","count":31},
                            {"id":23763,"name":"汤峪镇","regionName":"汤峪镇","count":7}],
                     "4255":[{"id":4255,"name":"全部","regionName":"周至县","count":104},
                            {"id":22410,"name":"周至汽车站","regionName":"周至汽车站","count":3},
                            {"id":22416,"name":"武商购物广场","regionName":"武商购物广场","count":17},
                            {"id":39395,"name":"沙河村","regionName":"沙河村","count":""}],
                     "4256":[{"id":4256,"name":"全部","regionName":"鄠邑区","count":123},
                            {"id":22405,"name":"娄敬路","regionName":"娄敬路","count":9},
                            {"id":22408,"name":"草堂路","regionName":"草堂路","count":21},
                            {"id":26289,"name":"余下镇","regionName":"余下镇","count":5},
                            {"id":26295,"name":"人民路","regionName":"人民路","count":28}],
                     "4257":[{"id":4257,"name":"全部","regionName":"高陵区","count":264},
                            {"id":16938,"name":"高陵县城","regionName":"高陵县城","count":95},
                            {"id":25170,"name":"车城花园","regionName":"车城花园","count":72},
                            {"id":25171,"name":"马家湾","regionName":"马家湾","count":55}],
                     "7149":[{"id":7149,"name":"全部","regionName":"阎良区","count":111},
                            {"id":25713,"name":"前进路","regionName":"前进路","count":6},
                            {"id":25715,"name":"千禧广场","regionName":"千禧广场","count":13},
                            {"id":25717,"name":"润天大道","regionName":"润天大道","count":20},
                            {"id":25719,"name":"凤凰广场","regionName":"凤凰广场","count":8},
                            {"id":25721,"name":"蓝天广场","regionName":"蓝天广场","count":8}]
                     }}

    datas = a['areaObj']
    b = datas.values()
    area_list = []
    for data in b:
        for d in data[1:]:
            area_list.append(d)  # 将每个区域信息保存到列表，元素是字典
    l = 0
    old = time.time()
    mtCookie = getCookies()
    for i in area_list:
        l += 1
        print('开始抓取第%d个区域：' % l, i['regionName'], '店铺总数：', i['count'])
        # try:
        if 1:
            crow_id(i['id'],mtCookie)
            now = time.time() - old
            print(i['name'], '抓取完成！', '时间:%d' % now)
        # except Exception as e:
        #     print(e)

