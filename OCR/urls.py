"""OCR URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from django.urls import path, include
from ocr_app import views
from django.contrib.auth import views as auth_views
from django.conf.urls.static import static
from django.conf import settings


urlpatterns = [
    url('admin/', admin.site.urls),
    path('', views.Index.as_view(), name='index'),
    path('home', views.Home.as_view(), name='home'),
    path('ocr/', include('ocr_app.urls')),
    path('accounts/', include('django.contrib.auth.urls')),

    # path('reset/', include('django.contrib.auth.urls'))
    # url('reset/', include('django.contrib.auth.urls')),
    # path('accounts/ password_change/', auth_views.PasswordResetForm, name='password_reset')
    # url(r'^accounts/password_reset/$', auth_views.PasswordResetView, name='password_reset'),
    # url(r'^accounts/password_reset/done/$', auth_views.PasswordChangeDoneView, name='password_reset_done'),
    # url(r'^accounts/reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
    #     auth_views.PasswordResetConfirmView, name='password_reset_confirm'),
    # url(r'^accounts/reset/done/$', auth_views.PasswordResetCompleteView, name='password_reset_complete'),

]

