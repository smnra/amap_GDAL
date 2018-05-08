#!usr/bin/env python  
#-*- coding:utf-8 _*-  

""" 
@author:Administrator 
@file: getProxyFromProxyPools.py 
@time: 2018/05/03
描述: 从 ProxyPools 中 使用 api 获取, 修改 删除 一个 http proxy

"""



import requests


class ChangeProxy():
    def __init__(self):
        self.cruuentProxyIP = self.getProxy()     #从proxyPools 获取一个http proxy
        print(self.cruuentProxyIP)

    def getProxy(self):
        proxy =  requests.get("http://123.207.35.36:5010/get/").content.decode('utf-8').split(':')     #http://123.207.35.36:5010/get
        return  proxy

    def changeProxyIP(self):
        # 返回一个设置代理的 requests 对象
        self.cruuentProxyIP = self.getProxy()  # 获取 keyCurrentProxyIndex 为 列表中的 当前正在使用index对应的 proxyIP

        if len(self.cruuentProxyIP) > 0 :
            self.proxies = {"http" : "http://" + self.cruuentProxyIP[0] + ":" + self.cruuentProxyIP[1],
                            "https": "https://" + self.cruuentProxyIP[0] + ":" + self.cruuentProxyIP[1]}   #设置类的 .session.proxies 属性
            proxyRequest = requests.session()  # 创建 session
            proxyRequest.proxies = self.proxies  # 设置http代理                             #设置 session proxies 代理
            print(u'当前代理:' + self.cruuentProxyIP[0] + ":" + self.cruuentProxyIP[1])
            return proxyRequest                                                             #返回一个设置代理的 Requests 对象
        else :
            self.changeProxyIP()                                                            #迭代本方法

    def noProxyIP(self):
        # 返回一个没有设置代理的 requests 对象
        proxyRequest = requests.session()  # 创建 session
        print(u'当前代理: 无')
        return proxyRequest                                                             #返回一个设置代理的 Requests 对象



if __name__ == '__main__' :

    proxyRequest = ChangeProxy()                #初始化ChangeProxy 类对象
    s = proxyRequest.changeProxyIP()               #返回一个设置代理的 requests 实例对象对象

    html = s.get('http://ip.chinaz.com/getip.aspx', timeout=10)

    print(html.text)











