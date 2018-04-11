# -*- coding:UTF-8 -*-
import json, random


# 获取从 key  列表中 依次更换key
class Keys():
    amap_web_keys = ['3a00e107b4ff451b9306fe3d0405d386',
                     '771b45888c08fcd20c0cf04ed882483a',
                     '9700dfeb2bbaf277dd856f1cd84e7975',
                     'e12b356d1573935e75f064c571e6e5a2',
                     '2a3bebd5eedaabc4cfa5c04eb6989365']
    keyCount = len(amap_web_keys)  # 可用的key的数量

    def __init__(self):
        self.keyCurrentIndex = random.randint(0,4)  # 初始化当前使用的key的 index
        self.keyCurrent = self.amap_web_keys[self.keyCurrentIndex]  # 初始化当前key
        print('Current used key is :',self.keyCurrent, ', Index is :', self.keyCurrentIndex)


    def getKey(self):
        self.keyCurrentIndex = self.keyCurrentIndex - 1  # 把当前正在使用的key的index 减去1

        if self.keyCurrentIndex < 0:  # 如果 当前正在使用的key的index 小于0
            self.keyCurrentIndex = self.keyCount - 1  # 则重新初始化当前正在使用的key的index(复位keyCurrentIndex)

        self.keyCurrent = self.amap_web_keys[self.keyCurrentIndex]  # 获取key 为 列表中的 当前正在使用的Key的上一个 Key
        print('Current used key is :',self.keyCurrent, ', Index is :', self.keyCurrentIndex)
        return self.keyCurrent

if __name__ == '__main__' :
    amapKey = Keys()                #初始化Keys 类对象
    amap_web_key = amapKey.keyCurrent       # 初始值
    amapKey.getKey()                #更换Key
