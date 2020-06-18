from django.shortcuts import render, redirect
from django.urls import reverse
import re
from django_redis import get_redis_connection
from utils.minxi import LoginRequireMixin
from celery_tasks.tasks import send_register_active_email
from .models import User, Address
from apps.goods.models import GoodsSKU
from django.contrib.auth import authenticate, login, logout
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
        # 判断是否记住用户名
        if 'username' not in request.COOKIES:
            username = ''
            checked = ''
        else:
            username = request.COOKIES.get('username')
            checked = 'checked'
        return render(request, 'login.html', {'username': username, 'checked': checked})

    def post(self, request):
        '''处理登录校验'''
        # 接收数据
        username = request.POST.get("username")
        password = request.POST.get("pwd")
        # 数据校验
        if not all([username, password]):
            return render(request, 'login.html', {"error_msg": "数据不完整"})

        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                # 用户激活 记录用户登录状态
                login(request, user)
                # 未登录访问用户中心页面需要进行登录然后进行跳转
                next_url = request.GET.get('next', reverse('goods:index'))
                response = redirect(next_url)  # HttpResponseRedirect
                # 获取就记住用户名状态
                remember = request.POST.get('remember')
                if remember == 'on':
                    response.set_cookie('username', username, max_age=60*60*24*7)
                else:
                    response.delete_cookie('username')
                return response
            else:
                return render(request, 'login.html', {"error_msg": "账号未激活"})
        else:
            return render(request, 'login.html', {"error_msg": "用户名或密码错误"})

        # 业务处理


class LogoutView(View):
    """退出登录"""
    def get(self, request):
        """退出登录"""
        # 清除用户session信息
        logout(request)
        return redirect(reverse('goods:index'))



class UserInfoView(LoginRequireMixin, View):
    """用户中心信息页面"""
    def get(self, request):
        page = 'user'
        # 获取用户个人信息
        user = request.user
        address = Address.objects.get_default_address(user)
        # 获取用户历史浏览
        conn = get_redis_connection('default')

        history_key = f'history_{user.id}'
        sku_ids = conn.lrange(history_key, 0, 4)
        goods_li = []
        for i in sku_ids:
            good = GoodsSKU.objects.get(id=i)
            goods_li.append(good)

        return render(request, 'user_center_info.html', {'page': page, 'address': address, 'goods_li': goods_li})


class UserAddressView(LoginRequireMixin, View):
    """用户中心地址页面"""
    def get(self, request):
        page = 'address'
        user = request.user
        # try:
        #     address = Address.objects.get(user=user, is_default=True)
        # except Address.DoesNotExist:
        #     address = None
        address = Address.objects.get_default_address(user)
        return render(request, 'user_center_site.html', {'page': page, 'address': address})

    def post(self, request):
        # 接受传过来的地址参数
        receiver = request.POST.get('receiver')
        addr = request.POST.get('addr')
        zip_code = request.POST.get('zip_code')
        phone = request.POST.get('phone')
        if not all([receiver, addr, phone]):
            return render(request, 'user_center_site.html', {'error_msg': '数据不完整'})
        if not re.match(r'^1[3|4|5|7|8][0-9]{9}$', phone):
            return render(request, 'user_center_site.html', {'error_msg': '电话格式不正确'})
        # 判断用户是否有默认收货地址
        user = request.user
        # try:
        #     address = Address.objects.get(user=user, is_default=True)
        # except Address.DoesNotExist:
        #     address = None
        address = Address.objects.get_default_address(user)
        if address:
            is_default = False
        else:
            is_default = True
        Address.objects.create(user=user,
                               receiver=receiver,
                               addr=addr,
                               zip_code=zip_code,
                               phone=phone,
                               is_default=is_default)
        return redirect(reverse('user:address'))



class UserOrderView(LoginRequireMixin, View):
    """用户中心订单页面"""
    def get(self, request):
        page = 'order'
        return render(request, 'user_center_order.html', {'page': page})