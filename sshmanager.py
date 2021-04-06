"""核心代码"""
import json

import paramiko
import threading
import os
import datetime


class REMOTE_HOST(object):
    #远程操作主机
    def __init__(self, node_name, host, port, username, password, cmd):
        self.node_name = node_name
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.cmd = cmd

    def run(self):
        """起线程连接远程主机后调用"""
        try:
            cmd_str = self.cmd.split()[0]
            if hasattr(self, cmd_str):      #反射 eg:调用put方法
                getattr(self, cmd_str)()
            else:
                #setattr(x,'y',v)is  equivalent  to   ``x.y=v''
                setattr(self, cmd_str, self.command)
                getattr(self, cmd_str)()  #调用command方法，执行批量命令处理
        except Exception as ex:
            print(self.host + ':' + str(ex))

    def command(self):
        """批量命令处理"""
        try:
            ssh = paramiko.SSHClient()  #创建ssh对象
            #允许连接不在know_hosts文件中的主机
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(hostname=self.host,port=self.port,username=self.username,password=self.password)
            stdin,stdout,stderr = ssh.exec_command(self.cmd)
            result = stdout.read()
            print(self.host + ' ' + result.decode('gbk') + '\r\n')
            ssh.close()
        except Exception as ex:
            print(self.host + ':' + str(ex) + '\r\n')

    def put(self):
        """上传文件"""
        try:
            filename = self.cmd.split()[1]  # 要上传的文件
            remote_path = self.cmd.split()[2]
            transport = paramiko.Transport((self.host, self.port))
            transport.connect(username=self.username, password=self.password)
            sftp = paramiko.SFTPClient.from_transport(transport)
            sftp.put(filename, remote_path)
            print(self.host + ':' + "put success")

            transport.close()
        except Exception as ex:
            print(self.host + ':' + str(ex))

    def get_config(self):
        """获取config.json"""
        try:
            file_path = 'D:\\AirportRfid\\config.json'
            save_path = self.cmd.split()[1]
            transport = paramiko.Transport((self.host, self.port))
            transport.connect(username=self.username, password=self.password)
            sftp = paramiko.SFTPClient.from_transport(transport)
            sftp.get(file_path, os.path.join(save_path, self.node_name + '.json'))
            print(self.host + ':' + "get config success")
            transport.close()
        except Exception as e:
            print(self.host + ':' + str(e))

    def send_config(self):
        """发送config.json"""
        try:
            path = self.cmd.split()[1]
            remote_path = 'D:\\AirportRfid\\config.json'
            transport = paramiko.Transport((self.host, self.port))
            transport.connect(username=self.username, password=self.password)
            sftp = paramiko.SFTPClient.from_transport(transport)
            files = os.listdir(path)
            for filename in files:
                if filename == self.node_name + '.json':
                    sftp.put(os.path.join(path, filename), remote_path)
                    print(self.host + ':' + "send config success")
                    break
            transport.close()

        except Exception as e:
            print(self.host + ':' + str(e))

    def send_files(self):
        """ send_files local_dir remote_dir"""
        try:
            local_dir = self.cmd.split()[1]
            remote_dir = self.cmd.split()[2]
            transport = paramiko.Transport((self.host, self.port))
            transport.connect(username=self.username, password=self.password)
            sftp = paramiko.SFTPClient.from_transport(transport)
            files = os.listdir(local_dir)
            for filename in files:
                sftp.put(os.path.join(local_dir, filename), os.path.join(remote_dir, filename))
                print(self.host + ':' + "send " + filename)
            transport.close()

        except Exception as e:
            print(self.host + ':' + str(e))

    def get_files(self):
        """ get_files remote_dir local_dir """
        try:
            local_dir = self.cmd.split()[2]
            remote_dir = self.cmd.split()[1]
            transport = paramiko.Transport((self.host, self.port))
            transport.connect(username=self.username, password=self.password)
            sftp = paramiko.SFTPClient.from_transport(transport)
            files = os.listdir(remote_dir)
            for filename in files:
                sftp.get(os.path.join(remote_dir, filename), os.path.join(local_dir, filename))
                print(self.host + ':' + "get " + filename)
            transport.close()

        except Exception as e:
            print(self.host + ':' + str(e))


def show_host_list():
    # read param
    with open('target.json') as json_file:
        target = json.load(json_file)

    """通过选择分组显示主机名与IP"""
    for index, key in enumerate(target):
        print(f'[{index}] {key}{len(target[key])}')
    while True:
        choose_index = int(input(">>>(index)").strip())
        host_dic = []
        for index, key in enumerate(target):
            if choose_index == index:
                host_dic = target[key]
                break
        if host_dic:
            for key in host_dic:
                print(key, host_dic[key]["IP"])
            return host_dic
        else:
            print("NO exit this group!")


def show_cmd_list():
    # read param
    with open('cmd.json') as json_file:
        cfg = json.load(json_file)
    """显示预设命令"""
    print('*-'*10 + ' preset cmd ' + '-*'*10)
    for index, key in enumerate(cfg):
        print('[' + key + ']', cfg[key])
    while True:
        cmd = input(">>>(eg:1)").strip()
        try:
            host_dic = cfg[cmd]
            if host_dic:
                print('cmd: ' + host_dic)
                return host_dic
            else:
                print('cmd: ' + cmd)
                return cmd
        except Exception as e:
            return cmd


def interactive(choose_host_list):
    """根据选择的分组主机起多个线程进行批量交互"""
    thread_list = []
    while True:
        # cmd = input(">>>").strip()
        cmd = show_cmd_list()
        if cmd == 'quit':
            break
        elif cmd:
            for key in choose_host_list:
                host, port, username, password = choose_host_list[key]["IP"], choose_host_list[key]["port"], \
                                                 choose_host_list[key]["username"], choose_host_list[key]["password"]
                func = REMOTE_HOST(key, host, port, username, password, cmd)  # 实例化类
                t = threading.Thread(target=func.run)  # 起线程
                t.start()
                thread_list.append(t)
            for t in thread_list:
                t.join()  # 主线程等待子线程执行完毕
            print('done')
        else:
            continue


def run():
    print('ssh manager version:1.0.1')
    choose_host_list = show_host_list()
    interactive(choose_host_list)


if __name__ == "__main__":
    run()

