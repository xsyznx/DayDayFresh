from celery import Celery
from django.conf import settings
from django.core.mail import send_mail

# 任务处理者一端加django环境初始化
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DayDayFresh.settings')
django.setup()

# 创建Celery实例对象
app = Celery('celery_tasks.tasks', broker='redis://127.0.0.1:6379/2')

# 定义任务函数
@app.task
def send_register_active_email(to_email, username, token):
    '''发送激活邮件'''
    subject = "天天生鲜激活邮件"
    message = ''
    from_email = settings.EMAIL_FROM
    recipient_list = [to_email]
    html_message = "<h1>{}欢迎你成为天天生鲜会员</h1>请点击下面链接进行激活<a href='http://127.0.0.1:8000/user/active/{}'>http://127.0.0.1:8000/user/active/{}</a>".format(
        username, token, token)

    send_mail(subject, message, from_email, recipient_list, html_message=html_message)