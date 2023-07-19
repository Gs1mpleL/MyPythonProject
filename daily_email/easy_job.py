import datetime


def remain_days_job():
    try:
        appointedTime = "2023-12-23"
        appointed_time = datetime.datetime.strptime(appointedTime, "%Y-%m-%d")
        curr_datetime = datetime.datetime.now()
        minus_date = appointed_time - curr_datetime
        return "<h1><a style='color:red'>考研还有" + "【" + str(minus_date.days + 1) + "】" + "天</a></h1>"
    except:
        return "remain_days_job_error"
