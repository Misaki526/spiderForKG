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
    h1 = ["（一）", "（二）", "（三）", "（四）", "（五）", "（六）", "（七）", "（八）", "（九）"]
    h3 = ["（1）", "（2）", "（3）", "（4）", "（5）", "（6）", "（7）", "（8）", "（9）"]

    nodeList = soup.select('.title-text span')
    for node in nodeList:
        # 名称，如病因，治疗等等（开始标签）
        fout.write("<" + node.nextSibling + ">\n")

        value = node.parent.parent.next_sibling.next_sibling
        TYPEOFTAG = value     # 用于后面判断类型，暂时没想到更好的办法

        # ------如果大标题下没有小标题：直接输出内容---------
        cur = value
        i = 0
        while (1):
            if (type(cur) == type(TYPEOFTAG)):
                if (not cur.has_attr('class') or cur['class'][0] != 'para'):
                    break
                if len(cur.select('b')) > 0:
                    i = i + 1
            cur = cur.next_sibling
        if i == 0:
            cur = value
            while (1):
                if (type(cur) == type(TYPEOFTAG)):
                    if (not cur.has_attr('class') or cur['class'][0] != 'para'):
                        break
                    else:
                        fout.write(cur.get_text())
                cur = cur.next_sibling
            fout.write("\n")
        # --------------------end---------------------------


        # 具体遍历每一个小标题
        # FILO，以后可以考虑用stack来存放，在合适的地方输出结束标签（一） > 1 > （1）
        stack=[]
        while (1):
            if (type(value) == type(TYPEOFTAG)):
                if (not value.has_attr('class') or value['class'][0] != 'para'):
                    break

                if len(value.select('b')) > 0:
                    # 型如（一）这种形式，将栈中的所有元素弹出并输出
                    if value.select('b')[0].get_text()[0:3] in h1:
                        while len(stack) > 0:
                            text = stack.pop(-1)
                            if text[0:1] == "（":
                                #if stackFlag.pop(-1) == 0:
                                    #fout.write(value.next_sibling.next_sibling.get_text())
                                fout.write("</" + text[3:] + ">\n")
                            else:
                                #if stackFlag.pop(-1) == 0:
                                    #fout.write(value.next_sibling.next_sibling.get_text())
                                fout.write("</" + text[2:] + ">\n")
                        fout.write("<" + value.select('b')[0].get_text()[3:] + ">\n")
                        stack.append(value.select('b')[0].get_text())


                    # 型如 1. 这种形式，将 1. 形式的元素弹出并输出
                    elif value.select('b')[0].get_text()[1:2] == "." or value.select('b')[0].get_text()[1:2] == "．":
                        while len(stack) > 0:
                            text = stack[-1]
                            if text[0:1] == "（":
                                break
                            else:
                                #if stackFlag.pop(-1) == 0:
                                    #fout.write(value.next_sibling.next_sibling.get_text())
                                fout.write("</" + stack.pop(-1)[2:] + ">\n")
                        fout.write("<" + value.select('b')[0].get_text()[2:] + ">\n")
                        stack.append(value.select('b')[0].get_text())


                    # 型如（1）这种形式，没有更低级的元素，不用入栈
                    elif value.select('b')[0].get_text()[0:3] in h3:
                        fout.write("<" + value.select('b')[0].get_text()[3:] + ">")
                        fout.write(value.get_text()[len(value.select('b')[0].get_text()):])
                        fout.write("</" + value.select('b')[0].get_text()[3:] + ">\n")

            value = value.next_sibling

        # 输出栈中尚未输出的元素
        while len(stack) > 0:
            text = stack.pop(-1)
            if text[0:1] == "（":
                fout.write("</" + text[3:] + ">\n")
            else:
                fout.write("</" + text[2:] + ">\n")

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
