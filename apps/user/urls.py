from django.urls import path
from . import views
from django.conf.urls import url

app_name = 'user'

urlpatterns = [
    path('register/', views.RegisterView.as_view(), name='register'),
    path('active/<token>', views.ActiveView.as_view(), name='active'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('address/', views.UserAddressView.as_view(), name='address'),
    path('order/', views.UserOrderView.as_view(), name='order'),
    url(r'^$', views.UserInfoView.as_view(), name='user'),
]
