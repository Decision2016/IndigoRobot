# IndigoRobot

[![Python](https://img.shields.io/badge/python-3.6.2-blue.svg?style=flat-square)](https://www.python.org/downloads/release/python-362/)
[![Django](https://img.shields.io/badge/django-3.0.1-blue.svg?style=flat-square)](https://www.djangoproject.com/)
[![Django Rest Framework](https://img.shields.io/badge/django_rest_framework-3.11.0-blue.svg?style=flat-square)](http://www.django-rest-framework.org/)

# 说明
* 一个用来自己玩的机器人api网站
* API接口基于django的restframwork
* 代码还需要继续重构（咕咕咕）

# 目前功能

## 生草计数器

一开始只是为了记录“草”的出现次数

目前在QQ群内接收消息并可以添加任意形式的字符串进行检测

## UESTC教务处成绩检测

通过selenium进行登录，抓取二维码并发送到管理员QQ进行登录

在检测开关打开的时候可以每隔一段时间进行成绩的检测，如果出新成绩则发送到管理员QQ

## 日志记录

待开发

## MC服务器信息获取

在QQ群中发送"/mc"，获取服务器信息

可以在网页前端可修改服务器地址和端口
