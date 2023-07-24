import re


def get_local_time():
    import time
    # 获取当前时间
    current_time = int(time.time())
    # 转换为localtime
    localtime = time.localtime(current_time)
    # 利用strftime()函数重新格式化时间
    return time.strftime('%Y-%m-%d %H:%M:%S', localtime)


def re_findall(re_match_text, text):
    return re.findall(re_match_text, text, re.M | re.I)
