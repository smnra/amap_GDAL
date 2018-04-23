# -*- coding:UTF-8 -*-
#更换一个http 代理

import requests
import random


class ChangeProxy():
    def __init__(self,fileName):
        proxyFile = open(fileName,'r')               #读取打开文件句柄
        self.proxyList = proxyFile.readlines()       #读取文件为一个list 每一行一个元素   如: '192.168.2.34,8080,https'
        self.proxyCount = len(self.proxyList)             #计算共有多少行    多少个http proxy
        self.keyCurrentProxyIndex = random.randint(0, self.proxyCount - 1)       #随机选取一个 proxyIP 的索引
        self.cruuentProxyIP = self.proxyList[self.keyCurrentProxyIndex]     #当前正在使用的 proxyIP

    def changeProxyIP(self):
        self.keyCurrentProxyIndex = self.keyCurrentProxyIndex - 1  # 把当前正在使用的  proxyIP 的index 减去1

        if self.keyCurrentProxyIndex < 0:  # 如果 当前正在使用的 proxyIP 的index 小于0
            self.keyCurrentProxyIndex = self.proxyCount - 1  # 则重新初始化当前正在使用的 proxyIP 的index(复位 keyCurrentProxyIndex)

        self.cruuentProxyIP = self.proxyList[self.keyCurrentProxyIndex]  # 获取 keyCurrentProxyIndex 为 列表中的 当前正在使用index对应的 proxyIP
        print('Current used http proxy ip is :',self.cruuentProxyIP, ', Index is :', self.keyCurrentProxyIndex)
        return {'ip' :  self.cruuentProxyIP.split(',')[0], 'port' :  self.cruuentProxyIP.split(',')[1], 'protocol' :  self.cruuentProxyIP.split(',')[2]}

if __name__ == '__main__' :
    proxyFileName = r'./proxy.txt'
    proxyPool = ChangeProxy(proxyFileName)                #初始化Keys 类对象
    initProxyIP = proxyPool.cruuentProxyIP       # 初始值
    proxyPool.changeProxyIP()                #更换Key
