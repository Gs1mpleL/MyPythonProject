import os
import sys

curPath = os.path.abspath(os.path.dirname(__file__))
rootPath = os.path.split(curPath)[0]
sys.path.append(rootPath)
import time

import schedule

from daily_email.daily_job_starter import total_job_run
from my_utils import email_sender


def my_function():
    email_sender.sendemail("每日邮件", total_job_run())


schedule.every().day.at("08:00").do(my_function)

while True:
    schedule.run_pending()
    time.sleep(1)