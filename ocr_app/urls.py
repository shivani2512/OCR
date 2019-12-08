from django.urls import path
from django.views.static import serve

from . import views
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls import url


app_name = 'ocr_app'

urlpatterns = [
    path('register/', views.registration, name='register'),
    path('login/', views.login_user, name='login'),
    # Changed for trying purpose path('login/', views.login, name='login'),
    path('upload/<int:pk>', views.UploadImage, name='upload'),
    # path('config/<int:pk>', views.FileConfigurationForm, name='fileConfig'),
    path('process/<int:pk>', views.ImageProcess, name='process'),
    path('logout', views.logout_user, name='logout'),
    path('list/', views.listFiles, name='list'),
    path('history/<int:pk>', views.history, name='logs'),
    path('file/<str:fileName>/', views.fileDownload, name="fileDownload"),
    path('allfile/', views.allFiles, name='allFile'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

