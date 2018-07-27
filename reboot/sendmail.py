import smtplib
from email.mime.text import MIMEText


# 邮件设置
EMAIL_HOST = "smtp.mxhichina.com"
EMAIL_PORT = 25
EMAIL_USER = "sa-notice@yuanxin-inc.com"
EMAIL_PASSWORD = "Miao13456"
EMAIL_FROM = "sa-notice@yuanxin-inc.com"


def send_mail(to_addr, title, content):
    _server_conn = smtplib.SMTP(EMAIL_HOST, EMAIL_PORT)
    _server_conn.ehlo()
    # _server_conn.starttls()
    _server_conn.login(EMAIL_USER, EMAIL_PASSWORD)

    # 发送邮件
    message = MIMEText(content, 'html', 'utf-8')
    message['From'] = EMAIL_FROM
    message['Subject'] = title
    message['To'] = ';'.join(to_addr)
    # print message.as_string()
    _server_conn.sendmail(EMAIL_FROM, to_addr, message.as_string())
    # 关闭当前连接的session
    res = _server_conn.quit()
    return res


