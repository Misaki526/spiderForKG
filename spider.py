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

def catagory(html):
    # 以追加的方式打开
    fout = open("data.txt", "a")

    soup = BeautifulSoup(html)

    # 疾病名
    name = soup.h1.string
    fout.write(name + "\n")

    # 基本信息
    baseNameList = soup.select('.basic-info dt')
    baseValueList = soup.select('.basic-info dd')
    for i in range(0, len(baseNameList)):
        fout.write(baseNameList[i].get_text() + "\t" + baseValueList[i].get_text().replace("\n", "") + "\n")   # 去掉value中自带的回车

    # 各个属性
    nodeList = soup.select('.title-text span')
    for node in nodeList:
        # 名称
        fout.write(node.nextSibling + "\t")
        value = node.parent.parent.next_sibling.next_sibling
        TYPEOFTAG = value     #用于后面判断类型，暂时没想到更好的办法

        while (1):
            if (type(value) == type(TYPEOFTAG)):
                if (not value.has_attr('class') or value['class'][0] != 'para'):
                    break
                if len(value.select('b')) > 0 and (value.select('b')[0].get_text()[1:2] == '.' or value.select('b')[0].get_text()[1:2] == '．'):           # 暂时只找形如'1.'类型的值
                    fout.write(value.select('b')[0].get_text()[2:] + "\t")

            value = value.next_sibling

        fout.write("\n")

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
