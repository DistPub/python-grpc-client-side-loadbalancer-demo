import subprocess
from argparse import ArgumentParser


def get_current_host_ip():
    """获取本机局域网ip"""
    ip_list = subprocess.check_output(['hostname', '-I']).decode('utf-8').split()
    return ip_list[0]


def get_arguments_parser():
    parser = ArgumentParser()
    parser.add_argument('--etcd_host', type=str, required=True)
    parser.add_argument('--etcd_port', type=int, required=True)
    parser.add_argument('--etcd_username', type=str, required=True)
    parser.add_argument('--etcd_password', type=str, required=True)
    parser.add_argument('--etcd_app_path', type=str, required=True)
    return parser
