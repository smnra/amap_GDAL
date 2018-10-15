#!usr/bin/env python  
#-*- coding:utf-8 _*-  

""" 
@author:Administrator 
@file: test2.py 
@time: 2018/10/{DAY} 
描述: 

"""

import requests , re

parameter = {
        "newmap": "1",
        "reqflag": "pcmap",
        "biz": "1",
        "from": "webmap",
        "da_par": "direct",
        "pcevaname": "pc4.1",
        "qt": "con",
        "c": 233,            # 城市代码
        "wd": "学",       # 搜索关键词
        "wd2": "",
        "pn": 1,           # 页数
        "nn": 1 * 10,
        "db": "0",
        "sug": "0",
        "addr": "0",
        "da_src": "pcmappg.poi.page",
        "on_gel": "1",
        "src": "7",
        "gr": "3",
        "l": "12",
        "tn": "B_NORMAL_MAP",
        # "u_loc": "12621219.536556,2630747.285024",
        "ie": "utf-8",
        # "b": "(11845157.18,3047692.2;11922085.18,3073932.2)",  #这个应该是地理位置坐标，可以忽略
        "t": "1468896652886"
    }


url = 'http://map.baidu.com/'
htm = requests.get(url, params=parameter)
htm = htm.text.encode('latin-1').decode('unicode_escape')  # 转码
pattern = r'(?<=\baddress_norm":"\[).+?(?="ty":)'
htm = re.findall(pattern, htm)  # 按段落匹配

for r in htm:
    pattern = r'(?<=\b"\},"name":").+?(?=")'
    name = re.findall(pattern, r)
    if not name:
        pattern = r'(?<=\b,"name":").+?(?=")'
        name = re.findall(pattern, r)
        print(name[0])  # 名称

    pattern = r'.+?(?=")'
    adr = re.findall(pattern, r)
    pattern = r'\(.+?\['
    address = re.sub(pattern, ' ', adr[0])
    pattern = r'\(.+?\]'
    address = re.sub(pattern, ' ', address)
    print(address)  # 地址

    pattern = r'(?<="phone":").+?(?=")'
    phone = re.findall(pattern, r)
    print(phone[0])  # 电话
