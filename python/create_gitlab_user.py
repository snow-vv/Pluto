#-*- coding: utf-8 -*-
import gitlab
import click

gl = gitlab.Gitlab('http://git.wanmeizhensuo.com/', private_token = 'dKsN_XuDn6riUMJJP3yR')

# @click.command()
# @click.option('--username', prompt='Your username: ', help='用于登录git的账号')
# @click.option('--name', prompt='Your Name: ', help='用于git上的账户显示名称 ')
# @click.option('--password', prompt='Your password: ', help='登录git的密码')
# @click.option('--email', prompt='Your Email: ', help='绑定的邮箱地址')
# @click.option('--group', prompt='Your Group: ', help='所属的组')
def create_user():
    #gl = gitlab.Gitlab('http://git.wanmeizhensuo.com/', private_token = 'dKsN_XuDn6riUMJJP3yR')
    username = input("Your username: ")
    name = input("Your name: ")
    password = input("Your password: ")
    email = input("Your email: ")
    group = input("Your group: ")
    data = {
        'username': username,
        'password': password,
        'email': email,
        'name': name
    }
    user_info = gl.users.create(data)
    return {"group": group, "user_id": user_info.id}

def get_group_info():
    group_dict = {}
    groups = gl.groups.list()
    for group in groups:
        group_dict[group.id] = group.name
    return group_dict

def update_group_member():
    return_dict = create_user()
    group_info = get_group_info()
    for key, value in group_info.items():
        if return_dict['group'] == value:
            group = gl.groups.get(key)

    group.members.create({'user_id': return_dict['user_id'], 'access_level': gitlab.DEVELOPER_ACCESS})


if __name__ == '__main__':
    update_group_member()