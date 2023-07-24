import json
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.header import Header
import requests
import urllib.request
from bs4 import BeautifulSoup

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


def get_weather_msg():
    url = "http://www.weather.com.cn/weather/101100701.shtml"
    header = ("User-Agent",
              "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 "
              "Safari/537.36")  # 设置头部信息
    opener = urllib.request.build_opener()  # 修改头部信息
    opener.addheaders = [header]  # 修改头部信息
    request = urllib.request.Request(url)  # 制作请求
    response = urllib.request.urlopen(request)  # 得到请求的应答包
    html = response.read()  # 将应答包里面的内容读取出来
    html = html.decode('utf-8')  # 使用utf-8进行编码，不重新编码就会成乱码

    final = []  # 初始化一个空的list，我们为将最终的的数据保存到list
    bs = BeautifulSoup(html, "html.parser")  # 创建BeautifulSoup对象
    body = bs.body  # 获取body部分
    data = body.find('div', {'id': '7d'})  # 找到id为7d的div
    ul = data.find('ul')  # 获取ul部分
    li = ul.find_all('li')  # 获取所有的li

    i = 0
    for day in li:  # 对每个li标签中的内容进行遍历
        if i < 7:
            temp = []
            date = day.find('h1').string  # 找到日期
            #         print (date)
            temp.append(date)  # 添加到temp中
            #     print (temp)
            inf = day.find_all('p')  # 找到li中的所有p标签
            #     print(inf)
            #     print (inf[0])
            temp.append(inf[0].string)  # 第一个p标签中的内容（天气状况）加到temp中
            if inf[1].find('span') is None:
                temperature_highest = None  # 天气预报可能没有当天的最高气温（到了傍晚，就是这样），需要加个判断语句,来输出最低气温
            else:
                temperature_highest = inf[1].find('span').string  # 找到最高温度
                temperature_highest = temperature_highest.replace('℃', '')  # 到了晚上网站会变，最高温度后面也有个℃
            temperature_lowest = inf[1].find('i').string  # 找到最低温度
            temperature_lowest = temperature_lowest.replace('℃', '')  # # 最低温度后面有个℃，去掉这个符号
            temp.append(temperature_highest)
            temp.append(temperature_lowest)
            final.append(temp)
            i = i + 1
    return final


def gener_weather_msg():
    weather_msg_list = get_weather_msg()
    weather_msg_head = "<h1>近日天气</h1>"
    weather_msg = ""
    for weather in weather_msg_list:
        weather_msg += "{} {} {}°C~{}°C".format(weather[0], weather[1], weather[3], weather[2])
        weather_msg += '<br>'

    return weather_msg_head + weather_msg


def weather_job():
    try:
        return gener_weather_msg()
    except:
        return "weather_job_error"


def parse_hot_news_json_data(data):
    one_hot_news_dict = {
        "title": data["word"]
    }
    one_hot_news_dict['url'] = "https://s.weibo.com/weibo?q=%23" + one_hot_news_dict["title"] + "%23"
    if 'label_name' in data:
        if data["label_name"] == '':
            one_hot_news_dict["label"] = "普"
        else:
            one_hot_news_dict["label"] = data["label_name"]
    else:
        one_hot_news_dict["label"] = "普"
    if 'realpos' in data:
        one_hot_news_dict["rank"] = data["realpos"]

    if 'category' in data:
        one_hot_news_dict["category"] = data["category"]
    return one_hot_news_dict


def parse_hot_news_html(html):
    data = json.loads(html)
    parsed_list = []
    data_dict = data["data"]["realtime"]
    for one_hot_news_dict in data_dict:
        parsed_list.append(parse_hot_news_json_data(one_hot_news_dict))
    return parsed_list


def gener_hot_news_msg():
    html = requests.get("https://weibo.com/ajax/side/hotSearch").text
    parsed_list = parse_hot_news_html(html)
    hot_news_head = "<h1>微博热搜</h1>"
    hot_news = ""
    count = 1
    for one_hot_news in parsed_list:
        if count == 11:
            break
        hot_news += "{}.<{}><a href='{}'>{}</a>".format(count,
                                                        one_hot_news["label"], one_hot_news["url"],
                                                        one_hot_news["title"])
        hot_news += '<br>'
        count += 1

    return hot_news_head + hot_news


def hot_news_job():
    try:
        return gener_hot_news_msg()
    except:
        return "hot_news_job_error"


def remain_days_job():
    import datetime
    try:
        appointedTime = "2023-12-23"
        appointed_time = datetime.datetime.strptime(appointedTime, "%Y-%m-%d")
        curr_datetime = datetime.datetime.now()
        minus_date = appointed_time - curr_datetime
        return "<h1><a style='color:red'>考研还有" + "【" + str(minus_date.days + 1) + "】" + "天</a></h1>"
    except:
        return "remain_days_job_error"


def parse_total_msg():
    hot_news_job_msg = hot_news_job()
    weather_job_msg = weather_job()
    remain_days_job_msg = remain_days_job()
    return weather_job_msg + hot_news_job_msg + remain_days_job_msg


sendemail("每日邮件", parse_total_msg())
