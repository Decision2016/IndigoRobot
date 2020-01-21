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
    r = requests.get(url='http://eams.uestc.edu.cn/eams/home!submenus.action?menu.id=', cookies=cookies_dict)
    return not (len(re.findall(r'我的信息', r.text)) == 0)


def get_all_grades(cookies_str):
    cookies = json.loads(cookies_str)
    cookies_dict = {}
    for cookie in cookies:
        cookies_dict[cookie['name']] = cookie['value']
    r = requests.get(url='http://eams.uestc.edu.cn/eams/teach/grade/course/person!historyCourseGrade.action?projectType=MAJOR', cookies=cookies_dict)
    new_cookies = r.cookies
    return re.findall(r"(?<=<tr>)([\d\D]*?)(?=</tr>)", r.text)


def get_person_information(group_id, user_id, cq_url):
    url = cq_url + '/get_group_member_info'
    data = {
        'group_id': group_id,
        'user_id': user_id,
        'no_cache': 'true'
    }
    request = requests.post(url, data)
    return json.loads(request.text)


def send_group_message(message, group_id, cq_url):
    url = cq_url + "/send_group_msg"
    data_dic = {
         'group_id': group_id,
         'message': message,
    }
    request = requests.post(url=url, data=data_dic)
