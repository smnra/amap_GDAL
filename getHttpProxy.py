# -*- coding:UTF-8 -*-


import requests
from bs4 import BeautifulSoup
import  createNewDir


url = 'http://www.xicidaili.com/nt/'
headers = {'Upgrade-Insecure-Requests': '1',
           'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
           'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
           'Accept-Encoding': 'gzip, deflate, sdch, br',
           'Accept-Language': 'zh-CN,zh;q=0.8',
           }

i = 1
html = requests.get(url + str(i), timeout = 10, headers = headers)                #获取url 网址的网页html
print(html)
soup = BeautifulSoup(html.text , 'lxml')

ipList = soup.select('#ip_list')                            #返回 id 为 'ip_list' 的 所有节点

table = ipList[0].contents                                 #返回子节点列表
th = table[0]
tagList = []

for tr in table:
    if isinstance(tr,'Tag'):
        tagList.append(tr)
    else:
        print('空行 : ',tr)

print(ipList[0])