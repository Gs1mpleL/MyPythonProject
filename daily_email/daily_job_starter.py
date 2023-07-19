import sys
import os

curPath = os.path.abspath(os.path.dirname(__file__))
rootPath = os.path.split(curPath)[0]
sys.path.append(rootPath)
from easy_job import remain_days_job
from hot_news_catcher import hot_news_job
from weather_catcher import weather_job


def total_job_run():
    hot_news_msg = hot_news_job()
    weather_job_msg = weather_job()
    remain_days_job_msg = remain_days_job()
    return weather_job_msg + hot_news_msg + remain_days_job_msg



