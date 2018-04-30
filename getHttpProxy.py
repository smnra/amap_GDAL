# -*- coding:UTF-8 -*-
#获取西刺 代理网站 的 国内http 代理 列表

import requests
from bs4 import BeautifulSoup
import createNewDir
import time
import re

verifyUrl = 'https://ditu.amap.com/detail/get/detail'               #高德地图 验证连通性url              'https://pv.sohu.com/cityjson'  返回IP归属地的验证地址
url = 'http://www.xicidaili.com/wt/'
headers = {'Upgrade-Insecure-Requests': '1',
           'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
           'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
           'Accept-Encoding': 'gzip, deflate, sdch, br',
           'Accept-Language': 'zh-CN,zh;q=0.8',
           }

def proxyVerify(ip, port, protocol='https'):
    # 验证代理是否有效
    # verifyUrl = 'https://ditu.amap.com/detail/get/detail'       #高德地图验证  存在字符串 'status'
    verifyUrl = 'http://whois.pconline.com.cn/'           # 获取ip归属地验证   存在字符串 'ip'

    if protocol.lower() == 'http':
        proxies = {"http": "http://" + ip + ":" + port ,
                   "https": "https://" + ip + ":" + port}

    try:
        s = requests.session()                                      # 创建 session
        s.proxies = proxies  # 设置http代理                             #设置 session proxies 代理
        html = s.get(verifyUrl, timeout=10, headers=headers)            #get() 方法 打开 verifyUrl
        if 'X-Forwarded-For' in html.text:                                          #如果返回的text中存在 字符串 'cip'
            matchObj = re.match(r'.*\t\t位置：(.*?)\r\n.*X-Real-IP=(.*?)\n', html.text, re.DOTALL | re.I)         # 定义一个正则表达式对象用来提取 ip 和地址   re.DOTALL  多行匹配   re.I大小写不敏感
            address = matchObj.group(1)                                #匹配 地址信息
            proxyIp = matchObj.group(2)                                 #匹配 IP
            delay =  html.elapsed.total_seconds()                       #打开网页所用时间
            print(proxyIp, port , address , delay)                             #
            return html.elapsed.total_seconds()                            #返回 打开网页的时间
        else:
            return False                                                   #不存在就返回False

    except requests.exceptions.ConnectionError:                             #捕捉异常
        print('可能是代理不通: ConnectionError -- please wait 3 seconds')
        return False                                                        #有异常的返回 False
    except requests.exceptions.ChunkedEncodingError:
        print('ChunkedEncodingError -- please wait 3 seconds')
        return False
    except:
        print('Unfortunitely -- An Unknow Error Happened, Please wait 3 seconds')
        return False
    finally:
        s = None                                #复位 session s







i = 1
filePath = createNewDir.createNewDir()
file = open(filePath + 'ip.txt', 'a+', encoding='utf-8')


for i in range(1,11) :
    try:
        html = requests.get(url + str(i), timeout = 10, headers = headers)                #获取url 网址的网页html
        proxyList = []
        ipList = []
        table = []
        if html.status_code == 200:
            soup = BeautifulSoup(html.text, 'html.parser')              #把html 字符串实例化为BeautifulSoup 对象
            ipList = soup.select('#ip_list')                            #返回 id 为 'ip_list' 的 所有节点
            table = ipList[0].contents                                 #返回子节点列表
        else :
            break

        for tr in table:
            if tr.string == None  and tr.contents[3].string != 'IP地址':                                       #如果tr有子元素 则 tr.string 的值为None  否则 tr.string 为 标签的 text   并且 不是表头 (不包含'IP地址')
                ip = tr.contents[3].string              #ip地址
                port = tr.contents[5].string            # 端口
                protocol = tr.contents[11].string        # 协议 'http'  或者  'https'
                if proxyVerify(ip, port, protocol)  :
                    ipPort = ip + ',' + port +  ',' + protocol + '\n'     #如果代理可用 则 把此代理  添加到proxyList 列表
                    #print(ipPort.replace('\n', ''))
                    proxyList.append(ipPort)

        file.writelines(proxyList)                                 #把列表写入文件 file 缓冲区
        file.flush()                                            # 保存缓冲区到文件中

    except requests.exceptions.ConnectionError:
        print('ConnectionError -- please wait 3 seconds')
        time.sleep(3)
    except requests.exceptions.ChunkedEncodingError:
        print('ChunkedEncodingError -- please wait 3 seconds')
        time.sleep(3)
    except:
        print('Unfortunitely -- An Unknow Error Happened, Please wait 3 seconds')
        time.sleep(3)

    #finally:
    #        file.close()                                                #关闭文件句柄



