# -*- coding: utf-8 -*-
import psutil
import requests
import socket
import os

class DingDing(object):
    def send_message_to_dingding(self, content):
        url = 'https://oapi.dingtalk.com/robot/send?access_token=91e0ad0296e26bbfd59b7468003fc597b3d7574cff7e135bb2d83c46c4a4ee01'
        data = {
            "msgtype": "text",
            "text": {
                "content": content
            },
            "at": {
                "atMobiles": ["15313890959"],
                "isAtAll": False
            }
        }

        requests.post(url, json=data)

class Process(object):
    file = '/data/process.txt'

    ##初始化服务器进程列表
    def init_process(self):
        f = open(self.file, 'w')
        cmd_list = []
        pids = psutil.pids()
        for pid in pids:
            p = psutil.Process(pid)
            if len(p.cmdline()):
                cmd = str(p.cmdline()).strip('\n')
                if cmd not in cmd_list:
                    cmd_list.append(cmd)
                    f.writelines(cmd + '\n')
                else:
                    pass
            else:
                pass
        f.close()

    ##读取进程文件判断进程应该属于此服务器
    def read_process(self):
        process_all = []
        f = open(self.file, 'r')
        for line in f.readlines():
            line = line.strip('\n')
            process_all.append(line)
        f.close()
        return process_all

    # 收集服务器进程
    def collect_process(self):
        process_info = {}
        pids = psutil.pids()
        for pid in pids:
            p = psutil.Process(pid)
            if str(p.cmdline()) not in process_info.values():
                process_info[pid] = str(p.cmdline())
            else:
                pass

        return process_info

    # def collect_process(self):
    #     process_info = {}
    #     pids = psutil.pids()
    #     for pid in pids:
    #         p = psutil.Process(pid)
    #         if str(p.cmdline()) not in process_info.values():
    #             process_info[p.name()] = str(p.cmdline())
    #         else:
    #             pass
    #     return process_info

    # 判断进程状态
    def judge_process_is_running(self):
        processes = self.collect_process()
        hostname = socket.gethostname()
        process_list = ['supervisord', 'filebeat', 'nginx', 'prometheus', 'node_exporter', 'process-exporter', 'kafka_exporter', 'elasticsearch_exporter']
        process_info = self.read_process()
        alert_list = []

        for service in process_list:
            for cmd in process_info:
                if service in cmd:
                    if service not in str(processes.values()):
                        alert_list.append(service)
                    else:
                        pass
                else:
                    pass

        if len(alert_list):
            content = '{}: {}进程已经挂掉，请及时确认'.format(hostname, alert_list)
            DingDing().send_message_to_dingding(content=content)
        else:
            pass


if __name__ == '__main__':
    file = Process().file
    if  not os.path.exists(file) or os.path.getsize(file) == 0:
        Process().init_process()

    else:
        pass

    Process().judge_process_is_running()