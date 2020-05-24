import re
from account.models import Command, User, Person, Group
from account.serializer import PersonSerializer
from utils.functions import get_person_information, send_group_message
from api.porn_detection import image_api
from uestc.portal import Portal
import requests


class Statistics(object):
    def __init__(self, user):
        self.user = user

    def zaunPost(self):
        zaunText = requests.get('https://nmsl.shadiao.app/api.php?level={0}&lang=zh_cn'.format(self.user.zaunLevel)).text
        return zaunText

    def get_person(self, command_string, **kwargs):
        string_array = command_string.split(' ')
        try:
            command = self.user.command.get(patternString=string_array[2])
        except Command.DoesNotExist:
            return "指令错误"

        try:
            group = command.group.get(groupId=kwargs['groupId'])
        except Command.DoesNotExist:
            group = Group.objects.create(groupId=kwargs['groupId'], belong=command)
            group.save()

        try:
            person = group.person.get(userId=string_array[1])
        except Person.DoesNotExist:
            person_data = get_person_information(kwargs['groupId'], string_array[1], self.user.cq_url)
            person = Person.objects.create(userId=string_array[1], nickname=person_data['data']['nickname'],
                                           belong=group)

        return person

    def commands(self, command_string, **kwargs):
        string_array = command_string.split(' ')
        if string_array[0] == '/add':
            # user_id:对应的用户信息，而非QQ账号
            if kwargs['user_id'] != self.user.superUserId:
                return "你add你🐎呢"
            if len(string_array) == 6 and not Command.objects.filter(patternString=string_array[1]).exists():
                command = Command.objects.create(patternString=string_array[1], outputCommand=string_array[2],
                                                 maxLength=int(string_array[3]), belong=self.user,
                                                 nickname=string_array[4], openRe=bool(int(string_array[5])))
                command.save()
                return " 添加成功"
            else:
                return "指令格式错误或指令已存在"
        elif string_array[0] == '/set':
            if kwargs['user_id'] != self.user.superUserId:
                return "你set你🐎呢"
            if len(string_array) == 4:
                person = self.get_person(command_string, **kwargs)
                person.count = int(string_array[3])
                person.save()
                return "修改成功"
            else:
                return "指令格式错误"
        elif string_array[0] == '/increase':
            if kwargs['user_id'] != self.user.superUserId:
                return "你increase你🐎呢"
            if len(string_array) == 4:
                person = self.get_person(command_string, **kwargs)
                person.count += int(string_array[3])
                person.save()
                return "添加成功"
            else:
                return "指令格式错误"
        elif string_array[0] == '/switch':
            if kwargs['user_id'] != self.user.superUserId:
                return "你close你🐎呢"
            if len(string_array) == 1:
                self.user.pornSwitch = not self.user.pornSwitch
                self.user.save()
                return "接口状态已调整:" + ('ON' if self.user.pornSwitch else 'OFF')
            else:
                return "指令格式错误"
        elif string_array[0] == '/switchZaun':
            if kwargs['user_id'] != self.user.superUserId:
                return "你close你🐎呢"
            if len(string_array) == 1 and self.user.zaunSwitch:
                self.user.pornSwitch = not self.user.zaunSwitch
                self.user.save()
                return "接口状态已调整:" + ('ON' if self.user.zaunSwitch else 'OFF')
        elif string_array[0] == '/Zaun':
            if len(string_array) == 2:
                if kwargs['user_id'] != self.user.superUserId:
                    return "你设置你🐎呢"
                self.user.zaunUserId = int(string_array[1])
                self.user.zaunGroupNumber = kwargs['group_id']
                self.user.zaunLevel =string_array[2]
                return "设置成功"
            elif len(string_array) == 1:
                return self.zaunPost()
        return None

    def count_add(self, group_id, command, nickname, user_id):
        try:
            group = command.group.get(groupId=group_id)
        except Group.DoesNotExist:
            group = Group.objects.create(belong=command, groupId=group_id)

        try:
            person = group.person.get(userId=user_id)
        except Person.DoesNotExist:
            person = Person.objects.create(userId=user_id, belong=group, nickname=nickname)

        person.nickname = nickname
        person.count = person.count + 1
        group.save()
        person.save()
        return False

    def rank_get(self, message, group_id):
        commands = self.user.command.all()
        for command in commands:
            if message == command.outputCommand:
                try:
                    group = command.group.get(groupId=group_id)
                except Group.DoesNotExist:
                    group = Group.objects.create(belong=command, groupId=group_id)

                persons = group.person.filter(inGroup=True)
                persons.order_by('count')
                length = min(len(persons), command.maxLength)
                res_data = PersonSerializer(persons[:length], many=True)
                return res_data.data, command.nickname
        return None, None

    @staticmethod
    def group_rank_message(rank_dic, group_id, nickname, cq_url):
        length = len(rank_dic)
        msg = "你群前" + str(length) + "名" + nickname + "："
        for item in rank_dic:
            msg += "\n" + str(item['nickname']) + " " + str(item['count'])
        send_group_message(msg, group_id, cq_url)

    def handle_message(self, data):
        message = data['message']
        user_id = data['user_id']
        group_id = data['group_id']
        command_res = self.commands(message, user_id=user_id, groupId=group_id)
        get_person_information(group_id, message, self.user.cqUrl)
        if command_res:
            send_group_message(command_res, group_id, self.user.cqUrl)
        else:
            rank_dic, nickname = self.rank_get(message, int(group_id))
            if rank_dic:
                self.group_rank_message(rank_dic, group_id, nickname, self.user.cqUrl)
            else:
                self.command_count(message, group_id, user_id, data['sender']['nickname'])
                ret = re.search("CQ:image", message)
                if self.user.pornSwitch and ret and image_api.detection(message):
                    send_group_message("gkdgkd!!!!", group_id, self.user.cqUrl)
        if user_id == self.user.zaunUserId and group_id == self.user.zaunGroupNumber:
                send_group_message(self.zaunPost(), group_id, self.user.cqUrl)

    def set_person_status(self, person, status):
        person.in_group = status
        person.save()

    def handle_group(self, data):
        notice_type = data['notice_type']
        user_id = data['user_id']
        group_id = data['group_id']
        groups = Group.objects.filter(groupId=group_id)
        status = notice_type == 'group_increase'
        for group in groups:
            person = group.person.get(userId=user_id)
            self.set_person_status(person, status)

    def command_count(self, message, group_id, user_id, nickname):
        commands = self.user.command.all()
        for command in commands:
            if command.openRe and re.findall(command.patternString, message):
                if self.count_add(group_id, command, nickname, user_id):
                    return True
            elif (not command.openRe) and message == command.patternString:
                if self.count_add(group_id, command, nickname, user_id):
                    return True
        return False

    def handle_private(self, data, user):
        if data['user_id'] == user.superUserId:
            portal = Portal(user)
            portal.command_analyse(data['message'])
