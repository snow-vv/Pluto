import requests
import json
import click
from pprint import pprint
import pypinyin

"""
curl -X POST "http://jump.wanmeizhensuo.com/api/users/v1/users/" -H "accept: application/json" -H "Content-Type: application/json" -H "X-CSRFToken: zkv54Yb7ZPCCOvs35w5WJc9qroK2wbXHpoypmvkjjMYVFXr042jVMSYq4BxwaQp0" -d "{ \"name\": \"鹏鸿测试\", \"username\": \"wph-test\", \"email\": \"ops@igengmei.com\", \"groups\": [ \"b188ba2b-c932-4179-817e-a172ef97a79b\" ], \"role\": \"User\", \"wechat\": \"18222390280\", \"phone\": \"18222390280\", \"otp_level\": 0, \"comment\": \"\", \"source\": \"local\", \"is_active\": true, \"created_by\": \"wph\", \"is_first_login\": true}"
"""

git_domain = 'http://jump.wanmeizhensuo.com'


def pinyin(word):
    s = ''
    for i in pypinyin.pinyin(word, style=pypinyin.NORMAL):
        s += ''.join(i)
    return s


def get_token():
    url = git_domain + '/api/users/v1/auth/'

    query_args = {
        "username": "jump-admin",
        "password": "Gengmei123123!",
    }

    response = requests.post(url, data=query_args)

    return json.loads(response.text)['token']


def get_user_info():
    url = git_domain + '/api/users/v1/users/'
    token = get_token()
    header_info = {"Authorization": 'Bearer ' + token}
    response = requests.get(url, headers=header_info)
    # pprint(json.loads(response.text))
    print(response.text)


# @click.command()
# @click.option('--name', prompt="用户姓名")
# @click.option('--username', prompt="Username")
def init_user_info():
    name = input('请输入用户中文姓名: ')
    username = pinyin(name)
    new_user_dic = {
        "name": name,
        "username": username,
        "email": username + '@igengmei.com',
        "role": "User",
        # "wechat": "18222390280",
        # "phone": "18222390280",
        "otp_level": 0,
        # "source": "local"
    }
    # print("-" * 50)
    return new_user_dic


def get_group_info():
    url = git_domain + '/api/users/v1/groups/'
    token = get_token()
    header_info = {"Authorization": 'Bearer ' + token, 'accept': 'application/json'}
    response = requests.get(url, headers=header_info)
    # pprint(json.loads(response.text))
    # print(response)

    groups_list = json.loads(response.text)
    new_groups = []
    for item in groups_list:
        data = {
            "id": item.get("id", ""),
            "name": item.get("name", ""),
            # "comment": item.get("comment", ""),
        }
        new_groups.append(data)

    return new_groups


def choice_group_id():
    group_dic = {}
    choice_dic = {}
    group_list = get_group_info()
    n = 1
    for item in group_list:
        group_dic[n] = item
        n += 1
    # print(group_dic)
    for group_id, group_info in group_dic.items():
        choice_dic[group_id] = group_info.get('name')
    for group_id, group_info in choice_dic.items():
        print(group_id, group_info)
    return group_dic


@click.command()
@click.option('--gid', prompt='请按序号选择用户组 ', help='The person to greet.')
def create_user(gid):
    url = git_domain + '/api/users/v1/users/'
    group_id_list = []
    group_id = group_dic[int(gid)]['id']
    group_id_list.append(group_id)
    new_user_dic['groups'] = group_id_list
    token = get_token()
    header_info = {"Authorization": 'Bearer ' + token, 'accept': 'application/json',
                   'Content-Type': 'application/json'}
    response = requests.post(url, headers=header_info, json=new_user_dic)
    if response.status_code == 201:
        print('======================>  用户创建成功! ')
    else:
        print(response.text)


if __name__ == '__main__':
    print('*' * 40)
    print('***   请按提示输入，创建jumpserver用户  ***')
    print('*' * 40)
    new_user_dic = init_user_info()
    group_dic = choice_group_id()
    create_user()
