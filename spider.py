#coding=utf-8

import urllib
import time
import json
import requests
import re
from bs4 import BeautifulSoup
import sys

reload(sys)
sys.setdefaultencoding('utf8') # set encoding

# 以 XML 格式输出
def catagory(html):
    fout = open("data2.txt", "a")

    # 每个疾病的XML开头标签
    fout.write("<disease>\n")

    soup = BeautifulSoup(html)

    # -------疾病名 start----------------------------------
    name = soup.h1.string
    fout.write("<name>" + name + "</name>\n")
    # -------疾病名 end------------------------------------


    # -------基本信息，作为疾病的属性 start------------------
    baseNameList = soup.select('.basic-info dt')
    baseValueList = soup.select('.basic-info dd')

    fout.write("<properties>\n")
    for i in range(0, len(baseNameList)):
        fout.write("<" + baseNameList[i].get_text() + ">")
        fout.write(baseValueList[i].get_text().replace("\n", ""))   # 去掉value中自带的回车
        fout.write("</" + baseNameList[i].get_text() + ">\n")
    fout.write("</properties>\n")
    # -------基本信息，作为疾病的属性 end-------------------


    # ------具体的详细内容则按照新的实体处理 start----------
    nodeList = soup.select('.title-text span')
    for node in nodeList:
        # 名称，如病因，治疗等等（开始标签）
        fout.write("<" + node.nextSibling + ">\n")

        value = node.parent.parent.next_sibling.next_sibling
        TYPEOFTAG = value     # 用于后面判断类型，暂时没想到更好的办法


        # 具体遍历每一个小标题
        # FILO，以后可以考虑用stack来存放，在合适的地方输出结束标签（一） > 1 > （1）
        while (1):
            if (type(value) == type(TYPEOFTAG)):
                if (not value.has_attr('class') or value['class'][0] != 'para'):
                    break

                if len(value.select('b')) > 0:
                    if value.select('b')[0].get_text()[1:2] == "." or value.select('b')[0].get_text()[1:2] == "．":
                        fout.write("<" + value.select('b')[0].get_text()[2:] + ">")
                        fout.write(value.next_sibling.next_sibling.get_text())
                        fout.write("</" + value.select('b')[0].get_text()[2:] + ">\n")

            value = value.next_sibling

        # 名称（结束标签）
        fout.write("</" + node.nextSibling + ">\n")
    # ------具体的详细内容则按照新的实体处理 end ------------


    # 每个疾病的XML结束标签
    fout.write("</disease>\n")

    fout.flush()
    fout.close()


def main(html):
    # 解析返回的json数据
    hjson = json.loads(html)

    # 每次xhr会有24条数据传回来
    i = 0
    while (i < 24):
        try:
            time.sleep(5)
            # 取出每个疾病的相关链接
            url = hjson['lemmaList'][i]['lemmaUrl']

            f = urllib.urlopen(url)
            text = f.read()
            catagory(text)

            # 及时关闭
            f.close()
            i = i + 1
        except Exception, result:
            # 异常则重新爬取
            # pass
            print result


if __name__ == '__main__':
    url='http://baike.baidu.com/wikitag/api/getlemmas'
    values={'limit':'24', 'timeout':'3000', 'filterTags':'[]', 'tagId':'75953', 'fromLemma':'false', 'contentLength':'40', 'page':'0'}

    html = requests.post(url, data=values)

    main(html.text)
