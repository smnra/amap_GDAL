#!usr/bin/env python  
#-*- coding:utf-8 _*-  

""" 
@author:Administrator 
@file: fenci.py 
@time: 2018/10/{DAY} 
描述: 

"""

import thulac

thu1 = thulac.thulac(seg_only=True)
def fenci(wd):
    text = thu1.cut(wd, text=True)
    return text

if __name__=='__main__':
    print(fenci('汉滨区新建中等职业技术学校'))