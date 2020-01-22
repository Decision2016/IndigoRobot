from selenium import webdriver
import re
import time, datetime
import json
import requests
from utils.functions import post_image, post_private_msg, get_all_grades, verify_login_status
from .models import UestcStu, Course
from selenium.webdriver.firefox.options import Options


class Portal(object):
    def __init__(self, user):
        self.user = user

    def login(self):
        # 抓取QQ登录二维码发送到管理员QQ进行登录
        firefox_option = Options()
        firefox_option.add_argument('--headless')
        driver = webdriver.Firefox(firefox_options=firefox_option)
        driver.get("http://portal.uestc.edu.cn/")
        driver.find_element_by_xpath('/html/body/div[1]/div[2]/div[2]/div/div[3]/div/form/div/div/div[1]/a').click()
        time.sleep(1)
        iframe = driver.find_element_by_xpath('//*[@id="ptlogin_iframe"]')
        code = iframe.screenshot_as_base64
        post_image(code, user_id=self.user.superUserId, url=self.user.cqUrl)
        try:
            stuInfo = self.user.stuInfo
        except UestcStu.DoesNotExist:
            stuInfo = UestcStu.objects.create()
        for i in range(0, 120):
            time.sleep(1)
            if driver.current_url == 'http://portal.uestc.edu.cn/':
                driver.get('http://eams.uestc.edu.cn/eams/')
                time.sleep(2)
                cookies = driver.get_cookies()
                cookies_json = json.dumps(cookies)
                cookies_str = str(cookies_json)
                stuInfo.stuCookies = cookies_str
                stuInfo.loginStatus = True
                stuInfo.loginHint = False
                stuInfo.belong = self.user
                stuInfo.save()
                break
            else:
                time.sleep(1)
        driver.close()

    def command_analyse(self, command_string):
        command_array = command_string.split(' ')
        if command_array[0] == '/login':
            self.login()
            post_private_msg(msg='教务处系统登录成功', user=self.user)
        elif command_array[0] == '/courseinit':
            # todo:此处存在bug需要进行修改
            try:
                stuInfo = self.user.stuInfo
            except UestcStu.DoesNotExist:
                post_private_msg(msg='用户未登录', user=self.user)
            course_list = get_all_grades(stuInfo.stuCookies)
            if len(course_list) == 0 and not stuInfo.loginHint:
                post_private_msg(msg="登录失效", user=self.user)
                stuInfo.loginHint = True
            stuInfo.save()
            for i in range(2, len(course_list)):
                course_detail = re.findall(r"(?<=<td>).*?(?=</td>)", course_list[i])
                grade = re.findall(r'(?<=<td style="">)([\d\D]*?)(?=</td>)', course_list[i])[1]
                grade = str(grade)
                grade.replace(" ", "")
                try:
                    self.user.course.get(courseId=course_detail[1])
                except Course.DoesNotExist:
                    course = Course.objects.create()
                    course.courseName = course_detail[3]
                    course.courseId = course_detail[1]
                    course.coursePoint = course_detail[5]
                    course.courseGrade = grade
                    course.belong = self.user
                    course.save()
            post_private_msg(msg='成绩初始化成功', user=self.user)
        elif command_array[0] == '/switch':
            self.switch()
        elif command_array[0] == '/test':
            self.test()
        elif command_array[0] == '/login_status':
            try:
                stuInfo = self.user.stuInfo
                login_status = verify_login_status(stuInfo.stuCookies)
            except UestcStu.DoesNotExist:
                login_status = False
            post_private_msg(msg='教务处登录状态:{0}'.format('True' if login_status else 'False'), user=self.user)


    def task(self):
        query_flag = False
        try:
            stuInfo = self.user.stuInfo
        except UestcStu.DoesNotExist:
            post_private_msg(msg='请先登录', user=self.user)
            return
        stuInfo.lastQueryTime = datetime.datetime.now()
        course_list = get_all_grades(stuInfo.stuCookies)
        if len(course_list) == 0 and not stuInfo.loginHint:
            post_private_msg(msg="登录失效", user=self.user)
            stuInfo.loginHint = True
        stuInfo.save()
        for i in range(2, len(course_list)):
            course_detail = re.findall(r"(?<=<td>).*?(?=</td>)", course_list[i])
            grade = re.findall(r'(?<=<td style="">)([\d\D]*?)(?=</td>)', course_list[i])[1]
            grade = str(grade)
            grade = grade.replace(" ", "")
            try:
                self.user.course.get(courseId=course_detail[1])
            except Course.DoesNotExist:
                course = Course.objects.create()
                course.courseName = course_detail[3]
                course.courseId = course_detail[1]
                course.coursePoint = course_detail[5]
                course.belong = self.user
                course.courseGrade = grade
                msg = "公布了新的课程{0}成绩：{1}".format(course.courseName, course.courseGrade)
                post_private_msg(msg=msg, user=self.user)
                query_flag |= True
                course.save()

    def switch(self):
        stuInfo = self.user.stuInfo
        stuInfo.gradeSpySwitch = not stuInfo.gradeSpySwitch
        stuInfo.save()
        post_private_msg('成绩检测接口已调整：{0}'.format('ON' if stuInfo.gradeSpySwitch else 'OFF'), self.user)

    def test(self):
        try:
            stuInfo = self.user.stuInfo
        except UestcStu.DoesNotExist:
            post_private_msg(msg='用户未登录', user=self.user)
        course_list = get_all_grades(stuInfo.stuCookies)
        if len(course_list) == 0 and not stuInfo.loginHint:
            post_private_msg(msg="登录失效", user=self.user)
            stuInfo.loginHint = True
        stuInfo.save()
        post_private_msg(len(course_list), self.user)