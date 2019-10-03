"""Alumni URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
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
from django.conf.urls import url
from . import DatabaseManager
from . import RequestHandler

info = {
    "openid":"xxxxx",
    "name": "小明",
    "gender": "male | female | other",
    "flag":"invalid",
    "education": [
    {
        "type": "undergraduate | master | doctor",
        "id": 2013010253,
        "start": 2013,
        "end": 2017,
        "departmentId": "00210",
        "department": "清华大学软件学院",
        "class": "软81"
    },
    {
        "type": "master",
        "id": 2017011210,
        "start": 2017,
        "end": 2020,
        "departmentId": "00207",
        "department": "清华大学精仪系",
        "class": "软81"
    }
    ]
    }
#DatabaseManager.AddUser(info["openid"], info["name"], info["gender"], info["flag"], info["education"])
urlpatterns = [
    url(r'^createAcitivity$', RequestHandler.StartActivity),
    url(r'^setUserInfo$', RequestHandler.ChangeUser),
    url(r'^joinActivity$', RequestHandler.JoinActivity),
    url(r'^modifyActivity$', RequestHandler.ChangeActivity),
    url(r'^getAllActivity$', RequestHandler.GetActivityList),
    url(r'^getUserInfo$', RequestHandler.QueryUser),
    url(r'^getActivityInfo$', RequestHandler.QueryActivity),
    url(r'^deleteUser$', RequestHandler.DeleteUser),
    url(r'^deleteActivity$', RequestHandler.DeleteActivity),

]