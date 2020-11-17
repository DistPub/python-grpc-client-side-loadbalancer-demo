#!/usr/bin/env python3
import signal
import threading
from concurrent import futures
from multiprocessing import cpu_count

import grpc

from common.etcd_client import Etcd3ClientProxy
from common.micro_service_manage_center import MicroServiceManageCenter
from common.utils import get_current_host_ip, get_arguments_parser
from protos import service_pb2_grpc
from services.service import Greeter


def get_server(port):
    server = grpc.server(futures.ThreadPoolExecutor(cpu_count()), options=(('gprc.so_reuseport', 0),))
    service_pb2_grpc.add_GreeterServicer_to_server(Greeter(), server)
    server.add_insecure_port(f'0.0.0.0:{port}')
    return server


def main(port, etcd_host, etcd_port, etcd_username, etcd_password, etcd_app_path):
    service_name = f'{etcd_app_path}Greeter'

    server = get_server(port)
    server.start()
    print(f'start service: {service_name} on port: {port}')

    client = Etcd3ClientProxy(host=etcd_host, port=etcd_port, user=etcd_username, password=etcd_password)
    ip = get_current_host_ip()
    control = MicroServiceManageCenter(ip, port, client, lock_prefix=f'{etcd_app_path}locks/')
    control.register_service(service_name)

    event = threading.Event()

    def signal_handler(*args):  # coverage:ignore= # pylint:disable=unused-argument
        control.cancel_service(service_name)
        event.set()

    signal.signal(signal.SIGTERM, signal_handler)

    try:
        event.wait()
    except KeyboardInterrupt:
        control.cancel_service(service_name)

    server.stop(10 * 60).wait()


if __name__ == '__main__':  # coverage:ignore=
    parser = get_arguments_parser()
    parser.add_argument('--port', type=int, required=True)
    options = parser.parse_args()
    main(options.port,
         options.etcd_host, options.etcd_port, options.etcd_username, options.etcd_password, options.etcd_app_path)
