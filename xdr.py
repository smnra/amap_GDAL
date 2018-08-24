#!usr/bin/env python
#-*- coding:utf-8 _*-

"""
@author:Administrator
@file: dianping_API.py
@time: 2018/08/{DAY}
描述: 大众点评 API
返回json格式的结果
"""


import requests,re,time
from bs4  import BeautifulSoup
#导入webdriver
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import  expected_conditions as EC

#要想调用键盘按键操作需要引入keys包
from selenium.webdriver.common.keys import Keys



class GetXDR():
    def __init__(self):

        self.headers = {"Accept": "*/*",
                        "Accept-Encoding": "gzip, deflate",
                        "Accept-Language": "zh-CN,zh;q=0.9",
                        "Cache-Control": "no-cache",
                        "Connection": "keep-alive",
                        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
                        "Cookie": "",
                        "DNT": "1",
                        "Host": "10.217.4.22:9088",
                        "Origin": "http://10.217.4.22:9088",
                        "Pragma": "no-cache",
                        "Referer": "http://10.217.4.22:9088/web/page/login/login.jsp",
                        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.162 Safari/537.36 Avast/65.0.411.162",
                        "X-Requested-With": "XMLHttpRequest"
                        }

        self.postData ={'userName': 'wangwp',
                        'userPwd': '%60%C2%BC%C3%93%C2%AE%C2%80vmoq',
                        'userVersion': '',
                        'validcheckcode': ''
                         }

        self.postDataPrep = {"queryType": "1",
                            "queryParams": '<?xml version="1.0" encoding="GB18030" standalone="yes"?><USERPARAMS><dataSource id="st_cl" moduleId="4565"/><extend><item field="TIME" value="MINUTE15"/><item field="ENDTIME" value="MINUTE15"/></extend><time id="timevalue" starttime="2018-07-28 00:00:00" endtime="2018-08-02 00:00:00" discrete="5"/><conditions><and><condition field="cellid" value="198186517" operator="=" type="string" caption="小区" display="198186517"/><condition field="DIMENSION" value="timevalue|cellid" operator="in" type="string" caption="维度" display="时间, 小区"/></and></conditions><measures><measure field="kpi_avgWebDLRate"/><measure field="kpi_avgWebOpenDelay"/></measures><dimensions><dimension field="timevalue" display="时间"/><dimension field="cellid" display=" 小区"/></dimensions></USERPARAMS>',
                            "moduleId": "1063",
                            "pushThreadKey": "key_4e1afbfa-6d0a-4f99-97ad-60519a1077f8",
                            "queryParamsLimit": '<?xml version="1.0" encoding="GB18030" standalone="yes"?><USERPARAMS><dataSource id="st_cl" moduleId="4565"/><extend><item field="TIME" value="MINUTE15"/><item field="ENDTIME" value="MINUTE15"/></extend><time id="timevalue" starttime="2018-07-28 00:00:00" endtime="2018-08-02 00:00:00" discrete="5"/><conditions><and><condition field="cellid" value="198186517" operator="=" type="string" caption="小区" display="198186517"/><condition field="DIMENSION" value="timevalue|cellid" operator="in" type="string" caption="维度" display="时间, 小区"/></and></conditions><measures><measure field="kpi_avgWebDLRate"/><measure field="kpi_avgWebOpenDelay"/></measures><dimensions><dimension field="timevalue" display="时间"/><dimension field="cellid" display=" 小区"/></dimensions></USERPARAMS>',
                            "queryLogMsg": "	开始时间:2018-07-28 00:00:00	结束时间:2018-08-02 00:00:00	小区:198186517	维度:时间, 小区	指标选择:大页面下载速率(kbps),小页面显示时长(ms)",
                            "phone": "",
                            "queryPermissions": "1",
                            "dataSourceType": "1",
                            "queryFrom": "",
                            }

        self.postAddQueryLog = {"content": "	开始时间:2018-07-28 00:00:00	结束时间:2018-08-02 00:00:00	小区:198186517	维度:时间, 小区	指标选择:大页面下载速率(kbps),小页面显示时长(ms)",
                                "moduleId": "1063",
                                "queryId": "1282C86ADD3E493AE1CC4D0D78691CED.jvm2_1063_1534994551532_5520cc49_6b38_467d_ab6e_c7fbce5486f2"
                                }

        self.postQuery_sl = {"queryid": "1282C86ADD3E493AE1CC4D0D78691CED.jvm2_1063_1534994551532_5520cc49_6b38_467d_ab6e_c7fbce5486f2",
                            "currentPage": "1",
                            "iframeid": "div_md_1063_1535001953",
                            "pageSize": "500",
                            "curPageTrans": "true"
                            }

        self.postExportAll = {"fileName": "数据业务质量分析",
                                "exportType": "2",
                                "textSplitSymbol": ",",
                                "wordSplitSymbol": ",",
                                "csvSplitSymbol": ",",
                                "csvQuotationSymbol": "",
                                "excelMinCellWidth": "80",
                                "excelMinRowHeight": "20",
                                "moreFile": "0",
                                "maxFileRow": "1000000",
                                "fieldToString": "",
                                "transout": "on",
                                "exportMethod": "exportPage",
                                "columnTitles": "时间,小区,小区ID,大页面下载速率(kbps),小页面显示时长(ms)",
                                "columnNames": "TIMEVALUE,CELLID_TRANS,CELLID,KPI_AVGWEBDLRATE,KPI_AVGWEBOPENDELAY",
                                "columnWidths": "150,85,85,142,131",
                                "moduleName": "数据业务质量分析",
                                "moduleId": "1063",
                                "queryParams": '<?xml version="1.0" encoding="GB18030" standalone="yes"?><USERPARAMS><dataSource id="st_cl" moduleId="4565"/><extend><item field="TIME" value="MINUTE15"/><item field="ENDTIME" value="MINUTE15"/></extend><time id="timevalue" starttime="2018-07-28 00:00:00" endtime="2018-08-02 00:00:00" discrete="5"/><conditions><and><condition field="cellid" value="198186517" operator="=" type="string" caption="小区" display="198186517"/><condition field="DIMENSION" value="timevalue|cellid" operator="in" type="string" caption="维度" display="时间, 小区"/></and></conditions><measures><measure field="kpi_avgWebDLRate"/><measure field="kpi_avgWebOpenDelay"/></measures><dimensions><dimension field="timevalue" display="时间"/><dimension field="cellid" display=" 小区"/></dimensions></USERPARAMS>',
                                "queryType": "1",
                                "queryFrom": "",
                                "queryid": "1282C86ADD3E493AE1CC4D0D78691CED.jvm2_1063_1534994551532_5520cc49_6b38_467d_ab6e_c7fbce5486f2",
                                "frameId": "div_md_1063_1535001953",
                                "pushThreadKey": "key_4e1afbfa-6d0a-4f99-97ad-60519a1077f8",
                                "dataSourceType": "1",
                                "exportLogMsg": "	开始时间:2018-07-28 00:00:00	结束时间:2018-08-02 00:00:00	小区:198186517	维度:时间, 小区	指标选择:大页面下载速率(kbps),小页面显示时长(ms)",
                                "page": "1"
                                }
        self.pushThreadKey = ""
        self.frameId = ''
        self.urlLogin = 'http://10.217.4.22:9088/loginController.do?method=ajaxCheckLogin'
        self.url = 'http://10.217.4.22:9088/web/page/login/login.jsp'
        self.url2 = 'http://10.217.4.22:9088/web/index.jsp'
        self.urlLongined = 'http://10.217.4.22:9088/web/index.jsp?datasourceType=1#1063'
        self.urlPrep = 'http://10.217.4.22:9088/analysisController.do?method=prep'
        self.urlAddQueryLog =  'http://10.217.4.22:9088/analysisConfigController.do?method=addQueryLog'
        self.urlQuery_sl = 'http://10.217.4.22:9088/analysisController.do?method=query_sl'
        self.urlExportAll = 'http://10.217.4.22:9088/analysisController.do?method=exportAll'
        self.enforceLogin = 'http://10.217.4.22:9088/loginController.do?method=enforceLogin&_dc=0.5855663784707259'
        self.urlLogout = 'http://10.217.4.22:9088/loginController.do?method=exitSystem'


        self.enforceLoginParma = {'method': 'enforceLogin','_dc': '0.5855663784707259'}
        self.enforceLoginHeaders= {"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
                                    "Accept-Encoding": "gzip, deflate",
                                    "Accept-Language": "zh-CN,zh;q=0.9",
                                    "Cache-Control": "no-cache",
                                    "Connection": "keep-alive",
                                    "Cookie": "theme=deepblue; JSESSIONID=5AE89FC7308F7FBC2FF981D4FB84AA64.jvm2",
                                    "DNT": "1",
                                    "Host": "10.217.4.22:9088",
                                    "Pragma": "no-cache",
                                    "Referer": "http://10.217.4.22:9088/web/page/login/login.jsp",
                                    "Upgrade-Insecure-Requests": "1",
                                    "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.162 Safari/537.36 Avast/65.0.411.162"
                                    }

    def seleniumChrome(self):
        # 模拟创建一个浏览器对象，然后可以通过对象去操作浏览器
        driverPath = r'./Chrome/Application/chromedriver.exe'

        # 浏览器驱动
        browserDriver = webdriver.Chrome(executable_path=driverPath)

        # 打开网页 url
        browserDriver.get(self.url)

        # 暂停2秒，已达到完全模拟浏览器的效果
        time.sleep(2)

        # 查找百度页面的input输入框

        print(browserDriver.title)

        # id="kw"是百度搜索输入框，输入字符串"长城"
        browserDriver.find_element_by_id('userName').send_keys('wangwp')       # 帐号
        browserDriver.find_element_by_id('userPwd').send_keys('Wen@@6789')  # 密码
        browserDriver.find_element_by_id('userPwd').send_keys(Keys.RETURN)   # 登陆

        # 添加等待时间
        time.sleep(2)

        try:
            # 打印对话框文本
            print(browserDriver.switch_to.alert.text)
            # 点击对话框确定按钮
            browserDriver.switch_to.alert.accept()
        except Exception as e:
            print(e)



        try:
            # 等待到 首页载入完成  实时刷新 10 分钟  出现
            element = WebDriverWait(browserDriver, 10).until(EC.presence_of_element_located((By.ID, "is10")))
        except Exception as e:
            print(e)
        finally:
            #打印网页渲染后的源代码
            # print(browserDriver.page_source)
            # 正则表达式匹配 pushThreadKey 并保存
            self.pushThreadKey = re.findall(r"var pushThreadKey = \'(.+?)\'\;", browserDriver.page_source)[0]
            self.postDataPrep['pushThreadKey'] = self.pushThreadKey
            self.postExportAll['pushThreadKey'] = self.pushThreadKey
            print("pushThreadKey:",self.pushThreadKey)

        browserDriver.find_element_by_xpath("//*[contains(text(), '面向运维')]").click()                # 点击面向运维
        # browserDriver.find_element_by_xpath("//div[@class='floatNav']/ul/li/dl/dd/a[2]").text          # 打印 文本
        browserDriver.find_element_by_xpath("//div[@class='floatNav']/ul/li/dl/dd/a[2]").click()        # 点击 数据业务质量分析 连接
        time.sleep(6)
        ifreamTag = browserDriver.find_element_by_xpath("//*[contains(@id,'div_md_1063')]")  # 寻找 数据业务质量分析的 ifream 标签
        self.iframeId = ifreamTag.get_attribute("id")                                           # 保存 iframeId
        self.postQuery_sl['iframeid'] = self.iframeId
        self.postExportAll['frameid'] = self.iframeId
        print("iframeId:", self.iframeId)

        # 切换到 ifream
        browserDriver.switch_to.frame(self.iframeId)

        try:
            element = WebDriverWait(browserDriver, 10).until(EC.presence_of_element_located((By.ID, "ID_button_query")))    # 等待到 查询 按钮出现
        except Exception as e:
            print(e)
        finally:
            print(element._parent.title)

        # 选择'  小区 纬度
        browserDriver.find_element_by_xpath("//span[text()='位置']/../div[1]").click()
        time.sleep(1)
        browserDriver.find_element_by_xpath("//span[text()='小区']").click()

        # 选择 "大页面下载速率(kbps)"  指标
        browserDriver.find_element_by_xpath("//*[text()='HTTP']/../div[1]").click()
        time.sleep(1)
        browserDriver.find_element_by_xpath("//*[text()='大页面下载速率(kbps)']/..").click()
        # 选择 "小页面显示时长(ms)"  指标
        browserDriver.find_element_by_xpath("//*[text()='小页面显示时长(ms)']/..").click()
        # 选择 "页面下载时延(内容>=50KB)(ms)"  指标
        browserDriver.find_element_by_xpath("//*[text()='页面下载时延(内容>=50KB)(ms)']/..").click()
        # 选择 "页面下载流量(内容>=50KB)(Byte)"  指标
        browserDriver.find_element_by_xpath("//*[text()='页面下载流量(内容>=50KB)(Byte)']/..").click()
        # 选择 "页面响应平均时长(ms)"  指标
        browserDriver.find_element_by_xpath("//*[text()='页面响应平均时长(ms)']/..").click()
        # 选择 "页面响应总时延(ms)"  指标
        browserDriver.find_element_by_xpath("//*[text()='页面响应总时延(ms)']/..").click()
        # 点击查询按钮
        browserDriver.find_element_by_xpath("//*[@id='ID_button_query']").click()
        time.sleep(1)


        '''
        # 设置时间    data-value="timevalue"   name="timevalue"
        browserDriver.find_element_by_xpath("//*[@data-value='timevalue']").click()
        time.sleep(0.5)
        timeInputId = browserDriver.find_element_by_xpath("//input[@name='timevalue']").get_attribute("id")
        print(timeInputId)
        browserDriver.execute_script('document.getElementById("'+ timeInputId + '").value="2018-07-28 23:00:00 至 2018-08-02 00:00:00"')
        '''




        # 点击查询
        # browserDriver.find_element_by_xpath("//*[@id='ID_button_query']").click()

        browserDriver.get(self.urlPrep)




        #获取当前页面Cookie
        print(browserDriver.get_cookies())

        #生成新的页面快照
        browserDriver.save_screenshot('itcast.png')

        browserDriver.quit()




    def exceptAll(self,page):
        try:
            session = requests.Session()
            session.headers = self.headers
            result = session.get(self.url,headers=self.headers)
            result = session.post(self.urlLogin, data=self.postData,headers=self.headers)                # 登录
            if result.status_code == 200:
                if "登录成功" in result.text:
                    self.headers['Cookie'] = "theme=deepblue; JSESSIONID=" + session.cookies._cookies['10.217.4.22']['/']['JSESSIONID'].value
                    session.headers = self.headers
                elif '该用户已经登录' in result.text:
                        result = session.get(url=self.enforceLogin, params=self.enforceLoginParma, headers=self.enforceLoginHeaders)

                result = session.get(self.urlLongined,headers=self.headers)
                if "var userName = '王文萍';" in result.text:
                    soup = BeautifulSoup(result.text, 'html.parser')  # 将返回的网页转化为bs4 对象
                    scriptTag = soup.find('script', attrs={"src": False})
                    userName = re.findall(r"var userName = \'(.+?)\'\;",scriptTag.text)[0]
                    self.pushThreadKey = re.findall(r"var pushThreadKey = \'(.+?)\'\;", scriptTag.text)[0]
                    self.postExportAll['pushThreadKey'] = self.pushThreadKey
                    print(userName,"登陆成功.\npushThreadKey:",self.pushThreadKey)

                    result = session.get(self.url2,params = {'datasourceType':'1'})
                    result = session.post(self.urlPrep, data=self.postDataPrep, headers = self.headers)
        except  Exception as e:
            print(e)



        result = session.post(self.urlPrep, data=self.postDataPrep)
        if result.status_code==200 and "通过" in result.text:
            resultJson = result.json()
            self.queryId = resultJson.get('msg')                # 获取 queryid
            self.postQuery_sl['queryid'] = self.queryId
            self.postAddQueryLog['queryid'] = self.queryId
            self.postExportAll['queryid'] = self.queryId
            self.postQuery_sl['iframeid'] = self.frameId
            self.postExportAll['frameId'] = self.frameId
        result = session.post(self.urlAddQueryLog, data=self.postAddQueryLog)
        if result.status_code==200:
            print(self.postAddQueryLog)
        result = session.post(self.urlQuery_sl, data=self.postQuery_sl)
        if result.status_code==200:
            print(result.text)




if __name__=="__main__":
    xdr = GetXDR()
    xdr.seleniumChrome()
    xdr.exceptAll(1)
    result = xdr.session.get(url=xdr.urlLogout)  # 退出登陆

