# -*- coding:UTF-8 -*-
import requests
import json
import time

pageNumber = 1

url = 'http://restapi.amap.com/v3/place/polygon'
headers = {'Upgrade-Insecure-Requests': '1',
           'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
           'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
           'Accept-Encoding': 'gzip, deflate, sdch, br',
           'Accept-Language': 'zh-CN,zh;q=0.8',
           }
pm = {'polygon': '107.124295,34.38007;107.15322,34.344148',
      'key': '7d3ff5a71f84c7446140f6cab819bd81',
      'extensions': 'base',       #返回结果控制 可选 为 "all"  或者 "base"
      'offset': 10,          #分页大小,高德地图分最大每页50个 强烈建议不超过25，若超过25可能造成访问报错
      'page': 1            #第几页 	最大翻页数100
      }


'''
此段用于计算 maxPage  最大页数
'''
poiRequest = requests.get(url, params=pm)  # 发送get 请求
poiJsons = json.loads(poiRequest.text)  # 用json 格式化服务器返回的text字符串
maxPage = int(poiJsons['count']) // 10 - 1  # 重json的 'count" 字段取得 经纬度范围内的POI的数量 然后除以分页大小 减去1 就是循环的最大页数
'''
此段用于计算 maxPage  最大页数
'''




'''
根据POI ID 获取 边界多边形
https://gaode.com/service/poiInfo?query_type=IDQ&pagesize=20&pagenum=1&qii=true&cluster_state=5&need_utd=true&utd_sceneid=1000&div=PC1000&addr_poi_merge=true&is_classify=true&zoom=11&id=B000A84IMM
'''
regionUrl= 'https://gaode.com/service/poiInfo?query_type=IDQ&pagesize=20&pagenum=1&qii=true&cluster_state=5&need_utd=true&utd_sceneid=1000&div=PC1000&addr_poi_merge=true&is_classify=true&zoom=11&id='






pois = []
for i in range(1,maxPage) :                     #循环 从第一页开始到最后一页
    poiRequest = requests.get(url, params=pm,)    # 发送get 请求
    poiJsons = json.loads(poiRequest.text)          #用json 格式化服务器返回的text字符串
    pm.update({'page': i + 1})                     # 当前页数加1

    for index,poi in enumerate(poiJsons['pois']):     #遍历整页的POI ID
        #print(str(poi['name']), str(poi['id']))
        regionRequest = requests.get(regionUrl + str(poi['id']))   #发送单个get 根据 POI 的 ID  获取 bound 经纬度
        regionJsons = json.loads(regionRequest.text)                # 格式化 json数据 为字典
        if regionJsons['data'] == 'too fast':                    # 判断取回的数据是否是 'too fast'  由于请求速度过快 造成的 异常数据
            time.sleep(3)                                           #延迟3秒再次请求
            regionRequest = requests.get(regionUrl + str(poi['id']))  # 发送单个get 根据 POI 的 ID  获取 bound 经纬度
            regionJsons = json.loads(regionRequest.text)  # 格式化 json数据 为字典
        else :
            poiJsons['pois'][index].update({'bound':regionJsons['data']['bounds']})       #把获取到的 bound 经纬度 更新到 单个的pois中
            print(str(poi['name']), str(poi['id']),regionJsons['data']['bounds'])          # 打印 POI 的  名字 ID  和 bounds


    pois.extend(list(poiJsons['pois']))                   #把poi 列表 添加到 pois 列表中保存