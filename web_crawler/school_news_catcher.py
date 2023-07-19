import sys
import os

curPath = os.path.abspath(os.path.dirname(__file__))
rootPath = os.path.split(curPath)[0]
sys.path.append(rootPath)

from my_utils import email_sender
from my_utils.base_utils import get_local_time

import time

import requests as req
import re


# 提取html格式类似 <href="xxx" xxx>xxxx</xx> 这样的信息，返回超链接和文本信息
def list_href_text(school_name, request_url, re_match_text):
    html = req.get(request_url)
    html.encoding = "utf-8"
    html = html.text
    news_list_tuple = re.findall(re_match_text, html, re.M | re.I)
    # 只取最新一条公告
    tmp_list = list(news_list_tuple[0])
    tmp_list[0] = list(re.findall('(.*?).edu.cn', request_url, re.M | re.I))[
                      0] + ".edu.cn" + tmp_list[0]
    print(school_name + "->最新公告：<" + str(tmp_list[1]) + ">  time:" + get_local_time())
    tmp_list.append(school_name)
    return tmp_list


def get_total_news_jobs_list():
    total_news_list = []
    # 西电
    total_news_list.append(list_href_text("西安电子科技大学", "https://gr.xidian.edu.cn/yjsy/yjszs.htm",
                                          '<a href="..(.*?)" target="_blank">(.*?)</a><span>'))
    # 西南交通
    total_news_list.append(list_href_text("西南交通大学",
                                          "http://yz.swjtu.edu.cn/vatuu/WebAction?setAction=newsList&viewType=secondStyle&selectType=smallType&keyWord=61E92EF67418DC54",
                                          'a href="..(.*?)" target="_blank">(.*?)</a></h3>'))
    return total_news_list


def compare_list(original_list, new_list):
    need_to_send = ''
    count = 0
    for i in original_list:
        if original_list[count] != new_list[count]:
            need_to_send += "<h1>" + new_list[count][2] + "</h1>" + "<h3><a href='" + str(
                new_list[count][0]) + "'>" + str(new_list[count][1]) + "</a></h3>"
        count += 1
    return need_to_send


def scanner_run():
    original_list = get_total_news_jobs_list()
    while True:
        try:
            new_list = get_total_news_jobs_list()
            need_to_send = compare_list(original_list, new_list)
            if need_to_send != '':
                original_list = new_list
                print(need_to_send)
                email_sender.sendemail("院校公告更新", need_to_send)
            time.sleep(300)
        except:
            print("爬虫运行出错,重启中....")
            time.sleep(100)
            continue


scanner_run()
