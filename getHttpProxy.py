# -*- coding:UTF-8 -*-


import requests
from bs4 import BeautifulSoup
import  createNewDir

verifyUrl = 'https://ditu.amap.com/detail/get/detail'
url = 'http://www.xicidaili.com/nt/'
headers = {'Upgrade-Insecure-Requests': '1',
           'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
           'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
           'Accept-Encoding': 'gzip, deflate, sdch, br',
           'Accept-Language': 'zh-CN,zh;q=0.8',
           }


def proxyVerify(ip, port, protocol='https'):
    # 验证代理是否有效
    verifyUrl = 'https://ditu.amap.com/detail/get/detail'
    if protocol == 'http':
        proxies = {"http": "http://" + ip + ":" + port}
    else:
        proxies = {"https": "https://" + ip + ":" + port}

    try:
        s = requests.session()
        s.proxies = proxies  # 设置http代理
        html = s.get(verifyUrl, timeout=10, headers=headers, proxies=s.proxies)
        if 'status' in html.text:
            return True
        else:
            return False
    except requests.exceptions:
        print(str(requests.exceptions))
        return False


i = 1
filePath = createNewDir.createNewDir()
file = open(filePath + 'ip.txt', 'a+', encoding='utf-8')

try:
    for i in range(1,31) :
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
                    ipPort = ip + ':' + port + '\n'     #如果代理可用 则 把此代理  添加到proxyList 列表
                    print(ipPort.replace('\n', ''))
                    proxyList.append(ipPort)
        file.writelines(proxyList)                                 #把列表写入文件 file 缓冲区
        file.flush()                                            # 保存缓冲区到文件中

finally:
        file.close()                                                #关闭文件句柄


