#!usr/bin/env python
#-*- coding:utf-8 _*-

"""
@author:Administrator
@file: dianping_API.py
@time: 2018/08/{DAY}
描述: 大众点评 API
返回json格式的结果
"""


import requests
from bs4  import BeautifulSoup




class GetXDR():
    def __init__(self):
        self.url = 'http://10.217.4.22:9088/analysisController.do?method=exportAll'
        self.urlTest = 'http://10.217.4.22:9088/web/index.jsp'
        self.headers = {"Accept": "*/*",
                        "Accept-Encoding": "gzip, deflate",
                        "Accept-Language": "zh-CN,zh;q=0.9",
                        "Cache-Control": "no-cache",
                        "Connection": "keep-alive",
                        "Content-Length": "2970",
                        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
                        "Cookie": "JSESSIONID=D3E02783EF9675E362A364D6A2FC9E56.jvm2; theme=deepblue",
                        "DNT": "1",
                        "Host": "10.217.4.22:9088",
                        "Origin": "http://10.217.4.22:9088",
                        "Pragma": "no-cache",
                        "Referer": "http://10.217.4.22:9088/analysisConfigController.do?method=begin&reurl=ui.report&viewModuleId=11431&moduleId=1063&iframeId=div_md_1063_1534933880&iframeTitle=%25E6%2595%25B0%25E6%258D%25AE%25E4%25B8%259A%25E5%258A%25A1%25E8%25B4%25A8%25E9%2587%258F%25E5%2588%2586%25E6%259E%2590",
                        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.162 Safari/537.36 Avast/65.0.411.162",
                        "X-Requested-With": "XMLHttpRequest"
                        }

        self.parmaters = {"method": "exportAll",
                            "fileName": "数据业务质量分析",
                            "exportType": "2",
                            "textSplitSymbol": ",",
                            "wordSplitSymbol": ",",
                            "csvSplitSymbol": ",",
                            "csvQuotationSymbol": '"',
                            "excelMinCellWidth": "80",
                            "excelMinRowHeight": "20",
                            "moreFile": "1",
                            "maxFileRow": "1000000",
                            "fieldToString": "",
                            "exportMethod": "exportAll",
                            "columnTitles": "时间,小区,小区ID,大页面下载速率(kbps),小页面显示时长(ms),页面响应平均时长(ms)",
                            "columnNames": "TIMEVALUE,CELLID,CELLID,KPI_AVGWEBDLRATE,KPI_AVGWEBOPENDELAY,KPI_AVGWEBRESDELAY",
                            "columnWidths": "150,85,85,142,131,143",
                            "moduleName": "数据业务质量分析",
                            "moduleId": "1063",
                            "queryParams": '<?xml version="1.0" encoding="GB18030" standalone="yes"?><USERPARAMS><dataSource id="st_cl" moduleId="4565"/><extend><item field="TIME" value="MINUTE15"/><item field="ENDTIME" value="MINUTE15"/></extend><time id="timevalue" starttime="2018-07-28 00:00:00" endtime="2018-08-02 00:00:00" discrete="5"/><conditions><and><condition field="cellid" value="198187275|198187285|198187295" operator="=" type="string" caption="小区" display="198187275,198187285,198187295"/><condition field="DIMENSION" value="timevalue|cellid" operator="in" type="string" caption="维度" display="时间, 小区"/></and></conditions><measures><measure field="kpi_avgWebDLRate"/><measure field="kpi_avgWebOpenDelay"/><measure field="kpi_avgWebResDelay"/></measures><dimensions><dimension field="timevalue" display="时间"/><dimension field="cellid" display=" 小区"/></dimensions></USERPARAMS>',
                            "queryType": "1",
                            "queryFrom": "",
                            "queryid": "D3E02783EF9675E362A364D6A2FC9E56.jvm2_1063_1534926781712_59137955_9dea_4cb9_a7ce_86a843795500",
                            "frameId": "div_md_1063_1534933880",
                            "pushThreadKey": "key_2c00c546-77d8-4fbe-b4a0-637a31e5c4e8",
                            "dataSourceType": "1",
                            "exportLogMsg": "	开始时间:2018-07-28 00:00:00	结束时间:2018-08-02 00:00:00	小区:198187275,198187285,198187295	维度:时间, 小区	指标选择:大页面下载速率(kbps),小页面显示时长(ms),页面响应平均时长(ms)",
                            "page": "1"
                            }

    def exceptAll(self,page):
        try:
            result = requests.post(self.urlTest, params=self.parmaters, timeout=300, headers=self.headers)
            # 请求重试次数加1
            if result.status_code == 200:
                soup = BeautifulSoup(result.text, 'html.parser')  # 将返回的网页转化为bs4 对象
                tabTag = soup.find_all("td")

        except  Exception as e:
            print(e)



if __name__=="__main__":
    xdr = GetXDR()
    xdr.exceptAll(1)


