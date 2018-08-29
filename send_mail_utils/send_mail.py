import smtplib
import configparser

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage


class SendMail(object):
    def __init__(self):
        self.smtp = smtplib.SMTP()
        self.conf = configparser.ConfigParser()
        self.conf.read('mail.conf', encoding='utf-8')
        self.mail_host = self.conf.get('mail', 'host')
        self.mail_port = self.conf.getint('mail', 'port')
        self.sender = self.conf.get('mail', 'username')
        self.password = self.conf.get('mail', 'passwd')
        self.recipient = self.conf.get('mail', 'receiver')
        self.subject = self.conf.get('mail', 'subject')

    def send(self, Image, Attachment):
        # 构造一个 MIMEMultipart 对象，邮件中有图片内容时，这样写
        msg = MIMEMultipart('related')

        # 构造主题、发件人、收件人
        msg['Subject'] = self.subject
        msg['From'] = self.sender
        msg['To'] = self.recipient

        # 邮件中有图片内容时，这样写
        msgAlternative = MIMEMultipart('alternative')
        msg.attach(msgAlternative)

        # 二进制模式读取图片文件，加载进内存
        with open(Image, 'rb') as f:
            image = MIMEImage(f.read())

        # 定义图片 ID, 在 HTML 文本中引用
        image.add_header('Content-ID', '<myimg>')
        msg.attach(image)

        # 构造 HTML，通过图片 ID 引用图片内容
        html_msg = """
          <p>Python 发送邮件测试......</p>
          <p><a href="http://www.qq.com/">腾讯</a></p>
          <h1>测试图片</h1>
          <p><img src="cid:myimg"></p>
        """
        # 邮件中有图片内容时，这样写
        msgAlternative.attach(MIMEText(html_msg, 'html', 'utf-8'))

        # 构造附件
        with open(Attachment, 'rb') as f:
            attachment = MIMEText(f.read(), 'base64', 'utf-8')

        # 定义附件内容类型
        attachment['Content-Type'] = 'application/octet-stream'
        # 附件名称为 英文 的写法
        # attachment['Content-Disposition'] = 'attachment; filename="list.png"'
        # 附件名称为 中文 的写法
        attachment.add_header('Content-Disposition', 'attachment', filename=('gbk', '', '第四周测试报告.png'))
        msg.attach(attachment)

        try:
            self.smtp.connect(self.mail_host, self.mail_port)
            self.smtp.login(self.sender, self.password)
            self.smtp.sendmail(self.sender, self.recipient, msg.as_string())
        except smtplib.SMTPException as e:
            print(e)
        finally:
            self.smtp.quit()


if __name__ == '__main__':
    # 声明图片和附件内容
    image_content = r'D:\123456\see-master\frontend\src\images\github\list.png'
    attachment_content = r'D:\123456\see-master\frontend\src\images\github\list.png'

    mail = SendMail()
    mail.send(image_content, attachment_content)
