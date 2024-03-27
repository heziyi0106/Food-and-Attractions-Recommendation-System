"""
URL configuration for groupSite project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.urls import re_path as url
from RecommenderSystem import views

urlpatterns = [
    # path("", views.shopsList),
    path('index/', views.index, name='index'),
    path("", views.recommender, name="recommender"),
    # path("recommender/", views.recommender, name="recommender"),
    path('import-csv/', views.import_csv),
    # path('/shopdetail/', views.shopDetail, name='/shopdetail'),
    url(r"^shopdetail/(\d+)", views.shopDetail),  # 位置對應
    # path('getKeyWords12/',views.getKeyWords12),
    # path('getKeyWords3/',views.getKeyWords3),
    # path('getKeyWords4/',views.getKeyWords4),
    # path('getKeyWords5/',views.getKeyWords5),






]
