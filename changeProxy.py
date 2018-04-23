#!usr/bin/env python
#-*- coding:utf-8 _*-

"""
@author:Administrator
@file: test.py
@time: 2018/04/{DAY}
描述: 更换一个http 代理

"""

import requests
import random


class ChangeProxy():
    def __init__(self,fileName):
        proxyFile = open(fileName,'r')               #读取打开文件句柄
        self.proxyList = proxyFile.readlines()       #读取文件为一个list 每一行一个元素   如: '192.168.2.34,8080,https\n'
        self.proxyList = [x.replace('\n', '') for x in self.proxyList]      #使用列表推导式删除每个元素最后面的 换行字符 '\n'

        self.proxyCount = len(self.proxyList)             #计算共有多少行    多少个http proxy
        self.keyCurrentProxyIndex = random.randint(0, self.proxyCount - 1)       #随机选取一个 proxyIP 的索引
        self.cruuentProxyIP = self.proxyList[self.keyCurrentProxyIndex]     #当前正在使用的 proxyIP
        print(self.cruuentProxyIP)
        proxyFile.close()

    def changeProxyIP(self):
        # 返回一个设置代理的 requests 对象
        self.keyCurrentProxyIndex = self.keyCurrentProxyIndex - 1  # 把当前正在使用的  proxyIP 的index 减去1

        if self.keyCurrentProxyIndex < 0:  # 如果 当前正在使用的 proxyIP 的index 小于0
            self.keyCurrentProxyIndex = self.proxyCount - 1  # 则重新初始化当前正在使用的 proxyIP 的index(复位 keyCurrentProxyIndex)
        self.cruuentProxyIP = self.proxyList[self.keyCurrentProxyIndex].split(',')  # 获取 keyCurrentProxyIndex 为 列表中的 当前正在使用index对应的 proxyIP

        if self.cruuentProxyIP[2].lower() in  ['http', 'https']:
            self.proxies = {self.cruuentProxyIP[2].lower() : self.cruuentProxyIP[2].lower()+ "://" + self.cruuentProxyIP[0] + ":" + self.cruuentProxyIP[1]}   #设置类的 .session.proxies 属性
            proxyRequest = requests.session()  # 创建 session
            proxyRequest.proxies = self.proxies  # 设置http代理                             #设置 session proxies 代理
            return proxyRequest                                                             #返回一个设置代理的 Requests 对象
        else :
            self.changeProxyIP()                                                            #迭代本方法


if __name__ == '__main__' :
    proxyFileName = r'./proxy.txt'
    proxyRequest = ChangeProxy(proxyFileName)                #初始化ChangeProxy 类对象
    s = proxyRequest.changeProxyIP()               #返回一个设置代理的 requests 实例对象对象

    html = s.get('http://ip.chinaz.com/getip.aspx', timeout=10)

    print(html.text)