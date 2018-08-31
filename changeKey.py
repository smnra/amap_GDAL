# -*- coding:UTF-8 -*-
import json, random


# 获取从 key  列表中 依次更换key
class Keys():
    amap_web_keys = ['3a00e107b4ff451b9306fe3d0405d386',
                     '771b45888c08fcd20c0cf04ed882483a',
                     '9700dfeb2bbaf277dd856f1cd84e7975',
                     'e12b356d1573935e75f064c571e6e5a2',
                     '2a3bebd5eedaabc4cfa5c04eb6989365',
                     "053a406aad6f5afd49afd82a64a4e034",
                     "932bb1b3414d6db917a3155b726e7d07",
                     "93ebbbb772a24c6625def52e779dc38b",
                     "a11acd70df7d78ed4f75a1539821358c",
                     "8325164e247e15eea68b59e89200988b",
                     "be64fe8a1752d3437dbbb715f359a141",
                     "7de8697669288fc848e12a08f58d995e",
                     "778e8bd7e977163d8b3ded18de20099c",
                     "608d75903d29ad471362f8c58c550daf",
                     "f7adb0b1d45b29b5f05b4f557f9541d8",
                     "dd21bdd2263294d9e11b4a9f9d5d6c71",
                     "7ec25a9c6716bb26f0d25e9fdfa012b8",
                     "389880a06e3f893ea46036f030c94700",
                     "c84af8341b1cc45c801d6765cda96087",
                     "6ca7b720f2ab2a48f749c1e19c3d1c47",
                     "cb649a25c1f81c1451adbeca73623251",
                     "550a3bf0cb6d96c3b43d330fb7d86950",
                     "c84af8341b1cc45c801d6765cda96087",
                     "7de8697669288fc848e12a08f58d995e",
                     "dc44a8ec8db3f9ac82344f9aa536e678",
                     "0b00174f6f8ab4ca8d350ac0da105bb9",
                     "959e9ee93388f4bd5a144aabcc884a2e"
                     ]
    keyCount = len(amap_web_keys)  # 可用的key的数量

    def __init__(self):
        self.keyCurrentIndex = random.randint(0,4)  # 初始化当前使用的key的 index
        self.keyCurrent = self.amap_web_keys[self.keyCurrentIndex]  # 初始化当前key
        # print('Current used key is :',self.keyCurrent, ', Index is :', self.keyCurrentIndex)


    def getKey(self):
        self.keyCurrentIndex = self.keyCurrentIndex - 1  # 把当前正在使用的key的index 减去1

        if self.keyCurrentIndex < 0:  # 如果 当前正在使用的key的index 小于0
            self.keyCurrentIndex = self.keyCount - 1  # 则重新初始化当前正在使用的key的index(复位keyCurrentIndex)

        self.keyCurrent = self.amap_web_keys[self.keyCurrentIndex]  # 获取key 为 列表中的 当前正在使用的Key的上一个 Key
        # print('Current used key is :',self.keyCurrent, ', Index is :', self.keyCurrentIndex)
        return self.keyCurrent

if __name__ == '__main__' :
    amapKey = Keys()                #初始化Keys 类对象
    amap_web_key = amapKey.keyCurrent       # 初始值
    amapKey.getKey()                #更换Key
