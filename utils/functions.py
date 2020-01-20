import os
import requests
import json
import re


def get_env(name, default=""):
    return os.environ.get(name, default)


def post_image(imgB64code, user_id, url):
    data_dic = {
        'user_id': user_id,
        'message': '[CQ:image, file=base64://' + imgB64code + ']',
    }
    requests.post(url=url + '/send_private_msg', data=data_dic)


def post_private_msg(msg, user):
    data_dic = {
        'user_id': user.superUserId,
        'message': msg,
    }
    requests.post(url=user.cqUrl + '/send_private_msg', data=data_dic)


def verify_login_status(cookies_str):
    cookies = json.loads(cookies_str)
    cookies_dict = {}
    for cookie in cookies:
        cookies_dict[cookie['name']] = cookie['value']
    r = requests.get(url='http://eams.uestc.edu.cn/eams/', cookies=cookies_dict)
    return r.status_code == 200


def get_all_grades(cookies_str):
    cookies = json.loads(cookies_str)
    cookies_dict = {}
    for cookie in cookies:
        cookies_dict[cookie['name']] = cookie['value']
    r = requests.get(url='http://eams.uestc.edu.cn/eams/teach/grade/course/person!historyCourseGrade.action?projectType=MAJOR', cookies=cookies_dict)
    new_cookies = r.cookies
    return re.findall(r"(?<=<tr>)([\d\D]*?)(?=</tr>)", r.text)
