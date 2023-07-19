import urllib.request
from bs4 import BeautifulSoup


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
