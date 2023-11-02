import time

import requests as req
import re

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.header import Header

smtp_ssl = "smtp.qq.com"
smtp_ssl_port = 465
my_email = "804121985@qq.com"
my_email_authentication_code = "mwlopuckbuhebdbh"


def generate_html(text):
    html_string_head = '''
    <html>
      <head><title>HTML Pandas Dataframe with CSS</title></head>
      <link rel="stylesheet" type="text/css" href="df_style.css"/>
                 '''

    html_string_tail = '''
      </body>
    </html>
    '''

    return html_string_head + text + html_string_tail


# 邮件发送模块
def sendemail(title, text):
    # 1. 连接邮箱服务器
    con = smtplib.SMTP_SSL(smtp_ssl, smtp_ssl_port)
    # 2. 登录邮箱
    con.login(my_email, my_email_authentication_code)
    # 2. 准备数据
    # 创建邮件对象
    msg = MIMEMultipart()
    # 设置邮件主题
    subject = Header(title, 'utf-8').encode()
    msg['Subject'] = subject
    # 设置邮件发送者
    msg['From'] = '804121985@qq.com'
    # 设置邮件接受者
    msg['To'] = 'lzh_tuisong@qq.com'
    # 添加⽂文字内容
    text = MIMEText(generate_html(text), 'html', 'utf-8')
    msg.attach(text)
    # 3.发送邮件
    con.sendmail('804121985@qq.com', 'lzh_tuisong@qq.com', msg.as_string())
    con.quit()


def get_local_time():
    import time
    # 获取当前时间
    current_time = int(time.time())
    # 转换为localtime
    localtime = time.localtime(current_time)
    # 利用strftime()函数重新格式化时间
    return time.strftime('%Y-%m-%d %H:%M:%S', localtime)


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
                sendemail("院校公告更新", need_to_send)
            time.sleep(300)
        except:
            print("爬虫运行出错,重启中....")
            time.sleep(100)
            continue


scanner_run()
