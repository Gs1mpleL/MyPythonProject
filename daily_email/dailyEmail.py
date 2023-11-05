import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.header import Header
import requests
import urllib.request
from bs4 import BeautifulSoup
import json
from urllib3 import disable_warnings
import datetime
import random
import uuid
import time
import string
import hashlib

smtp_ssl = "smtp.qq.com"
smtp_ssl_port = 465
my_email = "804121985@qq.com"
my_email_authentication_code = "不给"


# 自动签到模块
class AutoSign:
    def __init__(self):
        self.log_to_msg = ''
        self.firsttime = True
        self.awardsurl = 'https://api-takumi.mihoyo.com/event/bbs_sign_reward/home?act_id=e202009291139501'
        self.roleurl = 'https://api-takumi.mihoyo.com/binding/api/getUserGameRolesByCookie?game_biz=hk4e_cn'
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) miHoYoBBS/2.3.0',
            'Referer': 'https://webstatic.mihoyo.com/bbs/event/signin-ys/index.html?bbs_auth_required=true&act_id=e202009291139501&utm_source=bbs&utm_medium=mys&utm_campaign=icon',
            'Accept-Encoding': 'gzip, deflate, br',
        }
        self.signurl = 'https://api-takumi.mihoyo.com/event/bbs_sign_reward/sign'
        self.SignInThread()

    def WriteLog(self, msg):
        print(msg)
        # 不写入log
        # with open("runlog", "a+") as f:
        #     f.write(msg + "\n")
        #     f.close()

    def SignInThread(self):
        ## 没必要循环，改成crontab
        # while True:
        #     if self.firsttime or (time.localtime().tm_hour == 4 and time.localtime().tm_min == 30 and time.localtime().tm_sec == 0):
        #         self.Init()
        #         self.firsttime = False

        self.Init()
        return self.log_to_msg

    def Init(self):
        self.conifg = self.getConfig()
        self.roles = []
        date = datetime.datetime.now()
        self.WriteLog(f"[INFO]今天是{date.year}.{date.month}.{date.day}")
        self.WriteLog(f"[INFO]导入了{len(self.conifg.cookies)}个Cookies")
        for cookies in self.conifg.cookies:
            roles = self.getRoles(cookies)
            if roles:
                print(roles)
                self.roles.append(roles)
            else:
                self.WriteLog("[Error]失效Cookies" + json.dumps(cookies))
        self.WriteLog("[INFO]获取角色成功!")
        if len(self.roles) == 0:
            self.WriteLog("[Error]没有找到任何角色!")
            exit()
        self.infolist = []
        for i in self.roles:
            for role in i:
                url = f"https://api-takumi.mihoyo.com/event/bbs_sign_reward/info?region={role['region']}&act_id=e202009291139501&uid={role['game_uid']}"
                res = requests.get(url, headers=self.headers, verify=False, cookies=role["cookies"]).json()
                if res["retcode"] != 0:
                    self.WriteLog(f"[Error]获取签到信息失败.错误信息:{res['message']}")
                    self.log_to_msg = f"[Error]获取签到信息失败.错误信息:{res['message']}"
                res['uid'] = role["game_uid"]
                res['cookies'] = role['cookies']
                res['region'] = role['region']
                self.infolist.append(res)
        self.SignIn(infolist=self.infolist)

    @staticmethod
    def get_ds():
        n = '9nQiU3AV0rJSIBWgdynfoGMGKaklfbM7'
        i = str(int(time.time()))
        r = ''.join(random.sample(string.ascii_lowercase + string.digits, 6))

        def md5(data):
            md5 = hashlib.md5()
            md5.update(data.encode())
            return md5.hexdigest()

        c = md5('salt=' + n + '&t=' + i + '&r=' + r)
        return f'{i},{r},{c}'

    def SignIn(self, infolist):
        for info in infolist:
            total_sign_day = info['data']['total_sign_day']
            awards = self.getawards(info["cookies"])
            awards = awards["data"]["awards"]
            self.WriteLog(f"[INFO]为UID:{info['uid']}签到中...")
            if info['data']['is_sign'] is True:
                self.WriteLog(F"[Waring]UID:{info['uid']}.您今日已经签到过了")
                self.log_to_msg = F"[Waring]UID:{info['uid']}.您今日已经签到过了"
                pass
            elif info['data']['first_bind'] is True:
                self.WriteLog(F"[Warning]UID:{info['uid']}请先去米游社签到一次!")
                self.log_to_msg = F"[Warning]UID:{info['uid']}请先去米游社签到一次!"

                pass
            else:
                awardname = awards[total_sign_day]['name']
                cnt = awards[total_sign_day]['cnt']
                self.WriteLog(f"[INFO]UID:{info['uid']}今日的奖励是{cnt}{awardname}")
                self.log_to_msg = f"[INFO]UID:{info['uid']}今日的奖励是{cnt}{awardname}"

                headers = {
                    'DS': self.get_ds(),
                    'Origin': 'https://webstatic.mihoyo.com',
                    'x-rpc-app_version': "2.34.1",
                    'User-Agent': 'Mozilla/5.0 (Linux; Android 9; Unspecified Device) AppleWebKit/537.36 (KHTML, like Gecko) '
                                  'Version/4.0 Chrome/39.0.0.0 Mobile Safari/537.36 miHoYoBBS/2.3.0',
                    'x-rpc-client_type': "5",
                    'Referer': '',
                    'Accept-Encoding': 'gzip, deflate',
                    'Accept-Language': 'zh-CN,en-US;q=0.8',
                    'X-Requested-With': 'com.mihoyo.hyperion',
                    'x-rpc-device_id': str(uuid.uuid3(
                        uuid.NAMESPACE_URL, json.dumps(info["cookies"]))).replace('-', '').upper(),
                }
                data = {
                    'act_id': 'e202009291139501',
                    'region': info["region"],
                    'uid': info["uid"]
                }
                res = requests.post(self.signurl, json=data, headers=headers, cookies=info["cookies"],
                                    verify=False).json()
                if res["retcode"] != 0:
                    self.WriteLog(f"[Error]UID:{info['uid']}签到失败.错误信息:{res['message']}")
                    self.log_to_msg += f"</br>[Error]UID:{info['uid']}签到失败.错误信息:{res['message']}"
                else:
                    self.WriteLog(f"[INFO]UID:{info['uid']}签到成功!")
                    self.log_to_msg += f"</br>[INFO]UID:{info['uid']}签到成功!"

    def getawards(self, cookies):
        res = requests.get(self.awardsurl, headers=self.headers, cookies=cookies, verify=False).json()
        if res["retcode"] != 0:
            self.WriteLog("[Error]获取奖励失败!")
            return None
        return res

    def getRoles(self, cookies):
        res = requests.get(self.roleurl, cookies=cookies, headers=self.headers, verify=False).json()
        if res["retcode"] != 0:
            return False
        roles = res["data"]["list"]
        for role in roles:
            role["cookies"] = cookies
        return roles

    def getConfig(self):
        try:
            # 就一条config，直接写入程序
            # file = open("config.json", "r").read()
            # ----------------------------------------------- 在这里该cookie -----------------------------------------------#
            file = "不给"
            config = json.loads(file)

            class Conifg:
                cookies = config["cookies"]

            return Conifg
        # 不读文件了
        # except FileNotFoundError:
        #     WriteLog("[Warning]未发现配置文件,重新生成中...")
        #     conifg = {"cookies": [{"ltoken": "", "cookie_token": "", "account_id": ""}]}
        #     open("config.json", "w").write(json.dumps(conifg, ensure_ascii=False))
        #     file = open("config.json", "r").read()
        #     config = json.loads(file)
        #     class Conifg:
        #         cookies = config["cookies"]
        #     return Conifg
        except json.JSONDecodeError:
            self.WriteLog("[Error]配置文件异常.请删除重试")
            exit()


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


def yuanshen_AutoSign_job():
    disable_warnings()
    sign = AutoSign()
    info = sign.log_to_msg
    return "<h1>" + "原神签到:</h1>" + info


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
    yuanshen_AutoSign_job_msg = yuanshen_AutoSign_job()
    print(weather_job_msg + hot_news_job_msg + yuanshen_AutoSign_job_msg + remain_days_job_msg)
    return weather_job_msg + hot_news_job_msg + yuanshen_AutoSign_job_msg + remain_days_job_msg


sendemail("每日邮件", parse_total_msg())
