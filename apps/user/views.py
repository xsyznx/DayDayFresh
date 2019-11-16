from django.shortcuts import render, redirect
from django.urls import reverse
import re
from celery_tasks.tasks import send_register_active_email
from .models import User
from django.contrib.auth import authenticate,login
from django.views import View
from django.conf import settings
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from django.http.response import HttpResponse
# Create your views here.

# /user/register
class RegisterView(View):

    def get(self, request):
        '''显示注册页面'''
        return render(request, 'register.html')

    def post(self, request):
        '''进行注册处理'''
        username = request.POST.get('username')
        password = request.POST.get('pwd')
        confirm_pwd = request.POST.get('cpwd')
        email = request.POST.get('email')
        allow = request.POST.get('allow')

        # 数据校验
        if not all([username, password, confirm_pwd, email]):
            return render(request, 'register.html', {"error_msg": "数据不完整"})

        # 校验邮箱
        if not re.match(r'^[a-z0-9][\w.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
            return render(request, 'register.html', {"error_msg": "邮箱不正确"})

        # 确认密码一致
        if password != confirm_pwd:
            return render(request, 'register.html', {"error_msg": "两次密码输入不一致"})

        # 同意协议
        if allow != 'on':
            return render(request, 'register.html', {"error_msg": "请同意协议"})

        # 校验用户名
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            # 抛出异常代表数据库中用户名不存在
            user = None
        if user:
            return render(request, 'register.html', {"error_msg": "用户名已存在"})

        user = User.objects.create_user(username, email, password)
        user.is_active = 0
        user.save()

        # 向用户发送邮件,激活链接为http://127.0.0.1:8000/user/active/user_id

        # 加密连接
        serializer = Serializer(settings.SECRET_KEY, 3600)
        info = {"confirm": user.id}
        token = serializer.dumps(info)
        token = token.decode()

        # 发送邮件
        send_register_active_email.delay(email, username, token)

        return redirect(reverse('user:login'))

# /user/active
class ActiveView(View):
    '''用户激活类'''
    def get(self, request, token):
        serializer = Serializer(settings.SECRET_KEY, 3600)
        try:
            token = token.encode()
            info = serializer.loads(token)
            user_id = info["confirm"]
            user = User.objects.get(id=user_id)
            user.is_active = 1
            user.save()
            return redirect(reverse('user:login'))
        except SignatureExpired as e:
            return HttpResponse("激活链接过期")


# /user/login
class LoginView(View):
    '''登陆页面'''
    def get(self, request):
        return render(request, 'login.html')

    def post(self, request):
        '''处理登录校验'''
        # 接收数据
        username = request.POST.get("username")
        password = request.POST.get("pwd")
        # 数据校验
        if not all([username, password]):
            return render(request, 'login.html', {"error_msg": "数据不完整"})

        user = authenticate(username=username, password=password)
        if user is None:
            return render(request, 'login.html', {"error_msg": "用户名或密码错误"})

        if user.is_active:
            login(request, user)
            return redirect(reverse('goods:index'))

        return render(request, 'login.html', {"error_msg": "用户未激活"})

        # 业务处理