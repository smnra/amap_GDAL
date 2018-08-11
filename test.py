'''
# #用于获取用户的url
# from get_url import store_information,user_index,user_index_distinct
#
# user_index.remove()
# for i in store_information.find({
 
},{
'member_comment' :1,'_id':0
}):
#     for information in i['member_comment']:
#         print(information['name'])
#         user_index.insert_one({
'user_url':information['name'][0],'user_name':information['name'][1]
})
#
# print(user_index.count())
#
# print(len(user_index.distinct('user_url')))
# print(user_index_distinct.count())
# for i in user_index.distinct('user_url'):
#     user_index_distinct.insert_one({
'user_url_distinct':i
})
'''
from get_url import header,user_index_distinct,user_information,shop_information,user_information_url,shop_index_distinct,shop_information_url,user_review_db
import requests
from bs4 import BeautifulSoup
import re
import time
import json
import random
from multiprocessing.dummy import Pool
 
# for i in user_index_distinct.find():
#     print(i)

class UserCrawler(object):
    def __init__(self):
        pass
        # self.user_name = None
        # self.user_contribute = None
        # self.user_birth = None
        # self.user_city = None
        # self.user_gender = None
        # self.user_label = None
        # self.user_follow = None
        # self.user_fans = None
        # self.score_list = []
 
    def get_member_information(self,url):
        #print(url)
        user_ID = url.split('/')[4]
        try:
            #print(type(user_ID))
            web_page = requests.get(url,proxies=proxies,timeout=5)
            time.sleep(random.random() * 2)
            soup = BeautifulSoup(web_page.text,'lxml')
            #print(soup)
            if soup.title.text == '提示_大众点评网':
                print('被屏蔽')
                time.sleep(300)
            user_names = soup.select('.tit .name')
            if len(user_names) > 0:
                user_name = user_names[0].text
            else:
                user_name = 'None'
 
            user_contributes = soup.find(id="J_col_exp")
            if len(user_contributes) > 0:
                user_contribute = user_contributes.text
            else:
                user_contribute = 0
 
            user_births = soup.select('.user-message')
            if len(user_births) > 0:
                user_birth = re.findall(r'\d{4
}-\d{
1,2
}-\d{
1,2
}',str(user_births),re.S)
                if len(user_birth) > 0:
                    user_birth = user_birth[0]
                else:
                    user_birth = 'None'
            else:
                user_birth = 'None'
 
            user_citys = soup.select('.user-groun')
            if len(user_citys) > 0:
                user_genders = re.findall(r'<i class="(.*?)"></i>',str(user_citys),re.S)
 
                if len(user_citys[0].text) > 0:
                    user_city = user_citys[0].text
                else:
                    user_city = 'None'
                if len(user_genders) > 0:
                    user_gender = user_genders[0]
                else:
                    user_gender = 'None'
 
            else:
                user_city = 'None'
                user_gender = 'None'
            #print(user_citys)
 
            user_labels = soup.find(id="J_usertag")
            user_label = re.findall(r'<em class="user-tag" id="-1">(.*?)</em>',str(user_labels),re.S)
            if len(user_label) == 0:
                user_label = None
            #print(user_ID)
            user_follow = self.member_follows(user_ID)
            user_fans = self.member_fans(user_ID)
            score_list = self.member_scored(user_ID)
            #用户关注，用户粉丝
            '''
            member_follows(user_ID)
            member_fans(user_ID)
            member_reviews(user_ID)
            member_checkin(user_ID)
            '''
            #print(self.user_name,self.user_contribute,self.user_birth,self.user_city,self.user_gender,self.user_label,self.user_follow,self.user_fans,self.score_list)
            data = {
'user_name':user_name,'user_contribute':user_contribute,'user_birth':user_birth,\
                    'user_city':user_city,'user_gender':user_gender,'user_label':user_label,'user_ID':user_ID,\
                    'user_follow':user_follow,'user_fans':user_fans,'score_list':score_list
}
            user_information.insert_one(data)
            print(data)
 
        except:
            print('rubbish')
            pass
 
 
    #人数和人物
    def member_follows(self,user_ID):
        #该用户关注的人
        member_follow_list = []
        num = self.member_follows_number(user_ID)
        if num == 0:
            temp_url_list = ['http://www.dianping.com/member/{
 
}/follows'.format(user_ID)]
        else:
            temp_url_list = ['http://www.dianping.com/member/{
 
}/follows?pg={
 
}'.format(user_ID,i) for i in range(1,num+1)]
        try:
            for temp_url in temp_url_list:
                web_page = requests.get(temp_url,proxies=proxies,timeout=5)
                time.sleep(random.random() * 2)
                soup = BeautifulSoup(web_page.text,'lxml')
                if soup.title.text == '提示_大众点评网':
                    print('被屏蔽')
                    time.sleep(300)
 
                member_informations = soup.select('.modebox  .pic-txt .tit')
                #print(member_informations)
                if len(member_informations) > 0:
                    for member_information in member_informations:
                        member_name = member_information.text.strip()
                        member_ID = re.findall(r'<a class="J_card" href="/member/(.*?)"',str(member_information),re.S)
                        if len(member_ID) > 0:
                            member_ID =  member_ID[0]
                            member_url = 'http://www.dianping.com/member/{
 
}'.format(member_ID)
                        else:
                            member_url = None
                            member_ID = None
 
                        member_follow_dic = {
'member_name': member_name, 'member_url': member_url,'member_ID':member_ID
}
                        member_follow_list.append(member_follow_dic)
                else:
                    #print(len(member_follow_list))
                    return member_follow_list
            #print(len(member_follow_list))
            return member_follow_list
        except:
            return None
 
 
 
    def member_follows_number(self,user_ID):
        temp_url = 'http://www.dianping.com/member/{
 
}/follows'.format(user_ID)
        try:
            web_page = requests.get(temp_url,proxies=proxies,timeout=5)
            time.sleep(random.random() * 2)
            soup = BeautifulSoup(web_page.text, 'lxml')
            if soup.title.text == '提示_大众点评网':
                print('被屏蔽')
                time.sleep(300)
            page_nums = soup.select('.pages-num')
            # print(page_nums)
            if len(page_nums) > 0:
                page_num = page_nums[0]
                page_num = page_num.text
                page_num = re.findall(r'\d+', page_num, re.S)
                # print(page_num)
                max_num = self.get_max(page_num)
                #print(max_num)
                return max_num
            else:
                return 0
        except:
            return 0
 
    def get_max(self,number_list):
        for i in range(len(number_list)):
            number_list[i] = int(number_list[i])
        max = number_list[0]
        for i in range(len(number_list)):
            if max < number_list[i]:
                max = number_list[i]
        return max
 
    def member_fans(self,user_ID):
        # 关注该用户的人
        fans_follow_list = []
        num = self.member_fans_number(user_ID)
        #print(num)
        if num == 0:
            temp_url_list = ['http://www.dianping.com/member/{
 
}/fans'.format(user_ID)]
        else:
            temp_url_list = ['http://www.dianping.com/member/{
 
}/fans?pg={
 
}'.format(user_ID, i) for i in range(1, num + 1)]
        try:
            for temp_url in temp_url_list:
                web_page = requests.get(temp_url,proxies=proxies,timeout=5)
                time.sleep(random.random() * 2)
                soup = BeautifulSoup(web_page.text, 'lxml')
                if soup.title.text == '提示_大众点评网':
                    print('被屏蔽')
                    time.sleep(300)
                member_informations = soup.select('.modebox  .pic-txt .tit')
                # print(member_informations)
                if len(member_informations) > 0:
                    for fans_information in member_informations:
                        fans_name = fans_information.text.strip()
                        fans_ID = re.findall(r'<a class="J_card" href="/member/(.*?)"', str(fans_information), re.S)
                        if len(fans_ID) > 0:
                            fans_ID = fans_ID[0]
                            fans_url = 'http://www.dianping.com/fans/{
 
}'.format(fans_ID)
                        else:
                            fans_url = None
                            fans_ID = None
 
                        fans_follow_dic = {
'fans_name': fans_name, 'fans_url': fans_url, 'fans_ID': fans_ID
}
                        fans_follow_list.append(fans_follow_dic)
                else:
                    # print(len(fans_follow_list))
                    return fans_follow_list
            #print(len(fans_follow_list))
            return fans_follow_list
        except:
            return None
 
    def member_fans_number(self,user_ID):
        temp_url = 'http://www.dianping.com/member/{
 
}/fans'.format(user_ID)
        try:
            web_page = requests.get(temp_url,proxies=proxies,timeout=5)
            time.sleep(random.random() * 2)
            soup = BeautifulSoup(web_page.text, 'lxml')
            if soup.title.text == '提示_大众点评网':
                print('被屏蔽')
                time.sleep(300)
            page_nums = soup.select('.pag
...
...
（文件超长，未完全显示，请下载后阅读剩余部分）