import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.header import Header

smtp_ssl = "smtp.qq.com"
smtp_ssl_port = 465
my_email = "804121985@qq.com"
my_email_authentication_code = "不给！"


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
