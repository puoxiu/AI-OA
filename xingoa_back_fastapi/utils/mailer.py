# app/utils/mailer.py
from smtplib import SMTP, SMTP_SSL
from email.mime.text import MIMEText
from app.core.config import settings



def send_email(subject: str, recipient_list: list[str], message: str):
    """
    发送邮件（自动适配 SSL / TLS 模式）
    :param subject: 邮件主题
    :param recipient_list: 收件人列表
    :param message: 邮件正文
    """
    msg = MIMEText(message, _charset="utf-8")
    msg["Subject"] = subject
    msg["From"] = settings.EMAIL_FROM
    msg["To"] = ", ".join(recipient_list)

    try:
        if settings.SMTP_PORT == 465:
            from smtplib import SMTP_SSL
            with SMTP_SSL(settings.SMTP_HOST, settings.SMTP_PORT) as smtp:
                smtp.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
                smtp.sendmail(settings.EMAIL_FROM, recipient_list, msg.as_string())
        else:
            with SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as smtp:
                smtp.ehlo()
                smtp.starttls()
                smtp.ehlo()
                smtp.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
                smtp.sendmail(settings.EMAIL_FROM, recipient_list, msg.as_string())
    except Exception as e:
        # 报警级别：warning 或 info，而非 error
        print(f"[警告] 邮件发送成功但返回异常：{e}")