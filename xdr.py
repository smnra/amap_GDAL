#!usr/bin/env python
#-*- coding:utf-8 _*-

"""
@author:Administrator
@file: dianping_API.py
@time: 2018/08/{DAY}
描述: 大众点评 API
返回json格式的结果
"""

import requests,re,time,os
from bs4  import BeautifulSoup
#导入webdriver
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver import ActionChains
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
        self.queryTime = "2018-09-27 00:00:00 至 2018-09-28 00:00:00"
        self.cgiList = ["197713675","197712907","197713419","197713163","197714955","197748491","197748235","197747979","197747723","197747467","197747211","197784075","197783819","197783563","197783307","197782795","10008843","10009099","197775627","197776395","197776139","197775883","197777419","197777163","10009355","10009611","197776907","197776651","197775371","197775115","197774859","197774603","197774347","9954827","9956107","9956363","9956619","9955595","9955851","9953803","9953291","9954315","9954059","9955083","9953035","197732107","197731851","197728011","9952779","197727755","9954571","197711627","197711371","197711115","197710859","9953547","9955339","197729035","197729291","197728779","197728523","197728267","197731595","197731339","197730827","197731083","197730315","197730571","197729803","197730059","197729547","197712139","197711883","9997835","9997579","9998091","9996811","9996555","9997067","9997323","9890907","9890897","9890887","9890581","9890315","9889291","9889803","9884427","9890355","9890345","9884683","9890335","9890325","9889035","9889547","9884171","9883915","9888267","9888779","9888011","9888523","9887243","9887755","9886987","9887499","9886219","9886731","9885963","9886475","9890571","9890611","9884939","9885195","9890591","9890601","9890089","9885451","9890867","9890877","9890837","9890827","9890857","9890847","9885707","9890365","9890631","9890621","9890059","9890069","9890079","9890651","9890641","197717004","197716758","197716512","197733899","197733643","197732875","197732619","197733387","197733131","197735947","197735691","197734923","197734667","197735435","197735179","197734411","197734155","10003211","10002443","10002699","10002955","10001931","10002187","10001675","197698827","197699083","197700363","197699851","197700107","197699339","197699595","197700619","10014475","10014219","10013707","10013451","10012939","10013195","10012427","10012683","10016011","10015499","10015755","10013963","10014987","10015243","10014731","10016523","10016267","10012171","197743115","197742859","197742603","197742347","197742091","197741835","197740555","197740811","197741067","197741323","197741579","197744651","197744395","197744139","197743883","197743627","197743371","197744907","9949963","9950219","9949707","9950475","9949451","9948427","9948683","9949195","9948939","9950731","9951243","9950987","9951499","10023179","10020875","10020619","10020363","10020107","10019851","10019595","10019339","10019083","10018827","10018571","10022923","10018315","10018059","10017803","10017547","10022667","10022411","10022155","10021899","10021643","10021387","10021131","197689867","197689355","197690123","197689611","197688587","197688331","197688843","197689099","197687819","197687307","197688075","197687563","197686795","197686539","197687051","197727243","197726987","197726731","197726475","197726219","197727499","9957643","9957131","9958155","9957899","9958411","9958421","9958431","9958441","9958451","9958461","9958471","9958481","9957387","10000395","10000139","9999883","9999627","9999371","9998603","9998859","9999115","9998347","10000907","10000651","9952267","9952011","9951755","9952523","197752843","197752587","197752331","197752341","197752351","197753099","197753611","197753355","10023691","10023435","197712395","9904139","9904140","9904651","9904652","9904395","9904396","9903371","9903883","9903627","9902603","9902604","9903115","9903116","9902859","9902860","9901835","9902347","9902091","9901067","9901068","9901579","9901580","9901323","9901324","9900299","9900811","9900555","9899531","9900043","9899787","9897995","9898507","9898251","9896459","9896971","9896715","9894923","9895435","9895179","9893387","9893899","9893643","9891851","9892363","9892107","9898763","9899275","9899019","9897227","9897739","9897483","9895691","9896203","9895947","9894155","9894667","9894411","9892619","9893131","9892875","9891083","9891595","9891339","9927179","9927691","9927435","9926411","9926923","9926667","9925643","9926155","9925899","9924875","9925387","9925131","9924107","9924619","9924363","9923339","9923851","9923595","9922571","9923083","9922827","9921803","9922315","9922059","9921035","9921547","9921291","9920267","9920779","9920523","9919499","9920011","9919755","9918731","9919243","9918987","9917963","9918475","9918219","9917195","9917707","9917451","9916427","9916939","9916683","9915659","9916171","9915915","9914891","9915403","9915147","9914123","9914635","9914379","9913355","9913867","9913611","9912587","9913099","9912843","9911819","9912331","9912075","9912085","9912095","9911051","9911563","9911307","9910283","9910795","9910539","9909515","9910027","9909771","9908747","9909259","9909003","9907979","9908491","9908235","9907211","9907723","9907467","9906443","9906955","9906699","9905675","9906187","9905931","9904907","9905419","9905163","9928203","9928459","9928715","9928971","200505355","198706955","198707211","198709003","198709259","200533003","198707467","198707723","198707979","198708235","198708491","198708747","198710539","198710795","198711051","198711307","198711563","198711819","198712075","198712331","198712587","198712843","198713099","198713355","198713611","198713867","198714123","198714379","198714635","198714891","198715147","198715403","198715659","198715915","198716171","198716427","198716683","198716939","198717195","198717451","198717707","198717963","198718475","200481803","198718219","198718731","198701835","198702091","198700043","198702347","198702603","200415755","200416011","200416267","200416523","200419595","200419851","200420875","200421643","200422923","200424715","200424971","200427275","200429579","200431883","200435211","200436747","200437003","200437259","200437515","200438027","200438283","200438539","200438795","200439051","200439563","200440587","200440843","200441611","200441867","200442123","200442891","198716428","198711308","198711564","198711820","198712844","198714892","198715148","198715404","198715916","200443147","200444939","200445195","200445451","200445707","200449291","200449547","200449803","200450059","200450571","200450827","200451083","200451339","200451349","200451359","200452107","200451851","200451595","199366411","199366421","199366431","10027019","10027275","10028043","10028299","10028555","10028811","10029067","10033931","10034187","10034443","10034699","10034955","10035211","10035467","10035723","10035979","10036235","10036747","10043147","10045451","199436555","199437323","199540747","199619595","199619851","199716875","199718411","199718667","199718923","199719691","199719947","199687424","199687424","199687424","199688960","199688960","199688960","199689728","199689728","199689728","199689984","199689984","199689984","9878283","9878539","9878795","9879051","9879307","9879563","9879819","9880075","9956875","9876235","9876491","9876747","9877003","9877259","9877515","9877771","9878027","9880331","9880587","9880843","9881099","9881355","9881611","9881867","9882123"]

    def seleniumChromeInit(self):

        # 模拟创建一个浏览器对象，然后可以通过对象去操作浏览器
        driverPath = r'./Chrome/Application/chromedriver.exe'
        self.downloadPath = r'C:\Users\Administrator\Downloads'
        # 浏览器驱动
        options = webdriver.ChromeOptions()
        prefs = {'profile.default_content_settings.popups': 0, 'download.default_directory': self.downloadPath}
        options.add_experimental_option('prefs', prefs)
        #options.add_argument("--no-sandbox")
        # options.add_argument('--headless')
        browserDriver = webdriver.Chrome(executable_path=driverPath, chrome_options=options)
        # browserDriver.maximize_window()     # 设置最大化
        browserDriver.set_window_size(1366,900)
        self.browserDriver = browserDriver
        return browserDriver

        browserDriver.close()




    def login(self,browserDriver):
        # 打开网页 url
        # self.url = 'https://www.baidu.com'
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

    def refPage(self,browserDriver):
        browserDriver.refresh()
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


    def menuClick(self,browserDriver):
        browserDriver.find_element_by_xpath("//*[contains(text(), '面向运维')]").click()                # 点击面向运维
        # browserDriver.find_element_by_xpath("//div[@class='floatNav']/ul/li/dl/dd/a[2]").text          # 打印 文本
        browserDriver.find_element_by_xpath("//div[@class='floatNav']/ul/li/dl/dd/a[2]").click()        # 点击 数据业务质量分析 连接

        try:
            ifreamTag = WebDriverWait(browserDriver, 10).until(EC.presence_of_element_located((By.XPATH, "//*[contains(@id,'div_md_1063')]")))  # 等待到 框架元素出现
        except Exception as e:
            print(e)
            time.sleep(3)
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
            # print(element._parent.title)
            pass


        self.hourClick()
        self.cellClick()
        self.userClick()


        """ 选择HTTP指标大分类"""
        http = browserDriver.find_element_by_xpath("//*[text()='HTTP']/../div[1]")
        if http:
            webdriver.ActionChains(browserDriver).move_to_element(http).perform()  # 鼠标移动到 HTTP 元素上
            http.click()                                                            # 点击 HTTP 元素
            ActionChains(browserDriver).double_click(http).perform()                # 双击




        """ 选择TCP指标大分类"""
        tcp = browserDriver.find_element_by_xpath("//*[text()='TCP']/../div[1]")
        if tcp:
            webdriver.ActionChains(browserDriver).move_to_element(tcp).perform()  # 鼠标移动到 TCP 元素上
            tcp.click()                                                            # 点击 TCP 元素
            ActionChains(browserDriver).double_click(tcp).perform()  # 双击


        """ 选择TCP指标大分类"""
        traffic = browserDriver.find_element_by_xpath("//*[text()='流量']/../div[1]")
        if traffic:
            webdriver.ActionChains(browserDriver).move_to_element(traffic).perform()  # 鼠标移动到 流量 元素上
            traffic.click()                                                            # 点击 流量 元素
            ActionChains(browserDriver).double_click(traffic).perform()  # 双击






        """     时间设置    """
        # 设置时间    data-value="timevalue"   name="timevalue"
        kpiTime = browserDriver.find_elements_by_xpath("//*[@data-value='timevalue']")[-1]
        webdriver.ActionChains(browserDriver).move_to_element(kpiTime).perform()
        kpiTime.click()
        time.sleep(0.5)
        timeInput = browserDriver.find_elements_by_xpath("//input[@name='timevalue']")[-1]
        timeInputId = timeInput.get_attribute("id")
        timeInput.send_keys(Keys.CONTROL, 'a')          # 全选 ctrl + a
        timeInput.send_keys(Keys.DELETE)                # 删除键
        timeInput.send_keys(self.queryTime)     # 输入时间
        # timeInput.send_keys("2018-09-26 00:00:00 至 2018-09-27 00:00:00")     # 输入时间

        okButton = browserDriver.find_elements_by_xpath('//*[@class="x-btn x-unselectable x-box-item x-toolbar-item x-btn-default-toolbar-small"]')[1]
        if okButton:
            okButton.click()        #点击确定按钮

        self.clearData(browserDriver)       #隐藏数据界面

    def cellClick(self):
        # 选择'  小区 纬度
        try:
            time.sleep(2)
            postsion = browserDriver.find_element_by_xpath("//span[text()='位置']/../div[1]")
            if postsion :
                webdriver.ActionChains(browserDriver).move_to_element(postsion).perform()
                postsion.click()
            time.sleep(2)
            cell = browserDriver.find_element_by_xpath("//span[text()='小区']")
            if cell:
                webdriver.ActionChains(browserDriver).move_to_element(cell).perform()
                cell.click()
            return True
        except Exception as e:
            print(e)
            print("选择小区异常，重试...")
            self.cellClick()


    def hourClick(self):
        # 选择 小时级
        try:
            time.sleep(2)
            hour = browserDriver.find_element_by_xpath("//*[text()='小时']")
            if hour:
                webdriver.ActionChains(browserDriver).move_to_element(hour).perform()
                hour.click()
                return True
        except Exception as e:
            print(e)
            print("选择小时级异常，重试...")
            self.hourClick()


    def userClick(self):
        # 选择'  用户  纬度
        try:
            time.sleep(2)
            userClass = browserDriver.find_element_by_xpath("//span[text()='用户']/../div[1]")
            if userClass :
                browserDriver.execute_script("window.scrollBy(0,200)", "")  # 向下滚动200px
                userClass.click()
            time.sleep(3)
            user = browserDriver.find_element_by_xpath("//tr[@data-qtip='双击选中所有【用户】类型的维度']/../../following-sibling::table[1]//span[text()='用户']")
            if user:
                webdriver.ActionChains(browserDriver).move_to_element(user).perform()
                user.click()
                return True

        except Exception as e:
            print(e)
            print("选择用户级异常，重试...")
            self.userClick()





    def queryCell(self,cellList ,browserDriver):
        self.currCgi = cellList
        """     小区设置    """

        cellSelectButton = browserDriver.find_elements_by_xpath("//*[text()='小区']")[1]
        # 点击小区选择
        if cellSelectButton:
            cellSelectButton.click()

        clearEciButton = browserDriver.find_element_by_xpath("//*[text()='清空']")
        if clearEciButton:                                 # 清空上一次的ECI
            clearEciButton.click()

            cgiInput = browserDriver.find_element_by_xpath('//*[@placeholder="【CGI】"]')
            if cgiInput:
                cgiInput.send_keys(','.join(self.currCgi))    # 输入eci
            cgiAdd = browserDriver.find_element_by_xpath('//*[contains(@class,"btnCmpAdd")]')
            if cgiAdd:
                cgiAdd.click()              # 点击添加
                #time.sleep(0.5)




        # for cgi in self.currCgi:
        #     cgiInput = browserDriver.find_element_by_xpath('//*[@placeholder="【CGI】"]')
        #     if cgiInput:
        #         cgiInput.send_keys(cgi)    # 输入eci
        #     cgiAdd = browserDriver.find_element_by_xpath('//*[contains(@class,"btnCmpAdd")]')
        #     if cgiAdd:
        #         cgiAdd.click()              # 点击添加
        #         #time.sleep(0.5)


        cgiOKButton = browserDriver.find_element_by_xpath('//*[contains(@class,"btnCmpOk")]')
        if cgiOKButton:
            cgiOKButton.click()              # 点击 确定
            time.sleep(0.5)


            """   查询时间设置    """
            # 设置时间    data-value="timevalue"   name="timevalue"
            kpiTime = browserDriver.find_elements_by_xpath("//*[@data-value='timevalue']")[-1]
            webdriver.ActionChains(browserDriver).move_to_element(kpiTime).perform()
            kpiTime.click()
            time.sleep(0.5)
            timeInput = browserDriver.find_elements_by_xpath("//input[@name='timevalue']")[-1]
            timeInputId = timeInput.get_attribute("id")
            timeInput.send_keys(Keys.CONTROL, 'a')  # 全选 ctrl + a
            timeInput.send_keys(Keys.DELETE)  # 删除键
            timeInput.send_keys(self.queryTime)  # 输入时间
            # timeInput.send_keys("2018-09-26 00:00:00 至 2018-09-27 00:00:00")     # 输入时间

            okButton = browserDriver.find_elements_by_xpath(
                '//*[@class="x-btn x-unselectable x-box-item x-toolbar-item x-btn-default-toolbar-small"]')[1]
            if okButton:
                okButton.click()  # 点击确定按钮
            """     查询时间设置    """


            # 点击查询按钮
            queryButton= browserDriver.find_element_by_xpath("//*[@id='ID_button_query']")
            if queryButton:
                queryButton.click()                 # 点击 确定
                self.queryCompalte(browserDriver)   # 等待查询完成
                self.exportAll(browserDriver)       # 导出
                self.cgiList.pop(0)                 # 删除 查询过的eci




    def exportAll(self,browserDriver):
        # 导出本次查询
        exportAllButton= browserDriver.find_element_by_xpath("//*[@id='ID_button_exportAll']")
        if exportAllButton:
            exportAllButton.click()     # 点击导出按钮

            fileNameInput = browserDriver.find_element_by_xpath("//input[@name='fileName']")
            if fileNameInput:
                fileNameInput.clear()
                fileNameInput.send_keys("_".join(self.currCgi))
                # time.sleep(0.5)

            excelAllButton = browserDriver.find_element_by_xpath("//*[@value='EXCEL']")
            if excelAllButton:
                excelAllButton.click()
                time.sleep(0.5)

            csvButton = browserDriver.find_element_by_xpath("//*[text()='CSV']")
            if csvButton:
                csvButton.click()
                time.sleep(0.5)

            maxRowInput = browserDriver.find_element_by_xpath("//*[@value='50000']")
            if maxRowInput:
                maxRowInput.clear()
                maxRowInput.send_keys('100000')
                # time.sleep(1)

            startExportInput = browserDriver.find_element_by_xpath("//*[text()='开始导出']")
            if startExportInput:
                startExportInput.click()
                self.count = 0                              # 等待完成迭代计数器
                self.exportCompalte(browserDriver)          # 等待导出完成



    def exportCompalte(self,browserDriver):
        # 查询是否完成 返回 True
        time.sleep(2)
        try:
            browserDriver.switch_to.default_content()  # 切换到默认的ifream
            if self.count>=100 :
                return False
            else:
                self.count = self.count +1
                exportCompalteButton= browserDriver.find_element_by_xpath("//a[@class='closebtn']")
                if exportCompalteButton:
                    self.saveCurr()             #保存进度
                    exportCompalteButton.click()
                    print('导出完成')
                    browserDriver.switch_to.frame(self.iframeId)  # 切换到 exportIfream
                    return True
                else:
                    time.sleep(1)
                    print('正在导出...')
                    return self.exportCompalte(browserDriver)
        except Exception as e:
            print(e)
            return self.exportCompalte(browserDriver)

    def saveCurr(self):
        with open('./tab/currentEGI.dat', 'a+', encoding='utf-8', errors=None) as f:  # 将采集进度写入文件
            f.writelines(str(self.currCgi).strip() + '\n')

    def readCurr(self):
        if os.path.isfile('./tab/currentEGI.dat'):
            with open('./tab/currentEGI.dat', 'r', encoding='utf-8', errors=None) as f:  # 读取采集进度文件
                currEgi = [line.strip() for line in f.readlines()]
                if currEgi[-1] in self.cgiList:
                    return self.cgiList.index(currEgi[-1])
                else: return 0
        else: return 0

    def queryCompalte(self,browserDriver):
        # 查询是否完成 返回 True
        try:
            stopButton= browserDriver.find_element_by_xpath("//*[@id='ID_button_stop']")
        except Exception as  e:
            print(e)

        if stopButton:
            if stopButton.get_attribute('class') == 'toolbar-item':
                time.sleep(1)
                return self.queryCompalte(browserDriver)
            if stopButton.get_attribute('class') == 'toolbar-item z-dis':
                return True

    def clearData(self,browserDriver):
        try:
            gridViewId = browserDriver.find_element_by_xpath("//*[@id='gridView']").get_attribute('id')
            js = '$("#' + gridViewId + '").hide();'  # 删除div元素
            # js = '$("#' + gridViewId + '").remove();'  # 删除div元素
            browserDriver.execute_script(js)
        except Exception as e:
            pass



    def isFileDonwed(self,cgi):
        fileList = os.listdir(self.downloadPath)
        if len(fileList)>0:
            for fileName in fileList:
                if cgi in fileName.split("_"):
                    return True
            return False
        return False


if __name__=="__main__":
    xdr = GetXDR()
    browserDriver = xdr.seleniumChromeInit()
    xdr.login(browserDriver)
    xdr.menuClick(browserDriver)
    CurrCgiIndex = xdr.readCurr()
    cellList = []
    cgiCount = 0
    for i,cgi in enumerate(xdr.cgiList[CurrCgiIndex:-1]):
        if xdr.isFileDonwed(cgi):
            # 如果cgi存在与目标文件名中,则跳过
            continue
        else:
            cellList.append(cgi)

        if len(cellList) % 400 == 0:
            # 如果大于 40 次 则刷新网页 以防止 key 过期
            try:
                xdr.refPage(browserDriver)
                xdr.menuClick(browserDriver)
            except Exception as e:
                print(e)

        if len(cellList)%10==0 or i+1==len(xdr.cgiList[CurrCgiIndex:-1]):
            # 10 个cgi 一组 也就是说每次取 10 个小区
            try:
                xdr.queryCell(cellList,browserDriver)
            except Exception as e:
                print(e)
            finally:
                cellList.clear()    # 清空 cellList []

    print('benlun yi wan')
    browserDriver.quit()